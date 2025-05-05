import json
import random
import re
import json_repair
import librosa
import requests
import torch
import whisperx
import os
import asyncio
import uuid
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware import Middleware
from get_file import get_file
from loguru import logger
from pydub import AudioSegment

torch.cuda.init()
load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')
T1_API_URL = os.getenv('T1_API_URL')
MAX_CONCURRENT = os.getenv('MAX_CONCURRENT')

app = FastAPI()

"""
Сервис для транскрибации и диаризации аудиозаписей

send_to_t1 - функция, которая отправляет запрос в LLM t1-pro: 
https://huggingface.co/t-tech/T-pro-it-1.0, запущенной через vllm
"""


class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.queue = asyncio.Queue()
        self.count_dict = {}
        self.count = 0
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        queue_time = time.time()
        async with self.lock:
            await self.queue.put(request_id)
            self.count += 1
            self.count_dict[request_id] = self.count
        logger.info(f"Request {self.count_dict[request_id]} add in queue | "
                    f"Queue size: {self.queue.qsize()} | "
                    f"Time {time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(queue_time))}")
        try:
            async with self.semaphore:
                wait_time = time.time() - queue_time
                start_time = time.time()

                logger.info(
                    f"Request {self.count_dict[request_id]} started processing | "
                    f"Wait time: {wait_time:.2f}s | ")

                response = await call_next(request)

                async with self.lock:
                    await self.queue.get()
                    process_time = time.time() - start_time

                logger.info(
                    f"Request {self.count_dict[request_id]} completed successfully | "
                    f"Queue size: {self.queue.qsize()} | "
                    f"Process time: {process_time:.2f}s | "
                    f"Status: {response.status_code}")

                return response

        except ValueError:
            return JSONResponse(
                content={"status": "cancelled"},
                status_code=499
            )


app.add_middleware(RateLimitingMiddleware)

def get_audio_duration(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        duration_in_seconds = audio.duration_seconds
        logger.info(
            f"Длительность файла {file_path}: {duration_in_seconds:.2f} секунд")
        return duration_in_seconds
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке файла {file_path}: {e}")
        return 0


def get_least_utilized_gpu():
    max_free_memory = 8000 * 1024 * 1024
    best_gpu = None

    for i in range(torch.cuda.device_count()):
        free_memory = torch.cuda.mem_get_info(i)[0]

        free_memory -= random.randint(20, 200)

        if free_memory > max_free_memory:
            max_free_memory = free_memory
            best_gpu = i
    return best_gpu


device = get_least_utilized_gpu()

logger.info(f"Selected CUDA: {device}")

model = whisperx.load_model("large-v3", device="cuda", device_index=device,
                            compute_type="float16", language="ru",
                            asr_options={
                                "initial_prompt": ""},
                            vad_options={"vad_onset": 0.4, "vad_offset": 0.3})
model1 = whisperx.load_model("large-v3", device="cuda", device_index=device,
                             compute_type="float16", language="ru",
                             vad_options={"vad_onset": 0.1, "vad_offset": 0.1},
                             asr_options={"no_speech_threshold": 0.1})
model2 = whisperx.load_model("large-v3", device="cuda", device_index=device,
                             compute_type="float16", language="ru",
                             asr_options={
                                 "initial_prompt": ""})
model_a, metadata = whisperx.load_align_model(language_code='ru',
                                              device=f"cuda:{device}")
diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_TOKEN,
                                             device=f"cuda:{device}")


def get_payload(prompt,
                transcription,
                system_content="You are a helpful assistant.",
                temperature=0.87,
                top_p=0.47,
                max_tokens=30000):
    return {
        "id": "-1",
        "dialog": [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": prompt + str(transcription)
            }
        ],
        "gen_profile": "VANILLA",
        "gen_kwargs_overrides": {"max_new_tokens": max_tokens,
                                 "temperature": temperature,
                                 "top_p": top_p}
    }


def send_to_t1(transcription, temp_first_elem, audio_id):
    system_content = """
1) Вы самый лучший аналитик диалогов между менеджером компании и клиентом с более чем десятилетним опытом. Вы умеете внимательно читать диалог, убирать лишнюю и выделять главную информацию из диалога, хорошо разбираетесь в банковской и предпринимательской сфере, а также знаете, как в общем строится диалог между менеджером компании и клиентом.
2) Ты здесь для того, чтобы помочь аналитику диалога проанализировать ДИАЛОГ между менеджером компании и клиентом и определить, на каком месте должна стоять определенная реплика клиента.
3) ДИАЛОГ в запросе является списком, который внутри себя содержит словарь с двумя полями: "speaker" и "text". В "speaker" указано, кто говорит текст:
SPEAKER_01, то есть менеджер или "SPEAKER_00", то есть клиент.
6) Ты должен вернуть словарь, содержащий позицию РЕПЛИКИ в ДИАЛОГЕ. Позиция РЕПЛИКИ - это целое положительное число большее либо равное 1;
7) Ты должен следовать ПРАВИЛАМ ОТВЕТА без исключений.
8) ПРАВИЛЬНОСТЬ ОТВЕТА ОЧЕНЬ ВАЖНА ДЛЯ МЕНЯ!
"""
    prompt = f"""1) При ответе рассуждай так, как указано в ЦЕПОЧКЕ МЫСЛЕЙ.
                 2) Подсчет элементов в списке начинается 1.
### ЦЕПОЧКА МЫСЛЕЙ ###:
1) Соблюдай режим выполнения;
2) Анализ ДИАЛОГА:
- раздели список реплик между двумя говорящими в нем, исходя из того, что указано в поле "speaker". "assistant" - это менеджер, а "user" - клиент;
- пойми, на какую тему ведется диалог;
- помни, менеджер всегда звонит клиенту сам;
- учти, что диалог строится в формате вопрос и ответ на него.
3) Анализ РЕПЛИКИ клиента:
- пойми, в какой месте диалога клиент мог сказать РЕПЛИКУ;
- учти, что в начале диалога всегда идет приветствие;
- если не знаешь, на какое место вставить РЕПЛИКУ, то верни значение position равное 1.
4) ПРОВЕРКА:
- проверь, что в поле "position" указано целое число больше либо равно 1;
- проверь, что ты возвращаешь словарь;
- проверь, что возвращаемый словарь состоит только из поля position.

Результатом должен быть фрагмент кода markdown без комментариев, отформатированный по следующей схеме, включая начальный и конечный символы "```json" и "```".
```json
{{
    "position": integer //Позиция репликп
}}
```

### РЕПЛИКА ###: "{temp_first_elem}"
### ДИАЛОГ ####: """

    payload = get_payload(prompt=prompt, system_content=system_content,
                          transcription=transcription)

    logger.info(
        f"Payload for {audio_id}: {json.dumps(payload, ensure_ascii=False)}")

    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(T1_API_URL,
                                 data=json.dumps(payload),
                                 headers=headers,
                                 timeout=10000)
        logger.info(
            f"Отправка запроса в T1_Chat for {audio_id}: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            content = json_repair.loads(content)["preds"][0]["text"]
            content = re.search("\{.*\}", content.replace("\n", ""))
            content = content.group()
            content = json_repair.loads(content)
            if isinstance(content, list) and len(content) > 0:
                for i in content:
                    if isinstance(i, dict) and "position" in i:
                        content = i

            logger.info(f"CONTENT for {audio_id}: {content}")

            return content
        else:
            logger.error(
                f"Ответ от сервера T1_Chat for {audio_id}: {response.text}")
            return None
    except requests.exceptions.Timeout:
        logger.error(
            "Запрос к T1_Chat for {audio_id} превысил время ожидания.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к T1_Chat for {audio_id}: {e}")
        return None


def load_audio(audio_file):
    audio, _ = librosa.load(audio_file, sr=16000, mono=False)
    if audio.ndim > 1:
        audio[0] = librosa.util.normalize(audio[0])

    return audio


def process(audio_file):
    result = ""
    text = ""
    with torch.cuda.device(device):
        audio = load_audio(audio_file)
        segments = []

        if audio.ndim > 1:
            for channel_id in range(audio.shape[0]):
                channel = audio[channel_id]

                logger.info(f"Channel id for {audio_file}: {channel_id}")

                if channel_id == 1:
                    channel_segments = model.transcribe(channel)["segments"]
                else:
                    channel_segments = model1.transcribe(channel)["segments"]

                if not channel_segments:
                    continue
                try:
                    channel_segments = \
                    whisperx.align(channel_segments, model_a, metadata,
                                   channel, f"cuda:{device}",
                                   return_char_alignments=False)["segments"]
                except Exception as e:
                    logger.error(f"Align error for {audio_file}: {e}")
                    logger.info(
                        f"Returning align for {audio_file}: {channel_segments}")

                for segment in channel_segments:
                    segment["channel"] = channel_id

                segments.extend(channel_segments)

            segments = sorted(segments, key=lambda x: x["start"])

            result = [
                {"speaker": f"SPEAKER_0{i['channel']}", "text": i["text"]} for
                i in segments if
                "channel" in i and "Продолжение следует" not in i["text"]
                and "DimaTorzok" not in i[
                    "text"] and "Эвотор, Сбербанк, Лусине" not in i[
                    "text"] and "Сбербанк, Лусине" not in i["text"]
                and "Эвотор, Сбербанк" not in i["text"]]

            if len(result) > 0 and "speaker" in result[0] and result[0][
                "speaker"] == "SPEAKER_00" and len(
                    set([i["speaker"] for i in result])) >= 2:
                temp_first_elem = result[0]
                del result[0]
                try:
                    right_position = int(
                        send_to_t1(result, temp_first_elem["text"],
                                   audio_file)["position"])
                    logger.info(
                        f"Right position for first elem for {audio_file}: {right_position}")
                    if right_position > 0:
                        right_position -= 1
                    result.insert(right_position, temp_first_elem)
                except Exception as e:
                    logger.error(
                        f"Error while choosing right position for {audio_file}: {e}")

            if len(result) > 0:
                text = [i["text"] for i in result]
                text = " ".join(text)

        else:
            logger.info(f"Audio {audio_file} is mono. Starting diarisation")
            diarize_segments = diarize_model(audio_file, num_speakers=2)
            audio = whisperx.load_audio(audio_file)
            result = model2.transcribe(audio)
            result = whisperx.align(result["segments"], model_a, metadata,
                                    audio, f"cuda:{device}",
                                    return_char_alignments=False)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            result = [{"speaker": i["speaker"], "text": i["text"]} for i in
                      result['segments'] if "speaker" in i
                      and "Продолжение следует" not in i[
                          "text"] and "DimaTorzok" not in i["text"]
                      and "Эвотор, Сбербанк, Лусине" not in i[
                          "text"] and "Сбербанк, Лусине" not in i["text"]
                      and "Эвотор, Сбербанк" not in i["text"]]
            text = [i["text"] for i in result]
            text = " ".join(text)

    return text, result


def download_file(url, destination_path):
    try:
        parsed_url = urlparse(url)
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        with req_session_for_download.get(cleaned_url, stream=True) as r:
            r.raise_for_status()
            with open(destination_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info(f"Файл успешно скачан: {destination_path}")
    except Exception as e:
        logger.error(f"Произошла ошибка при скачивании файла: {e}")
        raise

@app.post('/transcribe')
async def transcribe(request: Request):
    audio_file = ''
    try:
        data = await request.json()
        audio_url = data["audio_url"]
        audio_path = data["url_path"]
        audio_file = f'audio_files/{audio_url}.mp3'
        download_file(audio_url, audio_path)
        duration = get_audio_duration(audio_file)

        logger.info(f"Task for {audio_file} started transcribing")

        text, result = process(audio_file)
        os.remove(audio_file)

        logger.info(f"Task for {audio_file} completed")

    except Exception as e:
        logger.error(
            f"An error occurred during transcription for {audio_file}: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")
    return {'text': text, "result": result, "duration": duration}
