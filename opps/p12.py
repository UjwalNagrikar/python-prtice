# Question 1:
# Create a class Account with a private variable balance.
# Add methods deposit(), withdraw(), and display() to manage the balance.

class Account:
    def __init__(self, balance):
        self.__balance = balance

    def deposit(self, amount):
        self.__balance += amount
        print("Deposited Amount:", amount)
        print("Total Balance:", self.__balance)

    def withdraw(self, amount):
        if self.__balance >= amount:
            self.__balance -= amount
            print("Withdrawn Amount:", amount)
            print("Total Balance:", self.__balance)
        else:
            print("Insufficient Balance")

    def display(self):
        print("Total Balance:", self.__balance)


a1 = Account(10000)
a1.deposit(5000)
a1.withdraw(2000)
a1.display()


# Question 2:
# Create a class Bank with method get_rate().
# Create a child class SBI that overrides get_rate() and returns 6.5.

class Bank:
    def get_rate(self):
        return 0


class SBI(Bank):
    def get_rate(self):
        return 6.5


s1 = SBI()
print("Rate is:", s1.get_rate())


# Question 3:
# Create a class Person with name and age.
# Create a child class Teacher that adds subject.
# Display all details.

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display(self):
        print("Name:", self.name)
        print("Age:", self.age)


class Teacher(Person):
    def __init__(self, name, age, subject):
        super().__init__(name, age)
        self.subject = subject

    def display(self):
        super().display()
        print("Subject:", self.subject)


t1 = Teacher("Ujwal", 19, "Quant Finance")
t1.display()


# Question 4:
# Write a custom function to calculate x raised to the power of x.

def power(x):
    return x ** x


result = power(5)
print("5 raised to the power of 5 is:", result)
