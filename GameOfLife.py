import numpy as np
from Grid import Grid
from CellularAutomata import CellularAutomata
from matplotlib import pyplot as plt
import timeit
class GameOfLife(CellularAutomata):
    
    def randomise(self):
        """
        Initialises the grid to be in random states
        """
        self._Grid.randomise()
    
    def beehive(self):
        """
        Initialises the grid to be empty apart from a beehive shape
        0110
        1001
        0110
        """
        alive = self._actors[0]
        self._Grid.clear()
        x = self.shape[0]//2
        y = self.shape[1]//2
        self._Grid[y,x-1]=alive
        self._Grid[y-1,x]=alive
        self._Grid[y-1,x+1]=alive
        self._Grid[y+1,x]=alive
        self._Grid[y+1,x+1]=alive
        self._Grid[y,x+2]=alive

    def blinker(self):
        """
        Initialise the grid to be empty apart from the blinker shape
        010
        010
        010
        """
        alive = self._actors[0]
        self._Grid.clear()
        x = self.shape[0]//2
        y = self.shape[1]//2
        self._Grid[y,x]=alive
        self._Grid[y+1,x]=alive
        self._Grid[y+2,x]=alive
    
    def glider(self):
        """
        Initialise the grid to be empty apart from the glider shape
        001
        101
        011
        """
        alive = self._actors[0]
        self._Grid.clear()
        self._Grid[0,2]=alive
        self._Grid[1,0]=alive
        self._Grid[1,2]=alive
        self._Grid[2,1]=alive
        self._Grid[2,2]=alive

    def rules(self,x,y,N):
        if(self._Grid[x,y]):
            if(N[1] == 2 or N[1] == 3):
                return self._actors[0]
            else:
                return 0
        else:
            if(N[1]==3):
                return self._actors[0]
            else:
                return 0
