from datetime import datetime,timedelta
from vehicule_enum import VehiculeCategory
import os
import csv
import itertools as it
import operator as op

WDIR = os.path.abspath(os.path.dirname(__file__))
CSV_DB_PATH = WDIR + os.sep + 'datafile.csv'

def csv_date_to_epoch(date_string: str) -> int:
    datetime_object = datetime.strptime(date_string, r"%Y-%m-%d %H:%M")

    return int(datetime_object.timestamp())

def csv_vehicule_to_enumvehicule(vehicule_string : str) -> VehiculeCategory:
    for category in VehiculeCategory:
        if category.csv_name.casefold() == vehicule_string.casefold():
            return category
    raise TypeError()

def epoch_to_day_date(epoch_time: int)->str:

    datetime_object = datetime.utcfromtimestamp(epoch_time)

    formatted_date = datetime_object.strftime("%Y-%m-%d")
    return str(formatted_date)

def parse_to_sorted_day_dict():
    with open(CSV_DB_PATH,'r') as file:
        csv_reader = csv.reader(file)
        headers = ["requestcall_datetime", "start_datetime", "vehicle_category"]

        data_list = [dict(zip(headers, row)) for row in csv_reader]
        data_list.sort(key=lambda x: csv_date_to_epoch(x["start_datetime"]))#tuple(x["start_datetime"].split(' ')))

        # filtered_data_list = list(filter(lambda data : data['start_datetime'], data_list))

        grouped_entries = {date: list(group) for date, group in it.groupby(data_list, key=lambda x: x["start_datetime"].split(' ')[0])}
        for day, bookings_lst in grouped_entries.copy().items():
            for ix,b in enumerate(bookings_lst):
                grouped_entries[day][ix]['vehicle_category'] = category =  csv_vehicule_to_enumvehicule(grouped_entries[day][ix]['vehicle_category'])
                del grouped_entries[day][ix]['vehicle_category']
                # endtime_epoch = csv_date_to_epoch(b['start_datetime']) #+ category.hours * 3600
                endtime_obj = datetime.strptime(b['start_datetime'], r"%Y-%m-%d %H:%M") + timedelta(hours=category.hours)
                grouped_entries[day][ix]['end_datetime'] = endtime_obj.strftime("%H:%M")

                grouped_entries[day][ix]['start_datetime'] = b['start_datetime'].split(' ')[1]

                del grouped_entries[day][ix]['requestcall_datetime']

                grouped_entries[day][ix]['vehicle_category'] = category
            grouped_entries[day].sort(key=op.itemgetter('start_datetime'))
        return grouped_entries

if __name__ == '__main__':
    grouped_entries = parse_to_sorted_day_dict()
    print(*grouped_entries.keys(),sep="\n\r")
    print()
    for day,bookings_lst in grouped_entries.items():
        print(day)
        for b in bookings_lst:
            print(b)
        exit()
