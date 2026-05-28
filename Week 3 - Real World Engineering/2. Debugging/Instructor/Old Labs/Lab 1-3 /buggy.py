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
