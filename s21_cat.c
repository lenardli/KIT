#include <getopt.h>  //regex
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define GNU_SOURCE

void indents_count(int count);
void print_file(char *short_flag, char *long_flag, char *filename);
void options(char *filename, char *short_flag);

void indents_count(int count) {
  int nums = 0;
  while (count > 0) {
    count /= 10;
    nums += 1;
  }
  for (int i = 0; i <= 5 - nums; i++) {
    printf("%c", ' ');
  }
}
void options(char *filename, char *short_flag) {
  FILE *f = fopen(filename, "r");
  int ch = fgetc(f);
  while (ch != EOF) {
    if (ch > 127 && ch < 160) printf("M-^");
    if ((ch >= 0 && ch < 9) || (ch > 10 && ch < 32) || ch == 127) printf("^");
    if ((ch > 126 && ch < 160) || (ch >= 0 && ch < 9) || (ch > 10 && ch < 32))
      ch = ch < 126 ? ch + 64 : ch - 64;
    if (strchr(short_flag, 'e') != NULL && ch == '\n') printf("$");
    if (strchr(short_flag, 't') != NULL && ch == '\t') {
      printf("^");
      ch += 64;
    }
    fputc(ch, stdout);
    ch = fgetc(f);
  }
  fclose(f);
}
void print_file(char *short_flag, char *long_flag, char *filename) {
  FILE *f = fopen(filename, "rt");
  char *c = NULL;
  int count1 = 0, count2 = 0, count_file = 0;
  char first_char = '\0';
  int flag_s = 0, flag_t = 0, flag_b = 0, flag_v = 0, flag_e = 0;
  size_t n = 256;
  if (f != NULL) {
    while (getline(&c, &n, f) != -1) {
      if (strchr(short_flag, 's') != NULL ||
          strstr(long_flag, "squeeze-blank") != NULL) {
        if ((first_char == '\n') && (c[0] == '\n')) {
          flag_s = 1;
        }
      }
      if (!flag_s) {
        if ((strchr(short_flag, 'b') != NULL ||
             strstr(long_flag, "number-nonblank") != NULL)) {
          if (c[0] != '\n') {
            count2 += 1;
            indents_count(count2);
            printf("%d\t", count2);
          }
          flag_b = 1;
        }
        if (!flag_b && (strchr(short_flag, 'n') != NULL ||
                        strstr(long_flag, "number") != NULL)) {
          count1 += 1;
          indents_count(count1);
          printf("%d\t", count1);
        }
        if (count_file) {
          count_file = 0;
        }
        if (strchr(short_flag, 'v') != NULL ||
            strchr(short_flag, 'e') != NULL ||
            strchr(short_flag, 't') != NULL) {
          options(filename, short_flag);
          break;
          flag_v = 1;
        }
        if (strchr(short_flag, 'E') != NULL) {
          for (int i = 0; c[i] != '\0'; i++) {
            if (c[i] == '\n') printf("%c", '$');
            printf("%c", c[i]);
          }
          flag_e = 1;
        }
        if (strchr(short_flag, 'T') != NULL) {
          for (int i = 0; c[i] != '\0'; i++) {
            if (c[i] == '\t') {
              c[i] += 64;
              printf("%c", '^');
            }
            printf("%c", c[i]);
          }
          flag_t = 1;
        }
        if (!flag_t && !flag_v && !flag_e) {
          printf("%s", c);
        }
      }
      flag_s = 0;
      first_char = c[0];
    }
    if (c != NULL) free(c);
    fclose(f);
  } else {
    fprintf(stderr, "No such file %s\n", filename);
  }
}

int main(int argc, char *argv[]) {
  const char *short_options = "benstvTE";
  int flag_a = 0, rez = 0, option_index = 0;
  char short_flag[20] = {'\0'}, long_flag[30] = {'\0'}, temp1 = '\0',
       temp[2] = {'\0'};
  const struct option long_options[] = {{"number-nonblank", 3, &flag_a, 1},
                                        {"squeeze-blank", 3, &flag_a, 2},
                                        {"number", 3, &flag_a, 3},
                                        {NULL, 0, NULL, 0}};
  while ((rez = getopt_long(argc, argv, short_options, long_options,
                            &option_index)) != -1) {
    switch (rez) {
      case 0:
        strcat(long_flag, long_options[option_index].name);
        break;
      case '?':
        temp1 = rez;
        break;
      default:
        temp[0] = rez;
        strcat(short_flag, temp);
        break;
    }
  }
  if (temp1 != '?') {
    for (; optind < argc; optind++) {
      print_file(short_flag, long_flag, argv[optind]);
    }
  }
  return 1;
}