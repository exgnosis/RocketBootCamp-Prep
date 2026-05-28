def mean(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums)

if __name__ == "__main__":
    print(mean([]))
