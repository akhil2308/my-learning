### **Binary Search: Explained Simply**

**Binary Search** repeatedly halves a *sorted* (or monotonic) search space. Each comparison eliminates half the candidates, giving `O(log n)` instead of `O(n)`.

The big unlock: binary search is not about sorted arrays — it's about **monotonic conditions**. If you can write a function `condition(x)` that is `False, False, ..., False, True, True, ..., True` over the search space, you can binary search for the boundary.

---

### **The One Template to Memorize**

Most binary search bugs come from juggling `left <= right` vs `left < right`, `mid ± 1`, etc. This "find the first True" template solves nearly everything:

```python
def binary_search(lo, hi, condition):
    """Returns the smallest x in [lo, hi] where condition(x) is True."""
    while lo < hi:
        mid = (lo + hi) // 2
        if condition(mid):
            hi = mid        # mid might be the answer, keep it
        else:
            lo = mid + 1    # mid is definitely not the answer
    return lo
```

**Why it can't infinite-loop**: `mid` is always `< hi` (floor division), so `hi = mid` always shrinks the range, and `lo = mid + 1` always shrinks it too.

---

### **Examples**

#### **1. Classic — Find Target in Sorted Array**

```python
def search(nums, target):
    lo = binary_search(0, len(nums) - 1, lambda i: nums[i] >= target)
    return lo if nums[lo] == target else -1
```

`nums[i] >= target` is False for everything left of target, True from target onward — a monotonic condition.

#### **2. First and Last Position (LC 34)**
- First: smallest `i` where `nums[i] >= target`
- Last: (smallest `i` where `nums[i] > target`) minus 1

Same template, two conditions.

#### **3. Binary Search on the Answer — Koko Eating Bananas (LC 875)**
**Problem**: Find the minimum eating speed `k` to finish all piles within `h` hours.

```python
import math

def min_eating_speed(piles, h):
    def can_finish(k):
        return sum(math.ceil(p / k) for p in piles) <= h

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if can_finish(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

**Key insight**: The array isn't sorted — the *answer space* is monotonic. If speed `k` works, every speed `> k` also works. "Minimize the maximum / maximize the minimum" problems are almost always this pattern (Split Array Largest Sum, Capacity to Ship Packages).

#### **4. Rotated Sorted Array (LC 33)**
At every `mid`, at least one half is properly sorted. Check which half is sorted, check if target lies in it, discard accordingly.

---

### **When to Reach for Binary Search**
- Input is **sorted** or rotated-sorted
- "Find **minimum/maximum** x such that..." (search on answer)
- `O(n)` is too slow and the check function is monotonic
- **Peak finding** — condition can be local (`nums[i] > nums[i+1]`) as long as it's monotonic-ish

### **Common Pitfalls**
- Off-by-one in boundaries → use the single template above, always
- `(lo + hi) // 2` can overflow in other languages (not Python)
- Forgetting the "not found" check after the loop

### **Complexity**
- Time: `O(log n)` — or `O(n log(answer_range))` for search-on-answer
- Space: `O(1)`

### **Related LeetCode Problems**
- Binary Search (704) — Easy
- Find First and Last Position (34) — Medium
- Search in Rotated Sorted Array (33) — Medium
- Koko Eating Bananas (875) — Medium
- Find Peak Element (162) — Medium
- Median of Two Sorted Arrays (4) — Hard
- Split Array Largest Sum (410) — Hard

---

## Practice Rep (25 min, pass/fail) — Timed Warmup

One problem, one timer, no notes: **875 Koko Eating Bananas (Medium, 25 min)** — search-on-answer, the variant interviews actually test. The array you're searching is imaginary: candidate speeds 1..max(piles), monotonic feasibility check `hours(speed) <= h`.

**Pass:** accepted within 25 min, ≤2 submissions, using the one template from this doc (`lo < hi`, `hi = mid` on feasible), and you can say out loud what makes the predicate monotonic.
**Fail:** timer expires, an infinite loop from mixing templates, or `ceil` division hand-rolled wrong (`-(-p // speed)` or `math.ceil` — pick one and know it).

Rotation (next warmup cycles): 33 → 162 → 34 → 4 (Hard — allow 35 min, once the Mediums are clean).
