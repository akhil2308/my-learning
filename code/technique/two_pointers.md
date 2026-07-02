### **Two Pointers Technique: Explained Simply**

The **Two Pointers Technique** uses two index variables that move through a data structure (usually an array or string) in a coordinated way. Instead of checking every pair with nested loops (`O(n²)`), the pointers move intelligently based on conditions, reducing time to `O(n)`.

---

### **Why Use Two Pointers?**
Brute force pair-checking recomputes work you already know. If the array is sorted (or can be sorted), the relationship between the two pointer values tells you which pointer to move — you never need to revisit a pair.

---

### **Three Common Patterns**

1. **Opposite Ends (Converging):** `left` starts at 0, `right` at the end. Move toward each other.
   - Use for: pair sums in sorted arrays, palindromes, container problems.
2. **Same Direction (Fast/Slow):** Both start at the beginning, one moves faster.
   - Use for: removing duplicates in-place, cycle detection in linked lists.
3. **Two Sequences:** One pointer per array.
   - Use for: merging sorted arrays, comparing strings.

---

### **Examples**

#### **1. Opposite Ends — Two Sum II (Sorted Array)**
**Problem**: Find two numbers that add up to `target` in a sorted array.

```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        current = nums[left] + nums[right]
        if current == target:
            return [left, right]
        elif current < target:
            left += 1   # need a bigger sum
        else:
            right -= 1  # need a smaller sum
    return []
```

**Key insight**: Because the array is sorted, a too-small sum means only moving `left` can help. This is the same logic behind `3Sum` (fix one element, two-pointer the rest) and `Container With Most Water` (always move the shorter wall).

#### **2. Fast/Slow — Remove Duplicates from Sorted Array (In-Place)**

```python
def remove_duplicates(nums):
    if not nums:
        return 0
    slow = 0  # last position of the unique region
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1
```

**Key insight**: `slow` marks the boundary of the "result so far"; `fast` scans ahead. This "write pointer / read pointer" pattern also solves `Remove Element` and `Move Zeroes`.

#### **3. Fast/Slow — Linked List Cycle (Floyd's Algorithm)**

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

---

### **When to Reach for Two Pointers**
- The array is **sorted** (or sorting it doesn't break the problem)
- You need **pairs/triplets** satisfying a condition
- You need **in-place** modification with O(1) space
- The problem mentions **palindromes** or **reversal**

### **Two Pointers vs Sliding Window**
Sliding window is a special case of same-direction two pointers where the region *between* the pointers (the window) is what matters. Use sliding window when the answer is about a **contiguous subrange**; use plain two pointers when the answer is about **the elements at the pointers themselves**.

---

### **Complexity**
- Time: `O(n)` — each pointer moves at most `n` times
- Space: `O(1)`

### **Related LeetCode Problems**
- Two Sum II (167) — Easy
- Valid Palindrome (125) — Easy
- Remove Duplicates from Sorted Array (26) — Easy
- 3Sum (15) — Medium
- Container With Most Water (11) — Medium
- Trapping Rain Water (42) — Hard
