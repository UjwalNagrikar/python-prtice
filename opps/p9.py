class student :
    def __init__(self, name,grade , persentage, mark,team):
        self.name = name
        self.grade = grade
        self.persentage = persentage
        self.mark = mark
        self.team = team

    def display(self):
        print("Name : ", self.name)
        print("Grade : ", self.grade)
        print("Persentage : ", self.persentage)
        print("Mark : ", self.mark)
        print("Team : ", self.team)

    
s1 = student("Ujwal", "A", 90, 85, "Team A")
s1.display()
