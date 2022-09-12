from f_one.f_one import generate_file_paths
from models import db, Driver, Qualification
import datetime


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


def parse_laps_files() -> list:
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
    result = []
    for code, times in laps_time.items():
        result.append((code, times[0], times[1], times[2]))
    return result


def store_drivers(drivers):
    fields = [Driver.driver_code, Driver.driver_name, Driver.car]
    with db.atomic():
        Driver.insert_many(drivers, fields=fields).execute()


def store_laps_files(laps_time):
    fields = [Qualification.driver_code,
              Qualification.start,
              Qualification.stop,
              Qualification.lap_time]
    with db.atomic():
        Qualification.insert_many(laps_time, fields=fields).execute()


def retrieve_drivers_data():
    for dr in Driver.select():
        print(dr.driver_code, dr.driver_name, dr.car)


def retrieve_laps_data():
    for dr in Qualification.select():
        print(dr.driver_code, dr.start, dr.stop, dr.lap_time)


def create_tables() -> bool:
    """Create tables if they are not exist.
    Return:
         True: There were no tables Driver and Qualification in db. Function
         created them
         False: Tables were in database
    """
    tables_created = False
    if not db.table_exists(Driver):
        db.create_tables([Driver])
        tables_created = True
    if not db.table_exists(Qualification):
        db.create_tables([Qualification])
        tables_created = True
    return tables_created


@db.connection_context()
def main():
    if create_tables():
        drivers = parse_drivers_files()
        store_drivers(drivers)
        lap_times = parse_laps_files()
        store_laps_files(lap_times)
    retrieve_laps_data()
    retrieve_drivers_data()


if __name__ == "__main__":
    main()
