"""
Benchmark: Linear Search vs Binary Search (with Quick Sort)

Generates a large dataset of contacts and compares the runtime
of linear search against quick sort + binary search.
"""

import time
import random
import string


# --- Re-use the same algorithms from app.py ---

def quick_sort(arr, key='name'):
    """Quick Sort implementation for sorting contacts by a given key."""
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    pivot_val = pivot[key].lower() if isinstance(pivot[key], str) else pivot[key]

    left = []
    middle = []
    right = []

    for item in arr:
        item_val = item[key].lower() if isinstance(item[key], str) else item[key]
        if item_val < pivot_val:
            left.append(item)
        elif item_val == pivot_val:
            middle.append(item)
        else:
            right.append(item)

    return quick_sort(left, key) + middle + quick_sort(right, key)


def binary_search(sorted_contacts, target, key='name'):
    """Binary Search on a sorted list of contacts by a given key."""
    low = 0
    high = len(sorted_contacts) - 1

    if isinstance(target, str):
        target = target.lower()

    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_contacts[mid][key]
        if isinstance(mid_val, str):
            mid_val = mid_val.lower()

        if mid_val == target:
            return sorted_contacts[mid]
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return None


# --- Search implementations ---

def linear_search(contacts, target_name):
    """O(n) linear search through the contact list."""
    target_lower = target_name.lower()
    for contact in contacts:
        if contact['name'].lower() == target_lower:
            return contact
    return None


def binary_search_with_sort(contacts, target_name):
    """Quick Sort the list, then Binary Search for the target."""
    sorted_contacts = quick_sort(contacts, key='name')
    return binary_search(sorted_contacts, target_name, key='name')


def find_contact_by_id_linear(contacts, target_id):
    """O(n) linear search by id."""
    for contact in contacts:
        if contact['id'] == target_id:
            return contact
    return None


def find_contact_by_id_binary(contacts, target_id):
    """Quick Sort by id, then Binary Search."""
    sorted_contacts = quick_sort(contacts, key='id')
    return binary_search(sorted_contacts, target_id, key='id')


# --- Data generation ---

def random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def generate_contacts(n):
    contacts = []
    for i in range(1, n + 1):
        contacts.append({
            'id': i,
            'name': random_name(),
            'email': f'{random_name(5)}@example.com'
        })
    return contacts


# --- Benchmark ---

def benchmark(func, *args, iterations=100):
    """Run a function multiple times and return average time in ms."""
    start = time.perf_counter()
    for _ in range(iterations):
        func(*args)
    elapsed = time.perf_counter() - start
    return (elapsed / iterations) * 1000  # convert to ms


def benchmark_repeated_binary(sorted_contacts, targets, key='name'):
    """Perform many binary searches on an already-sorted list."""
    for t in targets:
        binary_search(sorted_contacts, t, key=key)


def benchmark_repeated_linear(contacts, targets):
    """Perform many linear searches."""
    for t in targets:
        linear_search(contacts, t)


def main():
    sizes = [1000, 5000, 10000, 50000]

    # ============================================================
    # PART 1: Single-query comparison (sort + search vs linear)
    # ============================================================
    print("=" * 70)
    print("PART 1: Single Query — Linear Search vs Quick Sort + Binary Search")
    print("=" * 70)

    for size in sizes:
        contacts = generate_contacts(size)
        target_contact = contacts[int(size * 0.9)]
        target_name = target_contact['name']
        target_id = target_contact['id']

        iterations = max(10, 500 // (size // 1000))

        print(f"\n--- {size:,} contacts ({iterations} iterations each) ---")

        linear_time = benchmark(linear_search, contacts, target_name, iterations=iterations)
        binary_time = benchmark(binary_search_with_sort, contacts, target_name, iterations=iterations)

        print(f"  Linear Search:              {linear_time:.4f} ms avg")
        print(f"  Quick Sort + Binary Search: {binary_time:.4f} ms avg")

    # ============================================================
    # PART 2: Pre-sorted repeated searches (the real advantage)
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 2: Repeated Queries on Pre-Sorted Data (sort once, search many)")
    print("  This is where Binary Search shows its O(log n) advantage.")
    print("=" * 70)

    num_queries = 1000

    for size in sizes:
        contacts = generate_contacts(size)

        # Pick random targets from the dataset
        targets = [random.choice(contacts)['name'] for _ in range(num_queries)]

        # Pre-sort once
        sort_start = time.perf_counter()
        sorted_contacts = quick_sort(contacts, key='name')
        sort_time_ms = (time.perf_counter() - sort_start) * 1000

        # Time: linear search x num_queries
        lin_start = time.perf_counter()
        benchmark_repeated_linear(contacts, targets)
        lin_total = (time.perf_counter() - lin_start) * 1000

        # Time: binary search x num_queries (on pre-sorted list)
        bin_start = time.perf_counter()
        benchmark_repeated_binary(sorted_contacts, targets, key='name')
        bin_total = (time.perf_counter() - bin_start) * 1000

        speedup = lin_total / bin_total if bin_total > 0 else float('inf')

        print(f"\n--- {size:,} contacts, {num_queries} search queries ---")
        print(f"  Quick Sort (one-time cost):   {sort_time_ms:.4f} ms")
        print(f"  Linear Search (total):        {lin_total:.4f} ms")
        print(f"  Binary Search (total):        {bin_total:.4f} ms")
        print(f"  Binary Search Speedup:        {speedup:.2f}x faster")

    print("\n" + "=" * 70)
    print("CONCLUSION: Binary Search is O(log n) per query vs O(n) for linear.")
    print("After the one-time O(n log n) sort, repeated searches are far faster.")
    print("=" * 70)


if __name__ == '__main__':
    main()
