import binarycheck
import decorator

def Task():
    """Solve Task3"""
    dec_check = decorator.decorator(binarycheck.check)
    while True:
        if(dec_check(input("Input str: ").upper())):
            print("Your str is binary number")
        else:
            print("Your str isn't binary number")

        while True:    
            c = input("Repeate?[Y/N]: ").upper()
            if c != "N" and c != "Y": print("Unknown command. Retry input")
            else: break
        if c == "N": break