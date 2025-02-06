# https://leetcode.com/problems/reverse-words-in-a-string/

class Solution:
    def reverseWords_v1(self, s: str) -> str:
        # best solution
        res = ""
        temp  = ""
        for i in s:
            # skip spaces 
            if i == " " and temp == "":
                continue

            if i != " ":
                temp = temp + i

            else:
                if not res:
                    res = temp
                else:
                    res = temp + " " + res
                temp = ""
        if temp and res:
            res = temp + " " + res
        elif not res:
            res = temp
        return res

    def reverseWords_v2(self, s: str) -> str:
        res = []
        temp  = ""
        for i in s:
            # skip spaces 
            if i != " ":
                temp = temp + i
            else:
                if temp:
                    res.insert(0, temp)
                    temp = ""

        if temp:
            res.insert(0, temp)
        return " ".join(res)
    
    def reverseWords(self, s: str) -> str:
        return " ".join(s.split()[::-1])
