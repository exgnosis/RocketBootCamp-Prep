def mean(nums):
    if len(nums) == 0:
        raise ValueError("mean() of empty list is undefined")
    total = 0
    for n in nums:
        total += n
    return total / len(nums)

if __name__ == "__main__":
    print(mean([]))