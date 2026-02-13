class student:
    def __init__(self, name, rollno,team):
        self.name = name
        self.team = team
        self.rollno = rollno

    def display(self):
        print("Name:", self.name)
        print("Roll No:", self.rollno)
        print("Team:", self.team)

s1 = student("Ujwal", 101, "Team A")
s1.display()