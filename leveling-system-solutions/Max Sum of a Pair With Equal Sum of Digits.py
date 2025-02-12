# https://leetcode.com/problems/max-sum-of-a-pair-with-equal-sum-of-digits

class Solution:
    def maximumSum(self, nums: List[int]) -> int:
        pair_dict = {}
        max_res = -1
        
        for num in nums:
            temp_num = num
            res = 0
            while temp_num:
                res += temp_num%10
                temp_num = temp_num//10
            
            if pair_dict.get(res):
                pre_num = pair_dict[res]
                current_num = pre_num + num
                max_res = max(max_res, current_num)
                pair_dict[res] = max(pre_num, num)
            else:
                pair_dict[res] = num
        
        return max_res
