list = [10, 20, 30, 60, 'a']
try:
    total = 0
    for i in list:
        total += i
    print("Total sum:", total)
except ValueError:
    print("ValueError: Non-numeric value encountered in the list.")
    print("List contents:", list)

except TypeError:
    print("TypeError: Cannot add different data types. Please ensure all elements are numbers.")
    print("List contents:", list)