# https://leetcode.com/problems/valid-palindrome/description/
import re

class Solution:
    def isPalindrome_v1(self, s: str) -> bool:
        #remove special char
        s = re.sub('[^A-Za-z0-9]','',s)
        s = s.lower()
        return s == s[::-1]
    
    def isPalindrome(self, s: str) -> bool:
        # two pointer
        if not s:
            return True
        
        start, end = 0, len(s) -1

        while start < end:
            if not s[start].isalnum():
                start +=1
                continue

            if not s[end].isalnum():
                end -=1
                continue
            
            if s[start].lower() == s[end].lower():
                start +=1
                end -=1
            else:
                return False
                
        
        return True
