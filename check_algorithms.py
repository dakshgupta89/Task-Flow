"""Automated checks for the algorithms engine (Section 2, Task 7).

Run with: python3 check_algorithms.py
Uses plain if/else conditional statements (no assert, pytest, or unittest).
Prints one PASS/FAIL line per case and completes normally either way.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from algorithms import (
    insertion_sort,
    binary_search,
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)


def check(case_name, actual, expected):
    if actual == expected:
        print(f"PASS: {case_name}")
    else:
        print(f"FAIL: {case_name} — expected {expected}, got {actual}")


def run_all_checks():
    # 1. insertion_sort on an empty list leaves it empty
    empty = []
    insertion_sort(empty, "val")
    check("insertion_sort empty list", len(empty), 0)

    # 2. insertion_sort on a single-element list leaves it unchanged
    single = [{"val": 42, "name": "only"}]
    insertion_sort(single, "val")
    check(
        "insertion_sort single element",
        (len(single) == 1 and single[0]["val"] == 42),
        True,
    )

    # 3. binary_search finds a value at the first index
    sorted_list = [
        {"title": "apple"},
        {"title": "banana"},
        {"title": "cherry"},
        {"title": "date"},
        {"title": "elderberry"},
    ]
    result = binary_search(sorted_list, "apple", "title")
    check("binary_search first index", result, 0)

    # 4. binary_search finds a value at the last index
    result = binary_search(sorted_list, "elderberry", "title")
    check("binary_search last index", result, 4)

    # 5. binary_search finds a value in the middle
    result = binary_search(sorted_list, "cherry", "title")
    check("binary_search middle index", result, 2)

    # 6. binary_search returns -1 when target is absent
    result = binary_search(sorted_list, "grape", "title")
    check("binary_search not found", result, -1)

    # 7. insertion_sort_count leaves list correctly sorted and returns int > 0
    count_list = [
        {"title": "delta"},
        {"title": "alpha"},
        {"title": "charlie"},
        {"title": "bravo"},
    ]
    count_result = insertion_sort_count(count_list, "title")
    is_sorted = all(
        count_list[i]["title"] <= count_list[i + 1]["title"]
        for i in range(len(count_list) - 1)
    )
    check("insertion_sort_count sorts correctly", is_sorted, True)
    check(
        "insertion_sort_count returns int > 0",
        (type(count_result) == int and count_result > 0),
        True,
    )

    # 8. binary_search_count on a present value returns correct index and int > 0
    search_list = [
        {"title": "alpha"},
        {"title": "bravo"},
        {"title": "charlie"},
        {"title": "delta"},
        {"title": "echo"},
    ]
    bs_result = binary_search_count(search_list, "charlie", "title")
    check(
        'binary_search_count correct index',
        bs_result["index"],
        2,
    )
    check(
        'binary_search_count comparison_count is int > 0',
        (type(bs_result["comparison_count"]) == int and bs_result["comparison_count"] > 0),
        True,
    )

    # 9. linear_search_count on absent value returns index=-1 and count=len
    linear_list = [
        {"title": "apple"},
        {"title": "banana"},
        {"title": "cherry"},
    ]
    ls_result = linear_search_count(linear_list, "grape", "title")
    check(
        "linear_search_count absent index",
        ls_result["index"],
        -1,
    )
    check(
        "linear_search_count absent comparison_count equals length",
        ls_result["comparison_count"],
        3,
    )


if __name__ == "__main__":
    run_all_checks()
