class student :
    def __init__(self, name, mark):
        self.name = name
        self.mark = mark

    def display(self):
        print("Name : ", self.name)
        print("Mark : ", self.mark)

s1 = student("Ujwal", 85)
s1.display()