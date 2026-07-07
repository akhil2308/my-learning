### **Heaps (Priority Queues): Explained Simply**

A **heap** is a tree stored in an array that keeps the smallest (min-heap) or largest (max-heap) element at the top at all times. You don't get full sorting — you get *instant access to the extreme element*, with cheap inserts and removals.

| Operation | Cost |
|---|---|
| Peek min/max | `O(1)` |
| Push | `O(log n)` |
| Pop min/max | `O(log n)` |
| Build from list (`heapify`) | `O(n)` |

---

### **Python: `heapq` Essentials**

`heapq` is **min-heap only**. For a max-heap, negate values.

```python
import heapq

nums = [5, 1, 8, 3]
heapq.heapify(nums)          # in-place, O(n)
heapq.heappush(nums, 2)
smallest = heapq.heappop(nums)   # 1
top = nums[0]                    # peek without popping

# Max-heap trick: negate on the way in and out
max_heap = [-x for x in [5, 1, 8]]
heapq.heapify(max_heap)
largest = -heapq.heappop(max_heap)   # 8

# Tuples sort by first element — attach priorities
heapq.heappush(tasks, (priority, task_id, payload))
```

---

### **The Three Core Patterns**

#### **1. Top-K — keep a heap of size k**
**Problem**: Kth largest element in an array (LC 215).

```python
def kth_largest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)              # min-heap of the k largest so far
    for x in nums[k:]:
        if x > heap[0]:
            heapq.heapreplace(heap, x)   # pop min, push x — one operation
    return heap[0]
```

**Key insight (counterintuitive)**: For the k **largest**, use a **min**-heap of size k. The heap's minimum is the "bar to beat" — anything smaller can't be in the top k. `O(n log k)` beats sorting's `O(n log n)` when k is small. Same pattern: Top K Frequent Elements (347), K Closest Points (973).

#### **2. K-Way Merge**
**Problem**: Merge k sorted lists (LC 23).

```python
def merge_k_lists(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    result = []
    while heap:
        val, li, ei = heapq.heappop(heap)
        result.append(val)
        if ei + 1 < len(lists[li]):
            heapq.heappush(heap, (lists[li][ei + 1], li, ei + 1))
    return result
```

**Key insight**: The heap holds one candidate per list — the overall smallest is always among the heads. This is exactly how external merge sort and LSM-tree compaction (RocksDB) work.

#### **3. Two Heaps — Streaming Median (LC 295)**
Maintain a max-heap of the smaller half and a min-heap of the larger half, kept balanced. The median is always at the top of one (or both) heaps. Also the backbone of scheduling problems (Meeting Rooms II — min-heap of end times).

---

### **When to Reach for a Heap**
- "**K-th** largest/smallest", "**top K**", "K closest"
- Merging **multiple sorted** sources
- Repeatedly need the min/max of a **changing** collection (schedulers, Dijkstra)
- **Streaming** data where sorting everything is wasteful

### **Heap vs Sort vs QuickSelect**
- Need everything ordered once → **sort** `O(n log n)`
- Need top-k from a stream / k ≪ n → **heap** `O(n log k)`
- Need k-th element once, array fits in memory → **quickselect** `O(n)` average

### **Related LeetCode Problems**
- Kth Largest Element (215) — Medium
- Top K Frequent Elements (347) — Medium
- K Closest Points to Origin (973) — Medium
- Merge k Sorted Lists (23) — Hard
- Find Median from Data Stream (295) — Hard
- Meeting Rooms II (253) — Medium

---

## Practice Rep (25 min, pass/fail) — Timed Warmup

One problem, one timer, no notes: **973 K Closest Points to Origin (Medium, 25 min)**.

The senior move: a **max-heap of size k** (negate distances in Python's min-heap `heapq`), push-then-pop past k — O(n log k), not "sort everything" O(n log n). Skip the sqrt; comparing squared distances orders identically.

**Pass:** accepted within 25 min, ≤2 submissions, heap bounded at size k, no sqrt, and you can state the complexity difference vs sorting without pausing.
**Fail:** timer expires, `sorted(points, key=...)[:k]` (correct but it's not the rep — the rep is the bounded heap), or negation bugs found by submitting.

Rotation (next warmup cycles): 621 Task Scheduler → 703 (Easy, 15 min) → 347 → 295 (Hard, two-heaps — allow 35 min). From [leveling-system.json](../../leveling-system.json) Levels 1 & 4.
