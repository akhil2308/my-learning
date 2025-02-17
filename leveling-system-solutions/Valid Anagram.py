# https://leetcode.com/problems/valid-anagram/description/

class Solution:
    def isAnagram_v1(self, s: str, t: str) -> bool:
        return sorted(s) == sorted(t)

    def isAnagram_v2(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        s_d = {}
        t_d = {}
        for i in range(len(s)):
            if s_d.get(s[i]):
                s_d[s[i]] +=1
            else:
                s_d[s[i]] = 1

            if t_d.get(t[i]):
                t_d[t[i]] +=1
            else:
                t_d[t[i]] = 1
        

        """
        for i in range(len(s)):
                s_d[s[i]] = 1 + s_d.get(s[i],0)
                t_d[t[i]] = 1 + t_d.get(t[i],0)

        """
        return s_d == t_d

    
