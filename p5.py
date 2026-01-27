try:
    user = "admin"
    password = "admin123"

    if len(password) < 6:
        raise ValueError("Username must be at least 6 characters long.")
    
    elif password is None or user is None:
        raise TypeError("Username or password cannot be None.")

    elif password == "" or user == "":
        raise ValueError("Username or password cannot be empty.")
    
    input_user = input("Enter username: ")
    input_password = input("Enter password: ")

    if input_user != user or input_password != password:
        raise PermissionError("Invalid username or password.")
    else:
        print("Login successful!")

except PermissionError as pe:
    print(f"PermissionError: {pe}")