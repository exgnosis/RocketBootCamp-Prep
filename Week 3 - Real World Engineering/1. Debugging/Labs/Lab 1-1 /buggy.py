# mean.py
def mean(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums)  # ZeroDivisionError if nums == []

if __name__ == "__main__":
    print(mean([]))  # Simulate a user path that passes empty data
