# https://leetcode.com/problems/product-of-the-last-k-numbers

class ProductOfNumbers:

    def __init__(self):
        self.prefix_product = [1]

    def add(self, num: int) -> None:
        if num == 0:
            self.prefix_product = [1]
        else:
            self.prefix_product.append(self.prefix_product[-1]*num)

    def getProduct(self, k: int) -> int:
        if k >= len(self.prefix_product):
            return 0
        else:
            return self.prefix_product[-1] // self.prefix_product[-k-1]



# Your ProductOfNumbers object will be instantiated and called as such:
# obj = ProductOfNumbers()
# obj.add(num)
# param_2 = obj.getProduct(k)

"""
To solve this problem, we need to design a data structure that efficiently maintains a stream of integers and allows retrieving the product of the last `k` integers. The challenge is to handle zeros in the stream efficiently to avoid incorrect products and unnecessary computations.

### Approach
The key insight is to reset the product calculation whenever a zero is encountered. This allows us to efficiently compute the product of the last `k` elements by maintaining a list of prefix products. Here's the detailed approach:

1. **Prefix Products List**: Maintain a list where each element at index `i` represents the product of all elements from the start up to index `i` (excluding any elements before the last zero).
2. **Handling Zeros**: When a zero is encountered, reset the prefix products list to `[1]` to start fresh. This is because any product involving a zero will be zero, and we can ignore previous elements once a zero is added.
3. **Product Calculation**: For each query to get the product of the last `k` elements:
   - Check if the length of the prefix products list is less than `k + 1`. If true, it means there's a zero in the last `k` elements, so return 0.
   - Otherwise, compute the product using the prefix products list by dividing the product of all elements up to the current index by the product of elements up to the index `k` elements before the current index.

### Solution Code
```python
class ProductOfNumbers:

    def __init__(self):
        self.prefix_products = [1]

    def add(self, num: int) -> None:
        if num == 0:
            self.prefix_products = [1]
        else:
            self.prefix_products.append(self.prefix_products[-1] * num)

    def getProduct(self, k: int) -> int:
        if k >= len(self.prefix_products):
            return 0
        else:
            return self.prefix_products[-1] // self.prefix_products[-k - 1]
```

### Explanation
- **Initialization**: The `prefix_products` list starts with `[1]` to handle the initial product calculation correctly.
- **Adding Elements**: When a new number is added, if it is zero, the list is reset to `[1]`. Otherwise, the new product is calculated by multiplying the current number with the last product in the list and appending the result.
- **Retrieving Product**: For each query, if the number of elements since the last zero is less than `k`, return 0. Otherwise, use the prefix products to compute the product of the last `k` elements efficiently by dividing the appropriate elements in the prefix products list.

This approach ensures that we handle zeros efficiently and compute the product in constant time for each query, making the solution both optimal and easy to understand.
"""
