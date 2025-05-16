from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        #просто для демонстрации работы метода через super()
        print("Super() method activated!")
        #pass