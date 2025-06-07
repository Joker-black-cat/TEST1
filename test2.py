def two_sum(nums, target):
    """
    时间复杂度: O(n)
    空间复杂度: O(n)
    """
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return []
