#Task1
#Лабораторная работа №4. Работа с файлами, классами, сериализаторами,регулярными выражениями и стандартными библиотеками.
#Version: 1.0
#Dev: Богуцкий Тимофей Сергеевич
#Date: 02.05.2025

import pickle
import phone
import csv
import re

if __name__ == "__main__":
    
    filename = "Task1/phoneBook.txt"
    csvfile = "Task1/phoneBook.csv"

    phonebook = {"Abonent1" : phone.Phone("Вася", "+375 (29) 173-84-81"),
                 "Abonent2" : phone.Phone("Петя", "+375 (29) 173-14-56"),
                 "Abonent3" : phone.Phone("Борис Николаевич Сухой", "+375 (29) 228-84-15"),
                 "Abonent4" : phone.Phone("Марья Ивановна Лебедева", "+375 (29) 228-84-17"),
                 "Abonent5" : phone.Phone("Петр Николаевич Морозов", "+375 (29) 228-52-46"),
                 "Abonent6" : phone.Phone("Вовочка", "+375 (44) 173-84-81"),
                 "Abonent7" : phone.Phone("Катюша", "+375 (44) 148-17-73"),
                 "Abonent8" : phone.Phone("Шариков", "+375 (25) 227-42-15"),
                 "Abonent9" : phone.Phone("Артем", "+375 (25) 227-43-19"),
                }
    
    with open(csvfile, "w", encoding = "utf-8", newline = "") as fl:
        writer = csv.writer(fl, quoting=csv.QUOTE_ALL)
        for abonent, phoneOwner in phonebook.items():
            writer.writerow([abonent, phoneOwner.owner, phoneOwner.phoneNumber])

    with open(filename, "wb") as fl:
        pickle.dump(phonebook, fl)

    while True:

        chooseOption = input("Выберите формат файла:\n1.txt\n2.csv\nДля выхода из программы введите 'S'\n").lower()
        if chooseOption == "s":
            break

        if chooseOption == "1":

            while True:
                number = input("Введите часть или полностью номер телефона: ")

                if re.fullmatch(r"\+\d{1,14}", number):
                    break 
                else:
                    print("Ошибка: нsомер должен начинаться с '+' и содержать только цифры (до 14 знаков). Попробуйте снова.")

            with open(filename, "rb") as fl:
                load_abonents = pickle.load(fl)

            found = False
            for abonent, phoneOwner in load_abonents.items():
                if phoneOwner.phoneNumber.startswith(number):
                    print(f"{abonent}: {phoneOwner.owner} ({phoneOwner.phoneNumber})")
                    found = True
            
            if not found:
                print("Ни один абонент не найден.")   

        elif chooseOption == "2":
            while True:
                number = input("Введите часть или полностью номер телефона: ")

                if re.fullmatch(r"\+\d{1,14}", number):
                    break 
                else:
                    print("Ошибка: нsомер должен начинаться с '+' и содержать только цифры (до 14 знаков). Попробуйте снова.")        
            load_abonents = {}

            with open(csvfile, "r", encoding="utf-8") as fl:
                reader = csv.reader(fl)
                for row in reader:
                    abonent_name = row[0]
                    owner_name = row[1]
                    phone_number = row[2]

                    load_abonents[abonent_name] = phone.Phone(owner_name, phone_number)

            found = False
            for abonent, phoneOwner in load_abonents.items():
                if phoneOwner.phoneNumber.startswith(number):
                    print(f"{abonent}: {phoneOwner.owner} ({phoneOwner.phoneNumber})")
                    found = True
            
            if not found:
                print("Ни один абонент не найден.")

        else:
            print("Ошибка при вводе!")