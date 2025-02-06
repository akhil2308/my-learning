# https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/

class Solution:
    def removeDuplicates_v1(self, nums: List[int]) -> int:
        # refrece
        nums_len = len(nums)
        result = []
        result.insert(0,nums[0])
        result_index = 0
        for i in range(nums_len):
            if result[result_index] != nums[i]:
                result_index +=1
                result.insert(result_index, i)
        nums = result
        return result_index + 1

    def removeDuplicates(self, nums: List[int]) -> int:
        nums_len = len(nums)
        result_index = 0
        for i in range(nums_len):
            if nums[result_index] != nums[i]:
                result_index +=1
                nums[result_index] = nums[i]
        return result_index + 1
