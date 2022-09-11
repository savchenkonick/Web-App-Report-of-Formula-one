# from peewee import *
import peewee
import sqlite3
from f_one.f_one import generate_file_paths
from models import db, Driver, Qualification
import datetime
import pprint

# class Driver(Model):
#     code = CharField()
#     name = CharField()
#     car = DateField()
#
#     class Meta:
#         database = db
#
#
# class Q1(Model):
#     driver = ForeignKeyField(Driver, backref='Q1')
#     start = DateTimeField()
#     stop = DateTimeField()
#
#     class Meta:
#         database = db


def parse_drivers_files() -> list:
    paths = generate_file_paths('static/data')
    drivers = []
    abbreviations_file_path = paths['abbreviations.txt']  # abbreviations.txt
    with open(abbreviations_file_path, 'r') as abbr:
        for line in abbr.readlines():
            if line == '\n':
                continue
            data = line.rstrip().split('_')
            drivers.append((data[0], data[1], data[2]))
    return drivers


def parse_laps_files() -> dict:
    paths = generate_file_paths('static/data')
    laps_time = {}
    start_file_path = paths['start.log']
    with open(start_file_path, 'r') as start:
        for line in start.readlines():
            if line == '\n':
                continue
            name = line[0:3]
            time = line[3:].rstrip()
            dt = datetime.datetime.strptime(time, '%Y-%m-%d_%H:%M:%S.%f')
            laps_time[name] = [dt]

    end_file_path = paths['end.log']
    with open(end_file_path, 'r') as stop:
        for line in stop.readlines():
            if line == '\n':
                continue
            name = line[0:3]
            time = line[3:].rstrip()
            dt = datetime.datetime.strptime(time, '%Y-%m-%d_%H:%M:%S.%f')
            laps_time[name].append(dt)
            lap_time = (dt - laps_time[name][0]).total_seconds()
            laps_time[name].append(lap_time)
    # pprint.pprint(laps_time)
    return laps_time


def store_drivers(drivers):
    db.connect()
    for driver in drivers:
        try:
            record = Driver.create(driver_code=driver[0], driver_name=driver[1],
                                   car=driver[2])
            record.save()
        except peewee.IntegrityError:
            pass
    db.close()


def store_laps_files(laps_time):
    db.connect()
    for code, times in laps_time.items():
        try:
            record = Qualification.create(driver_code=code, start=times[0],
                                          stop=times[1], lap_time=times[2])
            record.save()
        except peewee.IntegrityError:
            pass
    db.close()


def retrieve_drivers_data():
    db.connect()
    # for dr in Driver.select().iterator(db):
    for dr in Driver.select():
        print(dr.driver_code, dr.driver_name, dr.car)
    db.close()


def retrieve_laps_data():
    db.connect()
    # for dr in Qualification.select().iterator(db):
    for dr in Qualification.select():
        print(dr.driver_code, dr.start, dr.stop, dr.lap_time)
    db.close()


def create_tables() -> bool:
    """Create tables if they are not exist.
    Return:
         True: There were no tables Driver and Qualification in db. Function
         created them
         False: Tables were in database
    """
    tables_created = False
    db.connect()
    if not db.table_exists(Driver):
        print('Creating table Driver')
        db.create_tables([Driver])
        tables_created = True
    if not db.table_exists(Qualification):
        print('Creating table Qualification')
        db.create_tables([Qualification])
        tables_created = True
    db.close()
    return tables_created


def main():
    if create_tables():
        drivers = parse_drivers_files()
        store_drivers(drivers)
        lap_times = parse_laps_files()
        store_laps_files(lap_times)
    # retrieve_drivers_data()
    # retrieve_laps_data()

    # con = sqlite3.connect('f1.sqlite3')
    # cursor = con.cursor()
    # try:
    #     sql_del = cursor.execute("DELETE FROM Driver WHERE driver_code = 'KMH'")
    #     print("Total records affected: ", sql_del.rowcount)
    #     con.commit()
    # except sqlite3.Error as e:
    #     print(f"Oops! Something went wrong. Error: {e}")
    #     # reverse the change in case of error
    #     con.rollback()

    # query = 'PRAGMA foreign_key_list("Qualification")'
    # query = 'PRAGMA table_info("Qualification");'
    query = 'PRAGMA table_info("driver");'
    # query = 'select * from Qualification'
    # query = 'select * from Driver'

    con = sqlite3.connect('f1.sqlite3')
    cursor = con.cursor()
    cursor.execute(query)
    all_rows = cursor.fetchall()
    print(len(all_rows))
    pprint.pprint(all_rows)
    cursor.close()
    con.close()

    # retrieve_drivers_data()
    # retrieve_laps_data()


if __name__ == "__main__":
    main()
