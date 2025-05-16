#Task2
#Лабораторная работа №4. Работа с файлами, классами, сериализаторами,регулярными выражениями и стандартными библиотеками.
#Version: 1.0
#Dev: Богуцкий Тимофей Сергеевич
#Date: 02.05.2025

import os
import re
#from collections import Counter
from zipfile import ZipFile

if __name__ == "__main__":
    filename = "Task2/startingFile.txt" 
    zipfile = "Task2/zippedFile.txt"
    resultfile = "Task2/results.txt"
    with open(filename, "r", encoding = "utf-8") as fl:
        text = fl.read()

    #все слова без пробелов
    all_words = re.findall(r'\b[a-zA-Zа-яА-Я]+\b', text)
    print(all_words)

    #заменитель    
    processed_text = re.sub(r'([a-z])([A-Z])', r'_?_\1\2_?_', text)
    print("Текст, обработанный на латинские буквы:")
    print(processed_text)

    #слова короче 7 символов
    #short_words = [word for word in all_words if len(word) < 7]
    short_words = re.findall(r'\b[a-zA-Zа-яА-Я]{1,6}\b', text)
    print("Слова короче 7 символов:")
    print(short_words)

    #самое короткое на а
    #words_ending_with_a = [word for word in all_words if word.lower().endswith('а') and len(word) >= 2]
    words_ending_with_a = re.findall(r'\b[a-zA-Zа-яА-Я]{1,}а\b', text, re.IGNORECASE)
    #print(words_ending_with_a)
    shortest_a_word = min(words_ending_with_a, key=len) if words_ending_with_a else "Не найдено"
    print("Самое короткое слово, оканчивающиеся на 'а': ", shortest_a_word)

    #сортированные по длине
    words_sorted_by_length = sorted(all_words, key=lambda x: -len(x))
    print("Отсортированный по длине слов список:")
    print(words_sorted_by_length)

    with open(zipfile, "w", encoding = "utf-8") as fl:
        fl.write("1. Все слова текста: {}\n".format(all_words))
        fl.write("2. Текст с выделенными парами символов:\n{}\n".format(processed_text))
        fl.write("3. Количество слов короче 7 символов: {}\n".format(len(short_words)))
        fl.write("4. Самое короткое слово на 'a': {}\n".format(shortest_a_word))
        fl.write("5. Слова по убыванию длины: {}\n".format(words_sorted_by_length))

    os.chdir('Task2')
    with ZipFile("ENDZIP.zip", "w") as myzip:
        myzip.write("zippedFile.txt")
        info = myzip.getinfo("zippedFile.txt")
        print(info)
    os.chdir('..')

    dot = len(re.findall(r"\S\.\s", text))
    ep = len(re.findall(r"\S\!\s", text))
    qm = len(re.findall(r"\S\?\s", text))

    sen = [s for s  in re.split(r"(\.|\!|\?)\s", text) if s != "." and s != "!" and s != "?"]
    length = 0.
    count_word = 0
    print(sen)
    for s in sen:
        for w in re.findall(r'\b[a-zA-Zа-яА-Я]+\b', s):
            count_word = count_word + 1
            length = length + len(w)
    avgsen = length / len(sen)
    avgword = length / count_word

    smile_count = len(re.findall(r'(?:\:|\;)\-*(?:\(|\)|\[|\])+', text))

    with open(resultfile, "w", encoding = "utf-8") as fl:
        fl.write("Количество предложений: {}\n" \
        "Повествовательных: {}\n" \
        "Побудительных: {}\n" \
        "Вопросительных: {}\n".format(dot+ep+qm, dot, ep, qm)) 
        fl.write("Средняя длина предложений: {}\n" \
        "Средняя длина слов: {}\n" \
        "Количество смайликов: {}\n".format(avgsen, avgword, smile_count)) 