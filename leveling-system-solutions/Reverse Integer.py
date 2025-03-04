# https://leetcode.com/problems/reverse-integer/description/

class Solution:
    def reverse(self, x: int) -> int:
        is_negative = False

        if x < 0:
            is_negative = True
            x *= -1
        
        res = 0
        while x:
            res = (res * 10) + (x%10)
            x = x // 10
        
        if res > 2**31 -1:
            return 0

        return res * -1 if is_negative else res
        
