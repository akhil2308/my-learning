# https://leetcode.com/problems/text-justification/description/

class Solution:
    def divide_into_even_parts(self, total, parts):
        # Calculate the base value for each part
        base = total // parts
        # Calculate the remainder to distribute the extra
        remainder = total % parts
        
        # Create a list with the base value for all parts
        result = [base] * parts
        # Distribute the remainder by adding 1 to the first 'remainder' parts
        for i in range(remainder):
            result[i] += 1
        
        return result
      
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        res = []
        temp_list = []
        temp_count = 0
        for i in range(len(words)):
            # get a list which is <= maxWidth
            current_count = temp_count + len(words[i])
            if temp_count <= maxWidth and current_count + len(temp_list)  <= maxWidth:
                temp_count = current_count
                temp_list.append(words[i])
            else:
                temp = ""
                if len(temp_list) > 1:
                    spaces = self.divide_into_even_parts(maxWidth - temp_count, len(temp_list) - 1)
                    for j in range(len(temp_list) - 1):
                        temp = temp + temp_list[j] + " " * spaces[j]
                    temp = temp + temp_list[-1]
                else:
                    temp = temp_list[0] + " " * (maxWidth - temp_count)
                res.append(temp)
                temp_list = [words[i]]
                temp_count = len(words[i])
            
            if i == len(words) -1:
                temp = ""
                spaces = maxWidth - temp_count
                for j in range(len(temp_list) -1):
                    temp = temp + temp_list[j] + " "
                    spaces -= 1
                temp = temp + temp_list[-1] + " " * spaces
                res.append(temp)
        return res
