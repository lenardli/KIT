from database.common.models import db, ModelBase
from typing import List, Dict, TypeVar, Tuple

from peewee import ModelSelect

T = TypeVar("T")


def _store_date(db: db, model: T, *data: List[Dict]) -> None:
    with db.atomic():
        model.insert_many(*data).execute()


def _retrieve_single_row(db: db, model: T, query: str) -> ModelSelect:
    with db.atomic():
        response = model.select().where(model.user_id == query)
    return response


def _retrieve_all_data(db: db, model: T, *columns: ModelBase) -> ModelSelect:
    with db.atomic():
        response = model.select(*columns)
    return response


class CRUDInterface:
    @classmethod
    def create(cls):
        return _store_date

    @classmethod
    def retrieve_all(cls):
        return _retrieve_all_data

    @classmethod
    def retrieve_single(cls):
        return _retrieve_single_row


if __name__ == "__main__":
    _store_date()
    _retrieve_all_data()
    _retrieve_single_row()
    CRUDInterface()
