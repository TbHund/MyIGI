class ShapeColor:
    def __init__(self, color):
        self.__color = color

    @property
    def color(self):
        return self.__color
    
    @color.setter
    def color(self, color):
        self.__color = color

    def __str__(self):
        return "Цвет фигуры: {}".format(self.__color)