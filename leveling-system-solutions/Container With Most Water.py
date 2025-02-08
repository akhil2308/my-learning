# https://leetcode.com/problems/container-with-most-water/description/

class Solution:
    def maxArea_v1(self, height: List[int]) -> int:
        height_len = len(height)
        max_area = 0
        for i in range(height_len):
            for j in range(i,height_len):
                if j == i:
                    continue
                
                temp_area = (j-i) * min(height[i],height[j])
                max_area = max(temp_area,max_area)

        return max_area
    
    def maxArea(self, height: List[int]) -> int:
        height_len = len(height)
        start, end = 0, height_len - 1
        max_area = 0
        while start < end:
            temp_area = (end-start) * min(height[start], height[end])
            max_area = max(temp_area,max_area)

            if height[start] < height[end]:
                start +=1
            else:
                end -=1
        return max_area
