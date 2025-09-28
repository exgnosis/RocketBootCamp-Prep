# Lab 1-3: Debugging Python

## Buggy Code

- The following is some buggy Python code.
- Review the code and the run it to see the error
- The code is in the file buggy.py

```python
def subtotal(line_items):
    total = 0.0
    for item in line_items:
        total += item["unit_price"] * item["qty"]
    return total



def load_items():
    return [{"price": 10.0, "qty": 2}, {"price": 5.0, "qty": 1}]

if __name__ == "__main__":
    items = load_items()
    print("Subtotal:", subtotal(items))   
```

## Analysis

- Define the failure & reproduce
  - Run python buggy.py. 
  - Capture exception (likely KeyError: 'unit_price')
- Gather data & challenge assumptions 
  - What does pricing.subtotal expect? 
  - What does load_items() produce? 
  - Check both functions in terms of their inputs and outputs
- Structured decomposition
  - Sketch a tiny fault tree: 
  - “Wrong/failed subtotal”
    - subtotal( expects unit_price
    - load_items()) supplies price 
    - root cause: contract mismatch.

## Logging
- Add logging to investigate hypothesis

```python
import logging
logging.basicConfig(level=logging.DEBUG)


def subtotal(line_items):
    logging.debug("Computing subtotal for items=%s", line_items)
    total = 0.0
    for item in line_items:
        total += item["unit_price"] * item["qty"]
    return total



def load_items():
    return [{"price": 10.0, "qty": 2}, {"price": 5.0, "qty": 1}]

if __name__ == "__main__":
    items = load_items()
    print("Subtotal:", subtotal(items))  

```

## Conclusion
- load_items() is not providing the data in the format that subtotal() is expecting
- Fix the load_items() to provide the correct format
- The solution is the file solution.py
