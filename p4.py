try:
    num = int(input("Enter a amount : "))
    bal = 10000
    if num > bal:
        raise ValueError("Insufficient balance for the withdrawal.")
    else:
        print("widrawal amount =", num)
        print("Withdrawal successful!")
        print(f"Available balance = {bal - num}")

except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("Thank you for using our ATM service.")