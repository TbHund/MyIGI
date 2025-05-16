#Task4
#Лабораторная работа №4. Работа с файлами, классами, сериализаторами,регулярными выражениями и стандартными библиотеками.
#Version: 1.0
#Dev: Богуцкий Тимофей Сергеевич
#Date: 02.05.2025

from matplotlib.colors import CSS4_COLORS
import rhombus
import re

if __name__ == "__main__":
     file = "Task4/MyFigure.png"
     while True:
        print("CREATING RHOMBUS")
        while True:    
            try:
                a = float(input("Input A diagonal: "))
                if a <= 0: print("Input Error. Value must be positive")
                else: break
            except ValueError:
                print("Input Error")
        while True:    
            try:
                b = float(input("Input B diagonal: "))
                if b <= 0: print("Input Error. Value must be positive")
                else: break
            except ValueError:
                print("Input Error")

        while True:
            color = input("Input color (Format: 'red', 'green', '#FF00FF'): ").strip()
            
            if color.lower() in CSS4_COLORS:
                color = color.lower()
                break
            
            if re.match(r'^#[0-9a-fA-F]{6}$', color):
                break
            print("Incorrecr color! Retry.")     

        name = input("Input name of shape: ")

        shape = rhombus.Rhombus(a, b, color, name)
        shape.draw(file)

        while True:    
            c = input("Repeate?[Y/N]: ").upper()
            if c != "N" and c != "Y": print("Unknown command. Retry input")
            else: break
        if c == "N": break