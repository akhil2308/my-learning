# https://leetcode.com/problems/design-a-number-container-system/description/

import collections
import heapq

class NumberContainers:

    def __init__(self):
        self.container = {}
        self.number_index = collections.defaultdict(list)
        
    def change(self, index: int, number: int) -> None:
        self.container[index] = number
        
        # heapq -> {number: [index]}
        heapq.heappush(self.number_index[number],index)
        

    def find(self, number: int) -> int:
        # if number not present
        if number not in self.number_index:
            return -1
        heap = self.number_index[number]
        
        # delete indexes which no longer are present at the number
        while heap and self.container.get(heap[0]) != number:
            heapq.heappop(heap)
        
        return heap[0] if heap else -1
