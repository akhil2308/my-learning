# https://leetcode.com/problems/trapping-rain-water/?envType=daily-question&envId=2025-02-10

class Solution:
    def trap(self, height: List[int]) -> int:
        if not height:
            return 0
        
        left, right = 0, len(height) -1
        left_max, right_max = height[left], height[right]
        water = 0
        while left< right:
            if height[left] < height[right]:
                left +=1
                left_max = max(left_max, height[left])

                water += left_max - height[left]
            else:
                right -=1
                right_max = max(right_max, height[right])
                water += right_max - height[right]
        
        return water


"""
Below is an explanation of how the two‑pointer solution executes step by step. We'll use a concrete example to illustrate the flow. Suppose our input is:

```python
height = [4, 2, 0, 3, 2, 5]
```

### Initial Setup

- **Pointers:**  
  - `left = 0` (points to the first element, value 4)  
  - `right = 5` (points to the last element, value 5)

- **Maximums:**  
  - `left_max = height[0] = 4`  
  - `right_max = height[5] = 5`

- **Accumulated Water:**  
  - `water = 0`

The main loop runs while `left < right`.

---

### Iteration by Iteration

#### **Iteration 1:**
- **State Before:**  
  - `left = 0`, `right = 5`  
  - `height[left] = 4`, `height[right] = 5`  
  - `left_max = 4`, `right_max = 5`  
  - `water = 0`
  
- **Comparison:**  
  Since `height[left] (4) < height[right] (5)`, we move the **left pointer**.
  
- **Actions:**  
  - Increment `left` by 1 → now `left = 1`  
  - Update `left_max = max(left_max, height[1]) = max(4, 2) = 4`  
  - Calculate water at index 1: `left_max - height[1] = 4 - 2 = 2`  
  - Add to `water`: `water = 0 + 2 = 2`

#### **Iteration 2:**
- **State Before:**  
  - `left = 1`, `right = 5`  
  - `height[left] = 2`, `height[right] = 5`  
  - `left_max = 4`, `right_max = 5`  
  - `water = 2`
  
- **Comparison:**  
  `height[left] (2) < height[right] (5)`, so again move the **left pointer**.
  
- **Actions:**  
  - Increment `left` by 1 → now `left = 2`  
  - Update `left_max = max(4, height[2]) = max(4, 0) = 4`  
  - Calculate water at index 2: `left_max - height[2] = 4 - 0 = 4`  
  - Add to `water`: `water = 2 + 4 = 6`

#### **Iteration 3:**
- **State Before:**  
  - `left = 2`, `right = 5`  
  - `height[left] = 0`, `height[right] = 5`  
  - `left_max = 4`, `right_max = 5`  
  - `water = 6`
  
- **Comparison:**  
  Since `height[left] (0) < height[right] (5)`, move the **left pointer**.
  
- **Actions:**  
  - Increment `left` by 1 → now `left = 3`  
  - Update `left_max = max(4, height[3]) = max(4, 3) = 4`  
  - Calculate water at index 3: `left_max - height[3] = 4 - 3 = 1`  
  - Add to `water`: `water = 6 + 1 = 7`

#### **Iteration 4:**
- **State Before:**  
  - `left = 3`, `right = 5`  
  - `height[left] = 3`, `height[right] = 5`  
  - `left_max = 4`, `right_max = 5`  
  - `water = 7`
  
- **Comparison:**  
  `height[left] (3) < height[right] (5)`, so move the **left pointer**.
  
- **Actions:**  
  - Increment `left` by 1 → now `left = 4`  
  - Update `left_max = max(4, height[4]) = max(4, 2) = 4`  
  - Calculate water at index 4: `left_max - height[4] = 4 - 2 = 2`  
  - Add to `water`: `water = 7 + 2 = 9`

#### **Iteration 5:**
- **State Before:**  
  - `left = 4`, `right = 5`  
  - `height[left] = 2`, `height[right] = 5`  
  - `left_max = 4`, `right_max = 5`  
  - `water = 9`
  
- **Comparison:**  
  Again, `height[left] (2) < height[right] (5)`, so move the **left pointer**.
  
- **Actions:**  
  - Increment `left` by 1 → now `left = 5`  
  - Update `left_max = max(4, height[5]) = max(4, 5) = 5`  
  - Calculate water at index 5: `left_max - height[5] = 5 - 5 = 0`  
  - Add to `water`: `water` remains 9

At this point, `left` equals `right` (both are 5), so the loop terminates.

---

### Final Return
- The algorithm returns `water = 9`, which is the total amount of trapped rain water.

---

### Recap of the Key Ideas

- **Two Pointers:**  
  One pointer (`left`) moves from the start and the other (`right`) from the end.  
- **Left_max and Right_max:**  
  These track the highest wall seen so far from the left and right sides, respectively.
- **Water Calculation:**  
  At each step, we add the difference between the current pointer’s maximum (left_max or right_max) and the current height. This difference is the water that can be trapped at that index.
- **Decision to Move a Pointer:**  
  We move the pointer from the side that currently has the lower height because that side is the limiting factor for the water level at that point.

This step-by-step execution should help you see how the algorithm progresses through the array and accumulates the total trapped water.
"""
