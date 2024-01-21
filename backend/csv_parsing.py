from datetime import datetime,timedelta
from vehicule_enum import VehiculeCategory
import os
import csv
import itertools as it
import operator as op
from bay_intervals_ds import maximize_non_overlapping
import numpy as np

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
                grouped_entries[day][ix]['vehicle_category'] = category = csv_vehicule_to_enumvehicule(grouped_entries[day][ix]['vehicle_category'])
                del grouped_entries[day][ix]['vehicle_category']
                # endtime_epoch = csv_date_to_epoch(b['start_datetime']) #+ category.hours * 3600
                endtime_obj = datetime.strptime(b['start_datetime'], r"%Y-%m-%d %H:%M") + timedelta(hours=category.hours)
                grouped_entries[day][ix]['end_datetime'] = endtime_obj.strftime("%H:%M")

                grouped_entries[day][ix]['day'] = day
                grouped_entries[day][ix]['isWalkIn'] = is_walk_in = b['start_datetime'] == b['requestcall_datetime']
                grouped_entries[day][ix]['isSameDayBooking'] = not is_walk_in and request_day == day

                grouped_entries[day][ix]['start_datetime'] = b['start_datetime'].split(' ')[1]


                grouped_entries[day][ix]['vehicle_category'] = category
                request_day = b['requestcall_datetime'].split(' ')[0]#datetime.strptime(b['requestcall_datetime'].split(' ')[0], r"%Y-%m-%d")



                del grouped_entries[day][ix]['requestcall_datetime']

            grouped_entries[day].sort(key=op.itemgetter('start_datetime'))
        return grouped_entries

if __name__ == '__main__':
    grouped_entries = parse_to_sorted_day_dict()
    rows = 10
    columns = 720
    zero_filled_array = [np.array(columns*[0]) for _ in range(rows)]

    # zero_filled_array = final_half_greedy_bayconfig(
    #     *initial_half_avg_optimal_bayconfig(zero_filled_array,
    #
    #                                         list(grouped_entries.values())[2]))
    print("DONE SETTING UP THE OPTIMAL INITIAL STATE")
    for day,day_bookings in grouped_entries.items():
        zero_filled_array = final_half_greedy_bayconfig(
            *initial_half_avg_optimal_bayconfig(zero_filled_array,

                                                day_bookings))
        for timestamp_booking in filter(lambda b: b['isWalkIn'] or b['isSameDayBooking'], day_bookings):
            start = timestamp_booking["start_datetime"]
            end = timestamp_booking["end_datetime"]
            duration = calculate_duration_in_minutes(start, end)

            start_minute = calculate_duration_in_minutes('07:00', start)

            if timestamp_booking["vehicle_category"] is VehiculeCategory.CLASS2_TRUCK:
                if int(start_minute) >= 600:
                    continue
            if timestamp_booking["vehicle_category"] is VehiculeCategory.CLASS1_TRUCK:
                if int(start_minute) >= 660:
                    continue
            if timestamp_booking["vehicle_category"] is VehiculeCategory.COMPACT_CAR or timestamp_booking["vehicle_category"] is VehiculeCategory.MEDIUM_CAR or timestamp_booking["vehicle_category"] is VehiculeCategory.FULLSIZE_CAR:
                if int(start_minute) >= 690:
                    continue
            type_veh = get_vehicule_ordinal_from_booking(timestamp_booking)
            flag = 0
            for reservedBayNumber in range(0,5):
                if type_veh != reservedBayNumber+1:
                    continue
                if flag == 0:
                    initial_state = [row[:] for row in zero_filled_array]
                    for i in range(int(duration)):
                        index = int(start_minute) + i
                        if zero_filled_array[reservedBayNumber][index] != 0:
                            zero_filled_array = initial_state
                            flag = 0
                            break
                        zero_filled_array[reservedBayNumber][index] = zero_filled_array[reservedBayNumber][
                                                                          index] + type_veh
                        flag = 1
            for freeBayNUmber in range(5,10):
                if flag == 0:
                    initial_state = [row[:] for row in zero_filled_array]
                    for i in range(int(duration)):
                        index = int(start_minute) + i
                        if zero_filled_array[freeBayNUmber][index] != 0:
                            zero_filled_array = initial_state
                            flag = 0
                            break
                        zero_filled_array[freeBayNUmber][index] = zero_filled_array[freeBayNUmber][index] + type_veh
                        flag = 1
        print(day)
        print_2d_array(zero_filled_array)
        print()
        input()
        # exit()
    #print_2d_array(zero_filled_array)
    # printable_matrix = list(map(lambda row: ''.join(map(str,row)),zero_filled_array))
    # print(*printable_matrix,sep="\n\n\r")
    # exit()

    # print(*grouped_entries.keys(),sep="\n\r")
    # print()
    # for day,bookings_lst in grouped_entries.items():
    #     print(day)
    #     for b in bookings_lst:
    #         print(b)
    #     exit()
