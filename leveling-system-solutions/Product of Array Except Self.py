# https://leetcode.com/problems/product-of-array-except-self/description/

class Solution:
    def productExceptSelf_v1(self, nums: List[int]) -> List[int]:
        res = []
        for i in range(len(nums)):
            product = 1
            for j in range(len(nums)):
                if i == j:
                    continue
                product = product * nums[j]
            res.append(product)
        return res
    
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        res = [0] * len(nums)
        product = 1
        zero_count = 0
        for i in nums:
            if i == 0:
                zero_count +=1
                continue
            product = product * i
        
        # more than 2 0's all the values in list will be 0
        if zero_count > 1: 
            return res
    
        for i in range(len(nums)):
            if zero_count:
                if nums[i]:
                    res[i] = 0
                else:
                    res[i] = product
            else:
                res[i] = product//nums[i]
        
        return res
