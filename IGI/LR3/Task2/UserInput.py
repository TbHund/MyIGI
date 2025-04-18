def user_input(list):
    """Input list int numbers"""
    number = 0
    while number <= 100:
        while True: 
            try:
                number = int(input("Input number(>100 is end of input): "))
                break
            except ValueError:
                print("Input Error. number is integer")
        list.append(number)