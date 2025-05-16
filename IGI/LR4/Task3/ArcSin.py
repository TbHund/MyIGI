import math
import statistics

class ArcsinTaylor:
    
    def __init__(self, x=0.0, eps=0.1):
        self.x = x
        self.eps = eps
        self.terms = [] 
        self.sum = 0.0
        self.n = 0

        for n in range(0, 500):
            numerator = math.factorial(2 * n)
            denominator = (4**n) * (math.factorial(n)**2) * (2 * n + 1)
            term = numerator / denominator * x**(2 * n + 1)
            
            self.terms.append(term)
            self.sum += term
            
            if abs(term) < eps:
                self.n = n
                break

    @property
    def value(self):
        """Возвращает вычисленный арксинус"""
        return self.sum
    
    @property
    def list_mean(self):
        """Среднее значение членов ряда"""
        return statistics.mean(self.terms) if self.terms else 0
    
    @property
    def list_median(self):
        """Медиана членов ряда"""
        return statistics.median(self.terms) if self.terms else 0
    
    @property
    def list_variance(self):
        """Дисперсия членов ряда"""
        return statistics.variance(self.terms) if len(self.terms) > 1 else 0
    
    @property
    def list_stdev(self):
        """Стандартное отклонение членов ряда"""
        return statistics.stdev(self.terms) if len(self.terms) > 1 else 0
    
    @property
    def iterations(self):
        """Количество итераций до достижения точности"""
        return self.n