class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner          # public
        self.__balance = balance    # private

    def deposit(self, amount):
        self.__balance += amount

    def withdraw(self, amount):
        if amount <= self.__balance:
            self.__balance -= amount
            print("Withdrawn amount:", amount)
            print("Remaining balance:", self.__balance)
        else:
            print("Insufficient balance")
            print("Available balance:", self.__balance)

    def get_balance(self):
        return self.__balance


# Object creation
acc = BankAccount("Ujwal", 5000)

# User input
amount = int(input("Enter the amount to withdraw: "))

# Correct method call
acc.withdraw(amount)
