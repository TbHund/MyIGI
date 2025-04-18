import random

def gen_list():
    """Generate list of int numbers

    Return generate exp
    """
    random_number = 0
    while random_number != 10:
        random_number = random.randint(-10, 10)
        yield random_number