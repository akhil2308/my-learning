# https://leetcode.com/problems/count-number-of-bad-pairs/description

import heapq

class Solution:
    def minOperations_v1(self, nums: List[int], k: int) -> int:
        nums.sort()
        itter_count = 0
        while len(nums) > 1 and nums[0] < k: 
            if nums[0] < nums[1]:
                temp = nums[0] * 2 + nums[1]
            else:
                temp = nums[1] * 2 + nums[0]
            nums = nums[2:]
            nums.append(temp)
            itter_count +=1
            nums.sort()

        return itter_count

    def minOperations_v2(self, nums: List[int], k: int) -> int:
        heapq_nums = []
        count = 0
        for i in nums:
            heapq.heappush(heapq_nums, i)

        while len(heapq_nums) > 1 and heapq_nums[0] < k:
            x = heapq.heappop(heapq_nums)
            y = heapq.heappop(heapq_nums)
            temp = x*2 + y
            heapq.heappush(heapq_nums,temp)
            count +=1
        
        return count 
    
    def minOperations(self, nums: List[int], k: int) -> int:
        heapq.heapify(nums)
        count = 0
        
        while len(nums) > 1 and nums[0] < k:
            x = heapq.heappop(nums)
            y = heapq.heappop(nums)
            temp = x*2 + y
            heapq.heappush(nums,temp)
            count +=1
        
        return count 
