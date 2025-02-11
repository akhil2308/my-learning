# https://leetcode.com/problems/remove-all-occurrences-of-a-substring/description

class Solution:
    def removeOccurrences_v1(self, s: str, part: str) -> str:
        n = len(s)
        p_n = len(part)
        index = 0
        while index < n:
            if part == s[index:index+p_n]:
                s = s[:index] + s[index+p_n:]
                index = 0
            else:
                index +=1
        return s
    
    def removeOccurrences(self, s: str, part: str) -> str:
        n = len(s)
        p_n = len(part)

        while True:
            index = s.find(part)
            if index == -1:
                break
            s = s[:index] + s[index+p_n:]
        return s
