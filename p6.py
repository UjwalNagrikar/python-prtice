try:
    price = None

    if price is None:
        raise TypeError("Price cannot be None.")
    
except TypeError as te:
    print(f"TypeError: {te}")