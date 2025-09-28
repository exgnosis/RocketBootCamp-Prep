# Lab 1-1: Debugging Python

## Buggy Code

- Run the following buggy Python code
- It is also in the file `buggy.py`
- The code is intended to calculate the statistical mean of a list  of numbers
- Confirm that it does work

```python
# mean.py
def mean(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums)  # ZeroDivisionError if nums == []

if __name__ == "__main__":
    print(mean([4,5,6]))  

```

- Replace the last two lines with this code and run it again

```python
if __name__ == "__main__":
    print(mean([4,5,6])) 
```

- At this point the fault might be obvious but is that the actual fault?

### Logging
- Add logging and check the context in the output (the first line)
- Code is in logging.py

```python
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
```

## Analysis
- The failure occurs when we divide by zero
- This is not the fault
- The fault is that the code does not check for invalid input


## Fix the fault
- Apply a fix + defensive error handling
- Add a guard and an informative exception or a fallback:
- The code is in fixed.py

```python
def mean(nums):
    if len(nums) == 0:
        raise ValueError("mean() of empty list is undefined")
    total = 0
    for n in nums:
        total += n
    return total / len(nums)

if __name__ == "__main__":
    print(mean([]))

```

- Note that the fix here doesn't seem to prevent the failure, but it has been converted into a raised condition that can be handed in a try block.
- We can't ensure that bad data won't be passed, but we now identify it and raise a condition rather than just crashing
