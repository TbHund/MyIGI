def check(str):
    """Check str on hex number

    Return boolean
    """
    for c in str:
        if (c != '0' and c != '1'):
            return False
    return True