from peewee import *


db = SqliteDatabase('f1.sqlite3', pragmas={'foreign_keys': 1})


class Driver(Model):
    driver_code = CharField(primary_key=True)
    driver_name = CharField()
    car = DateField()

    class Meta:
        database = db


class Qualification(Model):
    driver_code = ForeignKeyField(Driver, on_delete='CASCADE')
    start = DateTimeField()
    stop = DateTimeField()
    lap_time = FloatField()

    class Meta:
        database = db
