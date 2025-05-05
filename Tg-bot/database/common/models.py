from datetime import datetime

import peewee as pw

db = pw.SqliteDatabase("first.db")


class ModelBase(pw.Model):
    created_at = pw.DateTimeField(default=datetime.now())

    class Meta():
        database = db


class History(ModelBase):
    profession_type = pw.TextField()
    user_id = pw.TextField()


