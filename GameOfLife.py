import numpy as np
from CellularAutomata import CellularAutomata
from matplotlib import pyplot as plt

class GameOfLife(CellularAutomata):
    
    
    def beehive(self):
        """
        Initialises the grid to be empty apart from a beehive shape
        0110
        1001
        0110
        """
        alive = self._actors[1]
        self.clear()
        x = self.shape[0]//2
        y = self.shape[1]//2
        self[y,x-1]=alive
        self[y-1,x]=alive
        self[y-1,x+1]=alive
        self[y+1,x]=alive
        self[y+1,x+1]=alive
        self[y,x+2]=alive

    def blinker(self):
        """
        Initialise the grid to be empty apart from the blinker shape
        010
        010
        010
        """
        alive = self._actors[1]
        self.clear()
        x = self.shape[0]//2
        y = self.shape[1]//2
        self[y,x]=alive
        self[y+1,x]=alive
        self[y+2,x]=alive
    
    def glider(self):
        """
        Initialise the grid to be empty apart from the glider shape
        001
        101
        011
        """
        alive = self._actors[1]
        self.clear()
        self[0,2]=alive
        self[1,0]=alive
        self[1,2]=alive
        self[2,1]=alive
        self[2,2]=alive

    def rules(self,x,y,N):
        if(self[x,y]):
            if(N[1] == 2 or N[1] == 3):
                return self._actors[1]
            else:
                return self._actors[0]
        else:
            if(N[1]==3):
                return self._actors[1]
            else:
                return self._actors[0]
