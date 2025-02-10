# https://leetcode.com/problems/clear-digits/description/
class Solution:
    def clearDigits_v1(self, s: str) -> str:
        char_index = []
        s = list(s)
        for i in range(len(s)):
            if s[i].isdigit():
                if char_index:
                    s[char_index[-1]] = ""
                    char_index.pop()
                s[i] = ""
            else:
                char_index.append(i)

        return "".join(s)
    
    
    def clearDigits(self, s: str) -> str:
        char_index = []
        s = list(s)
        for i in range(len(s)):
            if s[i].isdigit():
                char_index.pop()
            else:
                char_index.append(s[i])
        return "".join(char_index)
