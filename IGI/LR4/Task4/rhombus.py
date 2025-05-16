import shape
import shapecolor

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

class Rhombus(shape.Shape):
    def __init__(self, a_diagonal, b_diagonal, color, name="Rhombus"):
        self.a_diagonal = a_diagonal  
        self.b_diagonal = b_diagonal 
        self.color = shapecolor.ShapeColor(color) 
        self.__name = name

    @property
    def name(self):
        return self.__name

    def area(self):
        super().area()
        return (self.a_diagonal * self.b_diagonal) / 2

    def __format__(self):
        return "{} {} {} {} {}".format(self.__name, self.a_diagonal, self.b_diagonal, self.color, self.area())

    def draw(self, savefile=""):
        half_a = self.a_diagonal / 2
        half_b = self.b_diagonal / 2
        
        vertices = np.array([
            [-half_a, 0], 
            [0, half_b],   
            [half_a, 0],  
            [0, -half_b]  
        ])
        
        fig, ax = plt.subplots()
        rhombus = Polygon(vertices, closed=True, facecolor=self.color.color, edgecolor="black")
        ax.add_patch(rhombus)
        
        ax.set_xlim(-self.a_diagonal / 2 - 1, self.a_diagonal / 2 + 1)
        ax.set_ylim(-self.b_diagonal / 2 - 1, self.b_diagonal / 2 + 1)
        
        ax.set_title(f'{self.__name}\na={self.a_diagonal}, b={self.b_diagonal}, Area={self.area()}')
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)

        if savefile:
            plt.savefig(savefile)
        plt.show()