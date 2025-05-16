#Task5
#Лабораторная работа №4. Работа с файлами, классами, сериализаторами,регулярными выражениями и стандартными библиотеками.
#Version: 1.0
#Dev: Богуцкий Тимофей Сергеевич
#Date: 02.05.2025

import numpy as np

def get_std_manually(above_mean, count):
    manual_mean = np.mean(above_mean)
    squared_diff = np.sum((above_mean - manual_mean) ** 2)
    std_manual = np.sqrt(squared_diff / count)
    return std_manual

if __name__ == "__main__":

    while True:

        # массив через np.array
        data = [[1, 2, 3], [4, 5, 6]]
        arr = np.array(data)
        print("1. Массив через array():\n", arr)

        # особые массивы
        zeros_arr = np.zeros((2, 3))
        ones_arr = np.ones((3, 2))   
        diag_arr = np.eye(3)     
        print("\n2. Специальные массивы:")
        print("Нулевой:\n", zeros_arr)
        print("Единичный:\n", ones_arr)
        print("Диагональ:\n", diag_arr)

        # индексирование и срезы
        print("\n3. Индексирование:")
        print("Элемент [0,1]:", arr[0, 1])        
        print("Срез первого столбца:", arr[:, 0])  
        print("Срез последней строки:", arr[1, :]) 

        # универсальные функции
        sqrt_arr = np.sqrt(arr) 
        print("\n4. Универсальные функции (sqrt):\n", sqrt_arr, "\n")

        while True:    
            try:
                n = int(input("Input number of rows: "))
                if n <= 0: print("Input Error. Value must be positive")
                else: break
            except ValueError:
                print("Input Error")
        while True:    
            try:
                m = int(input("Input number of columns: "))
                if m <= 0: print("Input Error. Value must be positive")
                else: break
            except ValueError:
                print("Input Error")

        Matrix = np.random.randint(0, 100, size=(n, m))
        print("\nМатрица:\n", Matrix)

        corr_Matrix = np.corrcoef(Matrix)  
        print("\nМатрица корреляции:\n", corr_Matrix)

        mean_Matrix = np.mean(Matrix)
        print(f"\nСреднее значение элементов матрицы: {mean_Matrix:.2f}")

        median_Matrix = np.median(Matrix)
        print(f"Медиана матрицы: {median_Matrix:.2f}")

        var_Matrix = np.var(Matrix)
        print(f"Дисперсия всех элементов: {var_Matrix:.2f}")

        above_mean = Matrix[Matrix > mean_Matrix]
        count = len(above_mean)
        print(f"Количество элементов выше среднего: {count}")

        if count == 0:
            print("Нет элементов, превышающих среднее значение!")
        else:
            std_numpy = np.std(above_mean)
            helper = get_std_manually(above_mean, count)
            #manual_mean = np.mean(above_mean)
            #squared_diff = np.sum((above_mean - manual_mean) ** 2)
            #std_manual = np.sqrt(squared_diff / count)
            std_numpy = round(std_numpy, 2)
            helper = round(helper, 2)
            #std_manual = round(std_manual, 2)
            print(f"Стандартное отклонение (NumPy): {std_numpy}")
            print(f"Стандартное отклонение (ручной расчет): {helper}\n")
            #print(f"Стандартное отклонение (ручной расчет): {std_manual}\n")

        while True:    
            c = input("Repeate?[Y/N]: ").upper()
            if c != "N" and c != "Y": print("Unknown command. Retry input")
            else: break
        if c == "N": break