from bisect import bisect_left, insort
#import numpy as np

# def insert_sorted(intervals, new_interval):
#     start_time = new_interval[0]
#     index = bisect_left(intervals, start_time)
#
#     insort(intervals, new_interval)
#
# def remove_sorted(intervals, target_interval):
#     start_time = target_interval[0]
#     index = bisect_left(intervals, start_time)
#
#     for i in range(index, len(intervals)):
#         if intervals[i] == target_interval:
#             del intervals[i]
#             break
#


def maximize_non_overlapping(intervals):
    # Sort intervals by end time
    intervals.sort(key=lambda x: x[1])

    result = []
    current_end = float('-inf')

    for interval in intervals:
        start, end = interval

        # If the current interval does not overlap with the previous one, add it to the result
        if start > current_end:
            result.append(interval)
            current_end = end

    return result

# intervals = [(1, 5),(1,3),(4,8),(9,11), (6, 10), (3, 8), (12, 15), (15,16),(16, 18), (20, 25)]
# maximal_non_overlapping = maximize_non_overlapping(intervals)
