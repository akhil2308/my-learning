# https://leetcode.com/problems/3sum/

class Solution:
    def threeSum_v1(self, nums: List[int]) -> List[List[int]]:
        res = []
        nums = sorted(nums)
        nums_len = len(nums)
        for i in range(nums_len):
            for j in range(i+1, nums_len):
                for k in range(j+1, nums_len):
                    team = [nums[i], nums[j], nums[k]]
                    if sum(team) == 0 and team not in res:
                        res.append(team)
        return res
    
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        res = []
        nums = sorted(nums)
        for i in range(len(nums)):
            
            #skip duplicates
            if i>0 and nums[i] == nums[i-1]:
                continue

            left, right = i + 1, len(nums) -1

            while left < right:
                temp = nums[i] +  nums[left] +  nums[right]

                if temp < 0 :
                    left +=1
                elif temp > 0:
                    right -=1
                else:
                    res.append([nums[i],nums[left],nums[right]])
                    
                    # since both the values have been added
                    left +=1

                    # remove duplicates
                    while left < right and nums[left] == nums[left-1]:
                        left +=1


        return res
