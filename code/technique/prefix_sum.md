### **Prefix Sum Technique: Explained Simply**

A **Prefix Sum** is a precomputed running total. `prefix[i]` stores the sum of all elements from the start up to index `i`. Once built (`O(n)`), the sum of *any* subarray can be answered in `O(1)`:

```
sum(i..j) = prefix[j] - prefix[i-1]
```

---

### **Why Use Prefix Sums?**
If you need range sums repeatedly (many queries, or checking every subarray), recomputing each sum costs `O(n)` per query. Precompute once, answer instantly.

---

### **How It Works**

```python
nums   = [3, 1, 4, 1, 5]
prefix = [0, 3, 4, 8, 9, 14]   # one extra leading 0 avoids edge cases

# sum of nums[1..3] (1 + 4 + 1 = 6):
# prefix[4] - prefix[1] = 9 - 3 = 6
```

```python
def build_prefix(nums):
    prefix = [0] * (len(nums) + 1)
    for i, x in enumerate(nums):
        prefix[i + 1] = prefix[i] + x
    return prefix
```

**Tip**: The leading `0` means `sum(i..j) = prefix[j+1] - prefix[i]` with no special case for `i = 0`.

---

### **The Killer Pattern: Prefix Sum + Hash Map**

Most Medium-level prefix sum problems combine the running sum with a hash map of *previously seen sums*. This answers: *"how many subarrays ending here have sum k?"*

#### **Subarray Sum Equals K (LC 560)**

```python
def subarray_sum(nums, k):
    count = 0
    running = 0
    seen = {0: 1}  # empty prefix
    for x in nums:
        running += x
        # if (running - k) was seen before, a subarray summing to k ends here
        count += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return count
```

**Key insight**: `running - previous_prefix = k` rearranges to `previous_prefix = running - k`. You're looking up the past in O(1) instead of rescanning it. This is structurally identical to how the Two Sum hash map works.

---

### **Variations**

1. **Prefix Product** — `Product of Array Except Self` (238): answer[i] = prefix product before i × suffix product after i.
2. **Prefix XOR** — same trick works because XOR is invertible: `xor(i..j) = prefix[j] ^ prefix[i-1]`.
3. **2D Prefix Sum** — for matrix range sums:
   `sum(region) = P[r2][c2] - P[r1-1][c2] - P[r2][c1-1] + P[r1-1][c1-1]`
4. **Difference Array** (the inverse): apply many range *updates* lazily, then one prefix-sum pass materializes the result. Used in "Car Pooling" / "Corporate Flight Bookings".

---

### **When to Reach for Prefix Sums**
- "Sum/product/XOR of a **subarray/range**"
- "**Count** subarrays with sum equal to / divisible by k"
- Many **range queries** on static data
- Many **range updates**, read once (difference array)

### **Complexity**
- Build: `O(n)` time, `O(n)` space
- Each range query: `O(1)`

### **Related LeetCode Problems**
- Range Sum Query - Immutable (303) — Easy
- Product of Array Except Self (238) — Medium
- Subarray Sum Equals K (560) — Medium
- Continuous Subarray Sum (523) — Medium
- Product of the Last K Numbers (1352) — Medium

---

## Practice Rep (25 min, pass/fail) — Timed Warmup

One problem, one timer, no notes: **560 Subarray Sum Equals K (Medium, 25 min)**.

This is *the* prefix-sum interview problem because it fuses the technique with a hashmap: count of subarrays = for each running sum `s`, how many earlier prefixes equal `s - k`. The load-bearing line is seeding `{0: 1}` — miss it and every subarray starting at index 0 vanishes.

**Pass:** accepted within 25 min, ≤2 submissions, O(n) single pass, and the `{0: 1}` seed was in your first draft (not patched in after a wrong answer).
**Fail:** timer expires, O(n²) nested loops, or the seed was debugged in rather than reasoned in.

Rotation (next warmup cycles): 238 → 523 → 525. From [leveling-system.json](../../leveling-system.json) Levels 1–2.
