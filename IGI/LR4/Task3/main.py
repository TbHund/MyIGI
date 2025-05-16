#Task3
#Лабораторная работа №4. Работа с файлами, классами, сериализаторами,регулярными выражениями и стандартными библиотеками.
#Version: 1.0
#Dev: Богуцкий Тимофей Сергеевич
#Date: 02.05.2025

import ArcSin
import numpy as np
import math
import matplotlib.pyplot as plt

if __name__ == "__main__":
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

        ArcSinClass = ArcSin.ArcsinTaylor(x, eps)
        print("{:<10} {:<10} {:<20} {:<20} {:<10}".format("x", "n", "F(x)", "Math F(x)", "eps"))
        print("{:<10} {:<10} {:<20} {:<20} {:<10}".format(x, ArcSinClass.n, ArcSinClass.sum, math.asin(x), eps))

        print("Среднее значение членов ряда: ", ArcSinClass.list_mean)
        print("Медиана членов ряда: ", ArcSinClass.list_median)
        print("Дисперсия членов ряда: ", ArcSinClass.list_variance)
        print("Стандартное отклонение членов ряда: ", ArcSinClass.list_stdev)
        print("Количество итераций до достижения точности: ", ArcSinClass.iterations)
        print("Вычисленное значение: ", ArcSinClass.value)
        
        #диапазон для x: [-1; введенный x]
        #отмена
        save = x
        x = np.arange(-1, 1, 0.01)
        y = np.array([], "float64")

        for x_i in x:
            y = np.append(y, ArcSin.ArcsinTaylor(x_i, eps).sum)

        fig, ax = plt.subplots()

        ax.grid(True)
        ax.set_xlabel("x")
        ax.set_ylabel("F(x)")
        ax.set_title("Taylor")
        ax.plot(x, y, "r", linewidth = 2, label = "Taylor")
        ax.text(-1, 0, "График приближенного вычисления\nс помощью ряда Тейлора\nс точностью eps = {}".format(eps))
        ax.annotate("Точка (0, 0)", xy = (0, 0), xytext = (0.1, -1), arrowprops = dict(facecolor = "black", shrink = 0.05))
        ax.plot(x, np.arcsin(x), "b", linewidth = 3, label = "arcsin(x)")
        ax.legend()

        plt.savefig("Task3/Graphimage.png")
        plt.show()

        while True:    
            c = input("Repeate?[Y/N]: ").upper()
            if c != "N" and c != "Y": print("Unknown command. Retry input")
            else: break
        if c == "N": break