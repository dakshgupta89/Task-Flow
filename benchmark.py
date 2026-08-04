"""Benchmark script for the algorithms engine (Section 2, Tasks 5 & 6).

Run with: python3 benchmark.py

Generates synthetic task dictionaries using the exact same fields the endpoints
operate on (title, priority, due_date) at three sizes: 10, 500, and 3000.
Runs the counting-wrapper functions and prints comparison counts.

Saves results to results.txt.
"""

import sys
import os
import random
import string

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from algorithms import (
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
    insertion_sort,
)

PRIORITIES = ["low", "medium", "high"]
DUE_DATES = ["today", "tomorrow", "next monday", "next friday", "monday", None, None, None]


def generate_tasks(n):
    """Generate n synthetic task dicts with fields matching the real task model."""
    tasks = []
    for i in range(n):
        title = "Task-" + str(i).zfill(5) + "-" + "".join(
            random.choices(string.ascii_lowercase, k=4)
        )
        tasks.append({
            "id": i,
            "title": title,
            "priority": random.choice(PRIORITIES),
            "due_date": random.choice(DUE_DATES),
            "status": "pending",
            "project_id": 1,
        })
    return tasks


def run_benchmark():
    sizes = [10, 500, 3000]
    results = []

    print("=" * 75)
    print("TaskFlow Algorithms Benchmark — Comparison Counts")
    print("=" * 75)
    print()

    for size in sizes:
        tasks = generate_tasks(size)

        # --- Insertion sort (by priority_rank) ---
        sort_records = [dict(t, priority_rank={"low": 1, "medium": 2, "high": 3}[t["priority"]]) for t in tasks]
        sort_comparisons = insertion_sort_count(sort_records, "priority_rank")

        # --- Binary search (on title-sorted index) ---
        search_index = [{"id": t["id"], "title": t["title"]} for t in tasks]
        insertion_sort(search_index, "title")  # sort first (not counted in search cost)

        # Search for a title that exists (middle element)
        target_idx = len(search_index) // 2
        target_title = search_index[target_idx]["title"]
        bs_result = binary_search_count(search_index, target_title, "title")

        # Search for a title that does NOT exist
        bs_miss = binary_search_count(search_index, "ZZZZNONEXISTENT", "title")

        # --- Linear search (on unsorted index) ---
        linear_index = [{"id": t["id"], "title": t["title"]} for t in tasks]
        ls_result = linear_search_count(linear_index, target_title, "title")

        # Linear search miss
        ls_miss = linear_search_count(linear_index, "ZZZZNONEXISTENT", "title")

        line = f"Size: {size:>5}"
        results.append(line)
        print(line)
        print(f"  insertion_sort (by priority):  {sort_comparisons:>10} comparisons")
        print(f"  binary_search (hit):           index={bs_result['index']:>6}, comparisons={bs_result['comparison_count']:>4}")
        print(f"  binary_search (miss):          index={bs_miss['index']:>6}, comparisons={bs_miss['comparison_count']:>4}")
        print(f"  linear_search (hit):           index={ls_result['index']:>6}, comparisons={ls_result['comparison_count']:>4}")
        print(f"  linear_search (miss):          index={ls_miss['index']:>6}, comparisons={ls_miss['comparison_count']:>4}")
        print()

    print("=" * 75)
    print("Note: insertion_sort is O(n²) worst-case. At n=3000, expect ~4.5M comparisons.")
    print("      binary_search is O(log n) — even at 3000, only ~12 comparisons.")
    print("      linear_search is O(n) — at 3000, up to 3000 comparisons per search.")
    print("=" * 75)

    # Save to results file
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.txt")
    with open(results_path, "w") as f:
        f.write("TaskFlow Algorithms Benchmark Results\n")
        f.write("=" * 75 + "\n\n")
        for size in sizes:
            tasks = generate_tasks(size)
            random.seed(42)  # note: actual numbers vary by seed; the shape is what matters

        # Re-run deterministically for the file
        random.seed(42)
        for size in sizes:
            tasks = generate_tasks(size)

            sort_records = [dict(t, priority_rank={"low": 1, "medium": 2, "high": 3}[t["priority"]]) for t in tasks]
            sort_comparisons = insertion_sort_count(sort_records, "priority_rank")

            search_index = [{"id": t["id"], "title": t["title"]} for t in tasks]
            insertion_sort(search_index, "title")

            target_idx = len(search_index) // 2
            target_title = search_index[target_idx]["title"]
            bs_result = binary_search_count(search_index, target_title, "title")
            bs_miss = binary_search_count(search_index, "ZZZZNONEXISTENT", "title")

            linear_index = [{"id": t["id"], "title": t["title"]} for t in tasks]
            ls_result = linear_search_count(linear_index, target_title, "title")
            ls_miss = linear_search_count(linear_index, "ZZZZNONEXISTENT", "title")

            f.write(f"Size: {size}\n")
            f.write(f"  insertion_sort (by priority):  {sort_comparisons} comparisons\n")
            f.write(f"  binary_search (hit):           index={bs_result['index']}, comparisons={bs_result['comparison_count']}\n")
            f.write(f"  binary_search (miss):          index={bs_miss['index']}, comparisons={bs_miss['comparison_count']}\n")
            f.write(f"  linear_search (hit):           index={ls_result['index']}, comparisons={ls_result['comparison_count']}\n")
            f.write(f"  linear_search (miss):          index={ls_miss['index']}, comparisons={ls_miss['comparison_count']}\n\n")

    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    run_benchmark()
