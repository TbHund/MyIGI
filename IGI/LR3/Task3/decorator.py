def decorator(func):
    """Decorate function
    
    print name, args, kwargs, result 
    """
    def new_function(*args, **kwargs):
        print("Running function: ", func.__name__)
        print("Positional args: ", args)
        print("Keyword args: ", kwargs)
        result = func(*args, **kwargs)
        print("Result: ", result)
        return result
    return new_function