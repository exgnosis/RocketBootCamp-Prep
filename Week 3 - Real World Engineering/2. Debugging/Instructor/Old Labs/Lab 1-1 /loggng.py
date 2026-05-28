import logging
logging.basicConfig(level=logging.DEBUG)

def mean(nums):
    logging.debug("Computing mean for nums=%s (len=%d)", nums, len(nums))
    total = 0
    for n in nums:
        total += n
    return total / len(nums)

if __name__ == "__main__":
    print(mean([]))