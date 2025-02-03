# https://leetcode.com/problems/longest-common-prefix/description/

class Solution:
    def longestCommonPrefix_v1(self, strs: List[str]) -> str:
        min_word = strs[0]
        for i in strs[1:]:
            if  len(i) < len(min_word):
                min_word = i

        prefix = ""
        for i in range(len(min_word)):
            for j in strs:
                if j[:i+1] != min_word[:i+1]:
                    return prefix
            prefix = min_word[:i+1]
        return prefix

    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        prefix = strs[0]
        for s in strs[1:]:
            while not s.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix
