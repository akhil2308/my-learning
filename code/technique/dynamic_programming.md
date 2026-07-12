### **Dynamic Programming: Explained Simply**

**Dynamic Programming (DP)** = recursion + never solving the same subproblem twice. If a brute-force recursion keeps re-answering identical questions, cache the answers (memoization) or build them bottom-up in a table (tabulation).

DP applies when a problem has:
1. **Overlapping subproblems** — the recursion tree revisits the same states
2. **Optimal substructure** — the best answer is composed of best answers to smaller inputs

---

### **The Practical Recipe**

1. **Define the state**: What does `dp[i]` (or `dp[i][j]`) *mean* in plain English? This is 80% of the work.
2. **Write the recurrence**: How does `dp[i]` depend on smaller states?
3. **Base cases**: What are the trivially known answers?
4. **Order**: Memoize top-down (easy, natural) or tabulate bottom-up (faster, enables space optimization).
5. **Optimize space**: If `dp[i]` only needs `dp[i-1]` and `dp[i-2]`, keep two variables instead of an array.

---

### **Top-Down vs Bottom-Up (Climbing Stairs, LC 70)**

```python
# Top-down: brute force recursion + @cache. Easiest to derive.
from functools import cache

@cache
def climb(n):
    if n <= 2:
        return n
    return climb(n - 1) + climb(n - 2)

# Bottom-up + space optimized: two rolling variables.
def climb(n):
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b if n > 1 else a
```

**Tip**: When stuck, write the plain recursion first, confirm it's correct, then slap `@cache` on it. Convert to bottom-up only if needed.

---

### **The Core Patterns (learn these, most problems are variants)**

#### **1. Linear DP — House Robber (LC 198)**
State: `dp[i]` = max money using houses `0..i`.

```python
def rob(nums):
    prev, curr = 0, 0
    for x in nums:
        prev, curr = curr, max(curr, prev + x)  # skip house i, or rob it
    return curr
```

#### **2. Unbounded Knapsack — Coin Change (LC 322)**
State: `dp[a]` = fewest coins to make amount `a`.

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

#### **3. Two-Sequence DP — Longest Common Subsequence (LC 1143)**
State: `dp[i][j]` = LCS of `s1[:i]` and `s2[:j]`.

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

Edit Distance (72) is this same grid with different transitions.

#### **4. Grid DP — Unique Paths (62)**: `dp[i][j] = dp[i-1][j] + dp[i][j-1]`
#### **5. Subsequence DP — Longest Increasing Subsequence (300)**: `dp[i]` = LIS ending at `i` (`O(n²)`, or `O(n log n)` with patience sorting)

---

### **How to Spot DP**
- "Count the number of ways to..."
- "Minimum/maximum cost/path/length to reach..."
- "Can you partition/form/reach..." (decision problems)
- Choices at each step + brute force is exponential + inputs ≤ ~few thousand

### **DP vs Greedy vs Backtracking**
- **Greedy**: local best choice is provably globally safe → no table needed
- **DP**: must consider multiple choices, but subproblems repeat → cache
- **Backtracking**: need to enumerate actual solutions, subproblems don't collapse

### **Related LeetCode Problems**
- Climbing Stairs (70) — Easy
- House Robber (198) — Medium
- Coin Change (322) — Medium
- Longest Increasing Subsequence (300) — Medium
- Longest Common Subsequence (1143) — Medium
- Edit Distance (72) — Medium
- Partition Equal Subset Sum (416) — Medium

---

## Practice Rep (25 min, pass/fail) — Timed Warmup

One problem, one timer, no notes: **322 Coin Change (Medium, 25 min)**.

Unbounded knapsack, bottom-up: `dp[amount] = min(dp[amount - coin] + 1)` over coins, `dp[0] = 0`, infinity elsewhere, answer is `dp[target]` or −1. State the recurrence in English *before* typing — "fewest coins for amount a = 1 + best over each last-coin choice."

**Pass:** accepted within 25 min, ≤2 submissions, recurrence written as a comment before the loop, O(amount × coins) tabulation (no naive recursion TLE).
**Fail:** timer expires, memoized recursion that blows the stack on amount=10⁴ (know why tabulation dodges it), or the −1 case patched in after a wrong answer.

Rotation (next warmup cycles): 198 → 300 → 416 → 139. From [leveling-system.json](../../leveling-system.json) Level 5.
