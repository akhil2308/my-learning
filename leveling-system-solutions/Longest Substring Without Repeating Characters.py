# https://leetcode.com/problems/longest-substring-without-repeating-characters/description/

class Solution:
    def lengthOfLongestSubstring_v1(self, s: str) -> int:
        max_len = 0
        start_index = 0
        s_len = len(s)
        while start_index < s_len:
            temp = ""
            for i in range(start_index, s_len):
                if s[i] in temp:
                    break
                temp = temp + s[i]
            start_index += 1
            temp_len = len(temp)
            if temp_len > max_len:
                max_len = temp_len
        
        return max_len

    def lengthOfLongestSubstring(self, s: str) -> int:
        s_len = len(s)
        char_set = set()
        left = 0
        max_s = 0
        
        for right in range(s_len):
            if s[right] not in char_set:
                # if no duplicates are present
                char_set.add(s[right])
                max_s = max(max_s, right - left +1)
            else:
                # if duplicates are present
                while s[right] in char_set:
                    char_set.remove(s[left])
                    left +=1
                char_set.add(s[right])
                
        return max_s
