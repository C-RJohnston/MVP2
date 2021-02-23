import numpy as np
from Grid import Grid
from matplotlib import pyplot as plt
from matplotlib import cm
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib import animation
class CellularAutomata(Grid):
    """
    Base Cellular Automata class
    Has a grid of given shape and methods for rules, updating the grid, and calculating neighbours
    Args:
        shape - length and width of the playspace
        actors - value(s) used to represent active site(s), default 1
    """

    def rules(self,x,y,N):
        """
        Applies the ruleset to a given cell dependent on the cell's neighbours and returns the new state for that cell
        Args:
            x,y - the cell to update as a grid position
            N - number of neighbours around the cell
        Return:
            The new value of the cell
        """
        return 0
    
    def get_8_Neighbours_of_Value(self,x,y,value):
        """
        finds the number of neighbours of specific type around a cell using the on-axis and off-axis neighbours
        Args:
            x,y - the cell around which to find neighbours 
            values - value representing which actor to consider a neighbour
        Return:
            Number of neighbours
        """
        N_Pos = {(0,0):(x-1,y-1),(0,1):(x-1,y),(0,2):(x-1,(y+1)%self.shape[1]),
                (1,0):(x,y-1),(1,1):(x,y),(1,2):(x,(y+1)%self.shape[1]),
                (2,0):((x+1)%self.shape[0],y-1),(2,1):((x+1)%self.shape[0],y),(2,2):((x+1)%self.shape[0],(y+1)%self.shape[1])}
        Neighbours = np.empty((3,3))
        for I,N in N_Pos.items():
            Neighbours[I] = self[N]
        S = np.where(Neighbours==value,1,0)
        #don't count self
        S[1,1] = 0
        return np.sum(S)
    
    def get_4_Neighbours_of_Value(self,x,y,value):
        """
       finds the number of neighbours of specific type around a cell using the on-axis neighbours only
        Args:
            x,y - the cell around which to find neighbours
            values - value representing which actor to consider a neighbour
        Return:
            Number of neighbours
        """
        x_min = x-1
        y_min = y-1
        x_max = (x+1)%self.shape[0]
        y_max = (y+1)%self.shape[1]
        N=0
        if(self[x_min,y]==value):
            N+=1
        if(self[x_max,y]==value):
            N+=1
        if(self[x,y_min]==value):
            N+=1
        if(self[x,y_max]==value):
            N+=1
        return N
    
    def update(self,neighbour_method=8):
        """
        Updates the grid using the chosen method for neighbours

        Args:
            neighbour_method: either 8 (for on-and off axis) or 4 (for on-axis only)
        """
        new = self.__class__(self.shape,self._actors[1:])
        X = self.shape[0]
        Y = self.shape[1]
        for x in range(X):
            for y in range(Y):
                neighbours = {}
                if(neighbour_method == 8):
                    for n in self._actors[1:]:
                        neighbours[n] = self.get_8_Neighbours_of_Value(x,y,n)
                else:
                    for n in self._actors[1:]:
                        neighbours[n] = self.get_4_Neighbours_of_Value(x,y,n)
                new[x,y] = self.rules(x,y,neighbours)
        self.__dict__.update(new.__dict__)
    
    def find_equilibrium(self,actor,steps=10,tol=1,neighbour_method=8):
        """
        Updates the cells n times until it reaches equilibrium and returns
        the number of steps required to do so
        Args:
            -actor: actor value to monitor
            -steps: number of updates to check
            -tol: the degree to which the number of active cells must be the same
            -neighbours_method: the way of checking neighbours (on-axis only or on-and off axis)
        Returns:
            The number of steps required to reach equilibrium
        """
        num_active = [self.count(actor)]
        self.update(neighbour_method)
        num_active.append(self.count(actor))
        count = 1
        while(not np.allclose(num_active,num_active[0],atol=tol)):
            self.update(neighbour_method)
            num_active.append(self.count(actor))
            if(len(num_active)>10):
                del num_active[0]
            count +=1
        return count


    def animate(self,CELL_COLOURS,BG_COLOUR,steps,title,neighbour_method=8):
        """
        using matplotlib, animate the cellular automata over a given number of steps
        Args:
            -CELL_COLOURS: colours for each type of active cell
            -BG_COLOUR: colour for the background/dead cells
            -steps: number of frames to animate for
        """
        cols = ListedColormap([BG_COLOUR,CELL_COLOURS])
        fig,ax = plt.subplots()
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        ax.set_title(title)
        im = ax.imshow(self,cmap=cols)
        def animate(i):
            self.update(8)
            im.set_array(self)
            return im,
        a = animation.FuncAnimation(fig,animate,frames=steps,interval=1)
        plt.show()


