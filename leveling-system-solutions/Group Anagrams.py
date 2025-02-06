# https://leetcode.com/problems/group-anagrams/description/

class Solution:
    def groupAnagrams_v1(self, strs: List[str]) -> List[List[str]]:
        # better solution
        res = {}
        for i in strs:
            sorted_str = ''.join(sorted(i))
            res.setdefault(sorted_str,[]).append(i)
        
        return list(res.values())
    
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        # solution with defaultdict
        res = defaultdict(list)
        for i in strs:
            sorted_str = ''.join(sorted(i))
            res[sorted_str].append(i)
        
        return list(res.values())
