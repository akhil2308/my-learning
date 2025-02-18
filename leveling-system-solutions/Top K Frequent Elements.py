# https://leetcode.com/problems/top-k-frequent-elements/description/

import heapq

class Solution:
    
    def topKFrequent_v1(self, nums: List[int], k: int) -> List[int]:
        counter  = {}
        for i in nums:
            counter[i] = 1 + counter.get(i,0)
        temp = [[k,v] for k,v in counter.items()]
        temp.sort(key= lambda x: x[1])

        res = []
        while len(res) < k:
            res.append(temp.pop()[0])
        
        return res

    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        counter  = {}
        for i in nums:
            counter[i] = 1 + counter.get(i,0)
        heap = []
        for key,value in counter.items():
            heapq.heappush(heap,[value,key])
            if len(heap) >k:
                heapq.heappop(heap)
        
        res = []
        for value,key in heap:
            res.append(key)
        return res
