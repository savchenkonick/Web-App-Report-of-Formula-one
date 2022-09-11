"""Report of Monaco 2018 Racing
Application that builds and prints results of Formula 1 qualification
results. User needs to enter in command line with the help of --file key
path to folder with 3 files: abbreviations.txt, start.log and end.log which
store start and end of best lap time. It prints a sorted or reversed report
with the help of --desc or --asc key. --asc is default. Using
--driver <driver name> key will show you the result of only mentioned driver

Example: python --file data --desc

Format of abbreviations.txt:
SVF_Sebastian Vettel_FERRARI
LHM_Lewis Hamilton_MERCEDES

Format of start.log and end.log:
SVF2018-05-24_12:02:58.917
NHR2018-05-24_12:02:49.914


Functions:
    main()
    Collect and parse arguments: path to directory with files,
    driver (if needed), sorting order. Check that files exists. Send argument
    values to build_report function

    generate_file_paths(folder: str) -> dict | None:
    Check if folder and files exist. Returns dict with keys as file names and
    values as Path objects with file's path

    build_report(dir_path: str) -> tuple[list, list, list] | None:
    Return list with record of best lap of each driver, list
    with pilots' codes abbreviations and meaning, list with unreliable negative
    results, that are not present in result list

    print_report(report: list, reverse: bool = False, driver_name: str = None):
    Print report in format POS.DRIVER|CAR|Q1
    If driver name is not None function will try to find driver and print only
    one result of this driver

Global var:
    FILTERING = True - Filter unreliable results with negative time

Vars:
    file_start = "start.log"
    file_end= "end.log"
    file_abbreviations = "abbreviations.txt"
"""

import datetime
import argparse
from pathlib import Path
from peewee import *

FILTERING = True


def print_report(report: list, reverse: bool = False, driver_name: str = None):
    """Print report in format POS.DRIVER|CAR|Q1
    If driver name is not None function will try to find driver and print only
    one result of this driver.
    Arguments:
    report -- Report with best lap results
    reverse -- Ascending - False or descending - True (default False)
    driver_name -- print only particular driver (default None)
    """
    template = "{0:3}.{1:20}|{2:26}|{3:6}"  # column widths: 8, 10, 15, 7, 10
    print(template.format("POS", "DRIVER", "CAR", "Q1"))  # header

    if driver_name:  # Print report only for 1 driver
        record = [rec for rec in report if rec[1] == driver_name]
        if not record:
            print('Cannot find driver. Please check driver name')
            return None
        print(template.format(*record[0]))
    else:  # All drivers
        if reverse:
            report.reverse()
        for rec in report:
            if rec[0] == 16 and reverse:
                # Draw the line below which pilots will not pass to Q2
                print(template.format(*rec))
                print('-'*60)
            elif rec[0] == 16:
                print('-'*60)
                print(template.format(*rec))
            else:
                print(template.format(*rec))


def build_report(dir_path: str) -> tuple[list, list, list] | None:
    """Return list with record of best lap of each driver, list
    with pilots' codes abbreviations and meaning, list with unreliable negative
    results, that are not present in result list
    Argument:
    dir_path -- Path to directory with log files
    """
    pilots = {}
    qualification_report = {}
    paths = generate_file_paths(dir_path)
    unreliable_data = []
    if paths is None:
        return None
    abbreviations_file_path = paths['abbreviations.txt']  # abbreviations.txt
    with open(abbreviations_file_path, 'r') as abbr:
        for line in abbr.readlines():
            if line == '\n':
                continue
            data = line.rstrip().split('_')
            pilots[data[0]] = (data[1], data[2])

    start_file_path = paths['start.log']
    with open(start_file_path, 'r') as start:
        for line in start.readlines():
            if line == '\n':
                continue
            name = line[0:3]
            time = line[3:].rstrip()
            dt = datetime.datetime.strptime(time, '%Y-%m-%d_%H:%M:%S.%f')
            qualification_report[name] = [dt]

    end_file_path = paths['end.log']
    with open(end_file_path, 'r') as stop:
        for line in stop.readlines():
            if line == '\n':
                continue
            name = line[0:3]
            time = line[3:].rstrip()
            dt = datetime.datetime.strptime(time, '%Y-%m-%d_%H:%M:%S.%f')
            lap_time = (dt - qualification_report[name][0]).total_seconds()
            qualification_report[name].append(lap_time)

    results_raw = {}
    for name_abbr, lap_time in qualification_report.items():
        name, car = pilots[name_abbr]
        results_raw[name] = [car, lap_time[1]]

    results = dict(sorted(results_raw.items(), key=lambda kv: kv[1][1]))
    report = []
    i = 1
    for pilot in results.keys():
        car, lap_time = results[pilot]
        if lap_time < 0 and FILTERING:
            unreliable_data.append(('Unknown', pilot, car, 'Unreliable'))
            continue
        minutes = int(lap_time // 60)
        seconds = lap_time - minutes * 60
        lap_time_formatted = f'{minutes}:{seconds:.3f}'
        report.append((i, pilot, car, lap_time_formatted))
        i += 1
    pilots_list = [[code, value[0], value[1]]
                   for code, value in pilots.items()]
    return report, pilots_list, unreliable_data


def generate_file_paths(folder: str) -> dict | None:
    """Check if folder and files exist. Returns dict with keys as file names and
     values as Path objects with file's path"""
    file_abbreviations = "abbreviations.txt"
    file_end = "end.log"
    file_start = "start.log"
    path_to_folder = Path(__file__).resolve().parents[1].joinpath(folder)
    if not path_to_folder.is_dir():
        print(f'Cannot open {path_to_folder} folder')
        return None
    file_paths = {}  # dict with key as filename and value as Path object
    files_names = [file_abbreviations, file_end, file_start]
    for file in files_names:
        file_path = path_to_folder / file
        if file_path.is_file():
            file_paths[file] = file_path  # file-file name, file_path-Path obj
        else:
            print(f"File {file_start} doesn't exists")
            return None
    return file_paths


def pars_args(dir_path):
    """Collect and parse arguments: path to directory with files,
     driver (if needed), sorting order. Check that files exists.
    Send argument values to build_report function"""
    description = """The scrypt builds and prints results of Formula 1 
    qualification results. User needs to enter path to folder with 3 files:
    abbreviations, start and stop lap times. It prints a sorted report"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-f", "--files", help="Path to folder with log files")
    parser.add_argument("--asc", action="store_true", default=True,
                        help="Sorting order: ascending. Default ascending")
    parser.add_argument("--desc", action="store_true",
                        help="Sorting order: descending. Default ascending")
    parser.add_argument("-d", "--driver", default=None, nargs='+',
                        help="Statistic about particular driver")
    args = parser.parse_args()
    if args.files is not None:
        data_folder = args.files
    else:
        data_folder = dir_path
    if args.driver:
        driver_name = ' '.join(args.driver)
    else:
        driver_name = None
    desc_order = args.desc
    q1_report = build_report(data_folder)[0]
    # Index 0 for qualification report, 1 for pilots list,
    # 2 for unreliable results
    print_report(q1_report, reverse=desc_order, driver_name=driver_name)


def parse_to_db():
    db = SqliteDatabase('f1.db')

    class Driver(Model):
        name = CharField()
        car = DateField()

        class Meta:
            database = db

    class Q1(Model):
        driver = ForeignKeyField(Driver, backref='Q1')
        start = DateTimeField()
        stop = DateTimeField()

        class Meta:
            database = db

    db.connect()
    db.create_tables([Driver, Q1])
    lwh = Driver(name='Hammilton', car='Mercedes')
    lwh.save()
    db.close()


def main():
    pass
    # pars_args('static/data')
    # parse_to_db()

if __name__ == '__main__':
    main()
