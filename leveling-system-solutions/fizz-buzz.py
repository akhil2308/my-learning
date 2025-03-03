# https://leetcode.com/problems/fizz-buzz/description/
class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        res = []

        for i in range(1,n+1):
            div_3 = i%3 == 0
            div_5 = i%5 == 0
            if div_3 and div_5:
                res.append("FizzBuzz")
            elif div_3:
                res.append("Fizz")
            elif div_5:
                res.append("Buzz")
            else:
                res.append(str(i))
        return res
