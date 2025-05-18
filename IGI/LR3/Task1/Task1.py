import math
import ArcSin

def Task():
    """Solve Task1"""
    while True:
        while True:    
            try:
                x = float(input("Input x, |x|<1: "))
                if abs(x) > 1: print("Input Error. Value of 'x' from -1 to 1 not including -1 and 1")
                else: break
            except ValueError:
                print("Input Error")
        while True:    
            try:
                eps = float(input("Input eps: "))
                break
            except:
                print("Input Error")

        answer = ArcSin.arcsin_taylor(x, eps)
        print("{:<10} {:<10} {:<20} {:<20} {:<10}".format("x", "n", "F(x)", "Math F(x)", "eps"))
        print("{:<10} {:<10} {:<20} {:<20} {:<10}".format(x, answer[1], answer[0], math.asin(x), eps))
        
        while True:    
            c = input("Repeate?[Y/N]: ").upper()
            if c != "N" and c != "Y": print("Unknown command. Retry input")
            else: break
        if c == "N": break