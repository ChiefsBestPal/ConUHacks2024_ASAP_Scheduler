from datetime import datetime,timedelta
from vehicule_enum import VehiculeCategory
import os
import csv
import itertools as it
import operator as op
from bay_intervals_ds import maximize_non_overlapping
import numpy as np
from collections import Counter,defaultdict

SERVICED_VEHICULE_CATEGORIES_COUNTERFUNC = lambda *args,**kwargs: \
                        Counter(**dict.fromkeys(list(VehiculeCategory.__members__),0))
SERVICED_TRACKER_DDICT = defaultdict(SERVICED_VEHICULE_CATEGORIES_COUNTERFUNC)


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


def initial_half_avg_optimal_bayconfig(bay_matrix : list[np.ndarray], day_bookings: list[dict]) -> tuple[list[np.ndarray],list]:
    hourtime_to_matrixminutes = lambda hourtime: int((datetime.strptime(hourtime, "%H:%M") - datetime.strptime('07:00', "%H:%M")).total_seconds() // 60)

    remaining_bookings_for_freebays = []

    normal_bookings = list(it.filterfalse(lambda b: b['isWalkIn'] or b['isSameDayBooking'], day_bookings))

    
    for reservedBayNumber in range(0, 5):
        vehicule_enum_ordinal = reservedBayNumber + 1
        bay_normal_bookings = list(filter(lambda b:get_vehicule_ordinal_from_booking(b) == vehicule_enum_ordinal,
                                     normal_bookings))

        bay_normal_intervals = list(map(lambda tup: tuple(map(hourtime_to_matrixminutes,tup)),
                                        map(op.itemgetter('start_datetime','end_datetime'),bay_normal_bookings)
                                        ))

        maximal_nonoverlaps_bayconfig = maximize_non_overlapping(bay_normal_intervals)

        remaining_daybookings_for_freebays = []
        for ix,bay_normal_interval in enumerate(bay_normal_intervals):
            if bay_normal_interval not in maximal_nonoverlaps_bayconfig:
                remaining_daybookings_for_freebays.append(bay_normal_bookings[ix])
            else:
                SERVICED_TRACKER_DDICT[bay_normal_bookings[ix]['day']]\
                                        [bay_normal_bookings[ix]['vehicle_category']] += 1
        remaining_bookings_for_freebays.extend(remaining_daybookings_for_freebays)

        for (start_minuteix,end_minuteix) in maximal_nonoverlaps_bayconfig:
            bay_matrix[reservedBayNumber][start_minuteix : end_minuteix + 1] = vehicule_enum_ordinal

    return bay_matrix,remaining_bookings_for_freebays


def final_half_greedy_bayconfig(bay_matrix,remaining_bookings_for_freebays):

    # print(bay_matrix)
    zero_filled_array = bay_matrix#[np.array(columns*[0]) for _ in range(rows)]
    # print(*remaining_bookings_for_freebays,sep="\n")
    # input()
    #for day_bookings in remaining_bookings_for_freebays:#grouped_entries.items():
    for timestamp_booking in remaining_bookings_for_freebays: #list(it.filterfalse(lambda b: b['isWalkIn'] or b['isSameDayBooking'], day_bookings)):
        start = timestamp_booking["start_datetime"]
        end = timestamp_booking["end_datetime"]
        duration = calculate_duration_in_minutes(start, end)
        # if int(duration) % 30 != 0:
        #     exit()

        start_minute = calculate_duration_in_minutes('07:00', start)

        # print(start_minute)
        # print(calculate_duration_in_minutes('07:00', '07:01'))
        # input()

        if timestamp_booking["vehicle_category"] is VehiculeCategory.CLASS2_TRUCK:
            if int(start_minute) >= 600:
                continue
        if timestamp_booking["vehicle_category"] is VehiculeCategory.CLASS1_TRUCK:
            if int(start_minute) >= 660:
                continue
        if timestamp_booking["vehicle_category"] is VehiculeCategory.COMPACT_CAR or timestamp_booking[
            "vehicle_category"] is VehiculeCategory.MEDIUM_CAR or timestamp_booking[
            "vehicle_category"] is VehiculeCategory.FULLSIZE_CAR:
            if int(start_minute) >= 690:
                continue

        type_veh = get_vehicule_ordinal_from_booking(timestamp_booking)
        flag = 0
        counter = 0
        for freeBayNUmber in range(5, 10):

            if flag == 0:
                initial_state = [row[:] for row in zero_filled_array]

                for i in range(int(duration)):
                    index = int(start_minute) + i
                    if zero_filled_array[freeBayNUmber][index] != 0:
                        zero_filled_array = initial_state
                        flag = 0
                        counter = 0
                        break
                    counter += 1
                    zero_filled_array[freeBayNUmber][index] = zero_filled_array[freeBayNUmber][index] + type_veh
                    flag = 1

        if flag != 0:

            SERVICED_TRACKER_DDICT[timestamp_booking['day']] \
                [timestamp_booking['vehicle_category']] += 1
    #print_2d_array(zero_filled_array)
    return zero_filled_array

def final_half_greedy_bayconfig2(bay_matrix,remaining_bookings_for_freebays):
    hourtime_to_matrixminutes = lambda hourtime: int((datetime.strptime(hourtime, "%H:%M") - datetime.strptime('07:00', "%H:%M")).total_seconds() // 60)

    for b in remaining_bookings_for_freebays:
        day = b['day']
        start = hourtime_to_matrixminutes(b["start_datetime"])
        end = hourtime_to_matrixminutes(b["end_datetime"])

        if b["vehicle_category"] is VehiculeCategory.CLASS2_TRUCK:
            if int(start) >= 600:
                continue
        if b["vehicle_category"] is VehiculeCategory.CLASS1_TRUCK:
            if int(start) >= 660:
                continue
        if b["vehicle_category"] is VehiculeCategory.COMPACT_CAR or b[
            "vehicle_category"] is VehiculeCategory.MEDIUM_CAR or b[
            "vehicle_category"] is VehiculeCategory.FULLSIZE_CAR:
            if int(start) >= 690:
                continue
        type_veh = get_vehicule_ordinal_from_booking(b)
        flag = 0
        for freeBayNUmber in range(5, 10):
            if np.all(bay_matrix[freeBayNUmber][start: end] == 0):
                bay_matrix[freeBayNUmber][start: end] = type_veh
                flag = 1
                break
        if flag != 0:
            SERVICED_TRACKER_DDICT[b['day']] \
                [b['vehicle_category']] += 1
    return bay_matrix

def calculate_duration_in_minutes(start_datetime_str, end_datetime_str):
    # Assuming datetime strings are in the format '%H:%M'
    format_str = '%H:%M'

    # Convert datetime strings to datetime objects
    start_datetime = datetime.strptime(start_datetime_str, format_str)
    end_datetime = datetime.strptime(end_datetime_str, format_str)

    # Calculate the difference
    duration = end_datetime - start_datetime

    # Get the total amount of minutes
    total_minutes = duration.total_seconds() / 60

    return total_minutes


def get_vehicule_ordinal_from_booking(booking : dict) -> int:
    vehicle_categoryenum: VehiculeCategory = booking['vehicle_category']
    return list(vehicle_categoryenum.__class__.__members__.values()).index(vehicle_categoryenum) + 1


def print_2d_array(arr):
    for row in arr:
        for element in row:
            print(element, end=" ")
        print()

def bay_matrix_to_list_of_intervals(bay_matrix : list[np.ndarray]) -> list[tuple[str,str]]:
    minutesIx_to_hourstime = lambda minutes_to_add: (datetime.strptime('07:00', "%H:%M") + timedelta(minutes=minutes_to_add)).strftime("%H:%M")
    res = []
    js_type_lookup = dict(zip(list(VehiculeCategory.__members__.values()),('C','M','F','C1','C2')))
    for bayNum, row in enumerate(bay_matrix,start=1):
        interval_js_body = dict()
        interval_js_body['bay'] = f'Bay {bayNum}'
        interval_js_body['reservations'] = []
        skipNext = False
        bayIntervals = []
        for minuteIx,typeNum in enumerate(row):
            if skipNext and int(typeNum) == 0:
                skipNext = False
                continue
            elif skipNext:
                continue

            if int(typeNum) != 0:
                vehicle_category_enum = list(VehiculeCategory.__members__.values())[int(typeNum)-1]
                skipNext = True
                bayIntervals.append((minuteIx , minuteIx + int(vehicle_category_enum.hours * 60)))
                interval_js_body['reservations'].append({
                    'start' : minutesIx_to_hourstime(minuteIx),
                    'end' : minutesIx_to_hourstime(minuteIx + int(vehicle_category_enum.hours * 60)) ,
                    'type' :  js_type_lookup[vehicle_category_enum]
                })
        res.append(interval_js_body)
    return res #yield from

if __name__ == '__main__':
    hourtime_to_matrixminutes = lambda hourtime: int(
        (datetime.strptime(hourtime, "%H:%M") - datetime.strptime('07:00', "%H:%M")).total_seconds() // 60)
    grouped_entries = parse_to_sorted_day_dict()

    for day in grouped_entries.keys():
        SERVICED_TRACKER_DDICT[day]

    rows = 10
    columns = 720
    zero_filled_array = [np.array(columns*[0]) for _ in range(rows)]

    # zero_filled_array = final_half_greedy_bayconfig(
    #     *initial_half_avg_optimal_bayconfig(zero_filled_array,
    #
    #                                         list(grouped_entries.values())[2]))


    print("DONE SETTING UP THE OPTIMAL INITIAL STATE")
    for day,day_bookings in grouped_entries.items():
        zero_filled_array = [np.array(columns * [0]) for _ in range(rows)]
        zero_filled_array = final_half_greedy_bayconfig2(
            *initial_half_avg_optimal_bayconfig(zero_filled_array,
                                                day_bookings))

        for timestamp_booking in filter(lambda b: b['isWalkIn'] or b['isSameDayBooking'], day_bookings):
            # start = timestamp_booking["start_datetime"]
            # end = timestamp_booking["end_datetime"]
            # duration = calculate_duration_in_minutes(start, end)
            #
            # start_minute = calculate_duration_in_minutes('07:00', start)

            start = hourtime_to_matrixminutes(timestamp_booking["start_datetime"])
            end = hourtime_to_matrixminutes(timestamp_booking["end_datetime"])

            duration = end - start + 1

            if timestamp_booking["vehicle_category"] is VehiculeCategory.CLASS2_TRUCK:
                if int(start) >= 600:
                    continue
            if timestamp_booking["vehicle_category"] is VehiculeCategory.CLASS1_TRUCK:
                if int(start) >= 660:
                    continue
            if timestamp_booking["vehicle_category"] is VehiculeCategory.COMPACT_CAR or timestamp_booking["vehicle_category"] is VehiculeCategory.MEDIUM_CAR or timestamp_booking["vehicle_category"] is VehiculeCategory.FULLSIZE_CAR:
                if int(start) >= 690:
                    continue
            type_veh = get_vehicule_ordinal_from_booking(timestamp_booking)
            flag = 0
            for reservedBayNumber in range(0,5):
                if type_veh != reservedBayNumber+1:
                    continue
                if flag == 0:
                    initial_state = [row[:] for row in zero_filled_array]
                    for i in range(int(duration)):
                        index = int(start) + 1#int(start_minute) + i
                        if zero_filled_array[reservedBayNumber][index] != 0:
                            zero_filled_array = initial_state
                            flag = 0
                            break
                        zero_filled_array[reservedBayNumber][index] = zero_filled_array[reservedBayNumber][
                                                                          index] + type_veh
                        flag = 1
            if flag != 0:
                SERVICED_TRACKER_DDICT[timestamp_booking['day']] \
                    [timestamp_booking['vehicle_category']] += 1
                continue
            flag = 0
            for freeBayNUmber in range(5, 10):
                if np.all(zero_filled_array[freeBayNUmber][start: end] == 0):
                    zero_filled_array[freeBayNUmber][start: end] = type_veh
                    flag = 1
                    break
            # for freeBayNUmber in range(5,10):
            #     if flag == 0:
            #         initial_state = [row[:] for row in zero_filled_array]
            #         for i in range(int(duration)):
            #             index = int(start_minute) + i
            #             if zero_filled_array[freeBayNUmber][index] != 0:
            #                 zero_filled_array = initial_state
            #                 flag = 0
            #                 break
            #             zero_filled_array[freeBayNUmber][index] = zero_filled_array[freeBayNUmber][index] + type_veh
            #             flag = 1
            if flag != 0:
                SERVICED_TRACKER_DDICT[timestamp_booking['day']] \
                    [timestamp_booking['vehicle_category']] += 1

        print(day)
        print(SERVICED_TRACKER_DDICT[day])
        print_2d_array(zero_filled_array)
        print()
        print(*bay_matrix_to_list_of_intervals(zero_filled_array),sep="\n")
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
