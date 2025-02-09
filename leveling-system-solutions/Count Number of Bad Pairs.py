# https://leetcode.com/problems/count-number-of-bad-pairs/description

class Solution:
    def countBadPairs_v1(self, nums: List[int]) -> int:
        res = 0
        nums_len = len(nums)
        for i in range(nums_len -1):
            for j in range(i+1, nums_len):
                if j - i != nums[j] - nums[i]:
                    res +=1

        return res
    
    def countBadPairs(self, nums: List[int]) -> int:
        n = len(nums)
        total_pairs = (n*(n-1)) // 2
        good = 0
        feq = {}
    
        for i,num in enumerate(nums):
            d = num - i

            if d in feq:
                good += feq[d]
                feq[d] +=1
            else:
                feq[d] = 1
        
        return total_pairs - good
