data = {"BTC": 45000, "ETH": 3200}
def get_price():
    try:
        coin = input("Enter cryptocurrency symbol (e.g., BTC, ETH): ").upper()
        price = data[coin]
        print(f"The current price of {coin} is ${price}")
    except KeyError:
        print("Error: Cryptocurrency symbol not found. Please enter a valid symbol.")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
get_price()