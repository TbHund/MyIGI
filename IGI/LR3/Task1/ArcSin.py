import math

def arcsin_taylor(x, eps):
    """
    Вычисляет арксинус с помощью ряда Тейлора с заданной точностью

    Возвращает:
        list 0:sum 1:number of iteraction
    """
        
    result = 0.0
    for n in range(0, 500):
        numerator = math.factorial(2 * n)
        denominator = (4**n) * (math.factorial(n)**2) * (2 * n + 1)
        term = numerator / denominator * x**(2 * n + 1)
        
        result += term
        
        if abs(term) < eps:
            return (result, n)
        
    return (sum, n)