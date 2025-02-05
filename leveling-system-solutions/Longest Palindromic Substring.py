# https://leetcode.com/problems/longest-palindromic-substring/

class Solution:
    def longestPalindrome_v1(self, s: str) -> str:
        res = ""
        s_len = len(s)
        for i in range(s_len):
            for j in range(i,s_len+1):
                temp = s[i:j]
                if temp == temp[::-1]:
                    if len(temp) > len(res):
                        res = temp
            if len(res) >= s_len - i:
                return res
        return res

    def longestPalindrome(self, s: str) -> str:
      # Expand Around Center approach 
        res = ""
        s_len = len(s)
        for i in range(s_len):
            # odd
            start, end = i,i
            while start >=0 and end< s_len and s[start] == s[end]:
                start -=1
                end +=1
            
            odd_pal = s[start+1: end]

            #even
            start, end = i, i+1
            while start >=0 and end< s_len and s[start] == s[end]:
                start -=1
                end +=1
            
            even_pal = s[start+1: end]

            res = max(res, odd_pal, even_pal, key=len)
        
        return res
