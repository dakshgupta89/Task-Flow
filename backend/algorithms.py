"""Hand-rolled sorting and searching algorithms that power the backend endpoints.

No use of Python's built-in sorted()/list.sort() anywhere in this module.
"""

from typing import Any


def insertion_sort(records: list[dict[str, Any]], key: str) -> None:
    """Sort a list of dictionaries in place by the value at record[key].

    Uses the standard insertion-sort structure: starting from the second element,
    comparing against previous elements, and shifting to insert each into position.
    Mutates the list directly and returns None.
    """
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1
        while j >= 0 and records[j][key] > current[key]:
            records[j + 1] = records[j]
            j -= 1
        records[j + 1] = current
    return


def binary_search(
    sorted_records: list[dict[str, Any]], target_value: Any, key: str
) -> int:
    """Binary search on a list already sorted by key.

    Returns the index of a record whose record[key] == target_value, or -1 if not found.
    """
    low = 0
    high = len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_records[mid][key]
        if mid_val == target_value:
            return mid
        elif mid_val < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def linear_search(
    records: list[dict[str, Any]], target_value: Any, key: str
) -> int:
    """Linear scan baseline. Returns index of first match, or -1 if not found."""
    for i, record in enumerate(records):
        if record[key] == target_value:
            return i
    return -1


# ---------------------------------------------------------------------------
# Counting-wrapper versions for benchmarking (Section 2, Task 5).
# Same logic, same contracts, but each counts comparisons internally.
# ---------------------------------------------------------------------------


def insertion_sort_count(records: list[dict[str, Any]], key: str) -> int:
    """Sort records in place exactly as insertion_sort does; return comparison count."""
    comparisons = 0
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if records[j][key] > current[key]:
                records[j + 1] = records[j]
                j -= 1
            else:
                break
        records[j + 1] = current
    return comparisons


def binary_search_count(
    sorted_records: list[dict[str, Any]], target_value: Any, key: str
) -> dict[str, int]:
    """Binary search returning {"index": int, "comparison_count": int}."""
    comparisons = 0
    low = 0
    high = len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        mid_val = sorted_records[mid][key]
        if mid_val == target_value:
            return {"index": mid, "comparison_count": comparisons}
        elif mid_val < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return {"index": -1, "comparison_count": comparisons}


def linear_search_count(
    records: list[dict[str, Any]], target_value: Any, key: str
) -> dict[str, int]:
    """Linear search returning {"index": int, "comparison_count": int}."""
    comparisons = 0
    for i, record in enumerate(records):
        comparisons += 1
        if record[key] == target_value:
            return {"index": i, "comparison_count": comparisons}
    return {"index": -1, "comparison_count": comparisons}
