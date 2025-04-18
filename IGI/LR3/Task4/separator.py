def sep_str(str):
    """Split text.

    Separators: ', ', ' '
    Return List of words
    """
    ls = []
    for elem in str.split(", "):
        ls.extend(elem.split(" "))
    return ls