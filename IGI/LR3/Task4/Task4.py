import separator

def Task():
    """Solve Task4"""
    str = "So she was considering in her own mind, " \
    "as well as she could, for the hot day made her " \
    "feel very sleepy and stupid, whether the pleasure " \
    "of making a daisy-chain would be worth the trouble of " \
    "getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her."
    while True:
        ls = separator.sep_str(str)
        copy = ls
        print("Count of words: ", len(ls))

        print(ls)
        counter_lowercase = 0
        for elem in ls:
            for char in elem:
                if (char.islower() and char != '.' and char != '-'):
                    counter_lowercase += 1
        print("Number of lowercase: ", counter_lowercase)

        word_with_v = ""
        number_of_word = 1
        for elem in ls:
            if elem.find("v") != -1:
                print(f"First word with 'v' is '{elem}' it's number is {number_of_word}")
                break
            number_of_word += 1

        for elem in ls:
            if elem.startswith("s"):
                copy.remove(elem)

        print("Str without words that startwith 's': ")
        new_str = " ".join(copy)
        print(new_str)

        while True:    
            c = input("Repeate?[Y/N]: ").upper()
            if c != "N" and c != "Y": print("Unknown command. Retry input")
            else: break
        if c == "N": break