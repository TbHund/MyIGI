def Task():
    """Solve Task5"""
    while True:
        ls = []
        proizvedenie = 1
        sum = 0
        sum_index = 0

        while True:    
            try:
                number = int(input("Input size of list:"))
                break
            except ValueError:
                print("Input Error. Size is integer number")

        print("There must be at least TWO ZEROs in your input!")
        counter_for_zero = 0
        for i in range(number):
            while True:    
                try:
                    number = float(input("Input element of list:"))
                    if number == 0:
                        counter_for_zero += 1
                    break
                except ValueError:
                    print("Input Error. Elem is floating number")

            ls.append(number)

        if ls.count(0) < 2:
            continue

        copy = ls
        first_zero = next(i for i, x in enumerate(copy) if x == 0.0)
        last_zero = len(copy) - 1 - next(i for i, x in enumerate(reversed(copy)) if x == 0.0)

        print(first_zero)
        print(last_zero)

        for index, elem in enumerate(ls):
            if index % 2 == 0: 
                proizvedenie *= elem
            if (index > first_zero and index < last_zero):
                sum += elem

        print("List: ", ls)
        print("{:<20} {:<20}".format("proizvedenie", "sum"))
        print("{:<20} {:<20}".format(proizvedenie, sum))

        while True:    
            c = input("Repeate?[Y/N]: ").upper()
            if c != "N" and c != "Y": print("Unknown command. Retry input")
            else: break
        if c == "N": break