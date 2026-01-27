try:
    list = [10, 20, 30, 60]
    print(list[7])
except IndexError:
    print("Index out of range! Please access a valid index.")
    print("list length ", len(list))
except ValueError:
    print("Invalid value encountered!")
    