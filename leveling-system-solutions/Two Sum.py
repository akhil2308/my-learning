# https://leetcode.com/problems/two-sum/description

class Solution:
    def twoSum_v1(self, nums: List[int], target: int) -> List[int]:
        n = len(nums)
        for i in range(n):
            for j in range(i+1,n):
                if nums[i] + nums[j] == target:
                    return [i,j]
        return []

    
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        hash_map = {}

        for i in range(len(nums)):
            temp = target - nums[i]
            if hash_map.get(temp) != None:
                return [hash_map[temp],i]
            
            hash_map[nums[i]] = i
        
        return []
