### **Backtracking: Explained Simply**

**Backtracking** is systematic trial and error: build a candidate solution one choice at a time, and the moment a choice can't lead to a valid solution, **undo it** (backtrack) and try the next option. It's DFS over a "decision tree" of choices.

---

### **Why Use Backtracking?**
When the problem asks for **all** solutions (or any valid one) and there's no formula — permutations, combinations, subsets, board puzzles — you must explore. Backtracking explores every possibility but **prunes** dead branches early instead of generating everything and filtering.

---

### **The Universal Template**

Every backtracking problem is this skeleton with different blanks:

```python
def backtrack(path, choices):
    if is_solution(path):          # 1. Base case
        results.append(path[:])    #    (copy! path gets mutated)
        return
    for choice in choices:         # 2. Iterate options at this level
        if not is_valid(choice):   # 3. Prune invalid branches
            continue
        path.append(choice)        # 4. Choose
        backtrack(path, next_choices)  # 5. Explore
        path.pop()                 # 6. Un-choose (the "backtrack")
```

**The choose → explore → un-choose triple is the entire technique.** Steps 4 and 6 must be perfect mirrors of each other.

---

### **The Three Canonical Problems**

#### **1. Subsets (LC 78)** — *include or skip each element*

```python
def subsets(nums):
    results = []
    def backtrack(start, path):
        results.append(path[:])          # every node is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)       # i+1: no element reuse
            path.pop()
    backtrack(0, [])
    return results
```

#### **2. Permutations (LC 46)** — *order matters, use each element once*

```python
def permute(nums):
    results = []
    used = [False] * len(nums)
    def backtrack(path):
        if len(path) == len(nums):
            results.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path)
            path.pop()
            used[i] = False
    backtrack([])
    return results
```

#### **3. Combination Sum (LC 39)** — *reuse allowed, prune by remaining target*

```python
def combination_sum(candidates, target):
    results = []
    candidates.sort()                    # enables pruning
    def backtrack(start, path, remaining):
        if remaining == 0:
            results.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break                    # prune: sorted, so rest are bigger too
            path.append(candidates[i])
            backtrack(i, path, remaining - candidates[i])  # i, not i+1: reuse ok
            path.pop()
    backtrack(0, [], target)
    return results
```

---

### **Key Decisions to Identify per Problem**
1. **What is a "choice"?** (an element, a cell, a letter)
2. **When is the path a complete solution?** (length reached, target hit)
3. **What makes a branch invalid?** — pruning is where the real speedup lives
4. **Can choices repeat?** — controls `start` vs `i + 1` vs a `used` array
5. **Duplicates in input?** — sort, then skip `nums[i] == nums[i-1]` at the same level

### **When to Reach for Backtracking**
- "Return **all** permutations / combinations / subsets / partitions"
- Grid/board puzzles: N-Queens, Sudoku, Word Search
- Constraint satisfaction with no greedy/DP structure

### **Complexity**
Exponential by nature — `O(2^n)` for subsets, `O(n!)` for permutations. Pruning reduces the constant, not the class. If n > ~20, backtracking alone is probably the wrong tool.

### **Related LeetCode Problems**
- Subsets (78) — Medium
- Permutations (46) — Medium
- Combination Sum (39) — Medium
- Letter Combinations of a Phone Number (17) — Medium
- Word Search (79) — Medium
- Palindrome Partitioning (131) — Medium
- N-Queens (51) — Hard
