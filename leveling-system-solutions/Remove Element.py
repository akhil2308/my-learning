# https://leetcode.com/problems/remove-element/description/

class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        nums_len = len(nums)
        index = 0
        for i in range(nums_len):
            if nums[i] != val:
                nums[index] = nums[i]
                index +=1
        return index
