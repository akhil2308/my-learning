# https://leetcode.com/problems/longest-consecutive-sequence/description

class Solution:
    def longestConsecutive_v1(self, nums: List[int]) -> int:
        """
        this solution is O(n log n) since sort will take this)
        """
        if not nums:
            return 0
        nums.sort()
        d = []
        current = nums[0]
        c_max = 1
        index = 1

        while index < len(nums):
            if current+1 == nums[index]:
                current +=1
                c_max +=1
            else:
                if current == nums[index]:
                    index +=1
                    continue
                current = nums[index]
                d.append(c_max)
                c_max = 1
            index +=1

        d.append(c_max)
        return max(d)   
    
    def longestConsecutive(self, nums: List[int]) -> int:
        nums = set(nums)
        longest_count = 0

        for i in nums:
            if i-1 not in nums: # this means its the start of the sequence
                current_num = i
                current_count = 1

                while current_num+1 in nums: # find all the seq of the current_num
                    current_num += 1
                    current_count += 1

                longest_count = max(longest_count,current_count)                  
        
        return longest_count
