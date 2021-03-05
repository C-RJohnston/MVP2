import numpy as np
from Grid import Grid
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import animation
import scipy.ndimage
import scipy.signal
import time


class CellularAutomata(Grid):
    """
    Base Cellular Automata class
    Has a grid of given shape and methods for rules, updating the grid, and calculating neighbours
    Args:
        shape - length and width of the grid
        actors - value(s) used to represent active site(s), default 1
    """

    def rules(self, c, neighbours):
        """
        Applies the rule-set to a given cell dependent on the cell's neighbours and returns the new state for that cell
        Args:
            c: the cell value at a given position
            neighbours: the number of neighbours of some value around that cell
        Return:
            The new value of the cell
        """
        return 0

    def get_neighbours_of_value(self, value, weight):
        """
        finds the number of neighbours of cells using the on-axis and off-axis neighbours
        Args:
            values - value representing which actor to consider a neighbour
        Return:
            array of number of neighbours
        """
        copy = np.copy(self.array)
        copy = np.where(copy == value, 1, 0)
        conv = scipy.ndimage.filters.convolve(copy, weight, mode='wrap')
        return conv

    def update(self, actor, weight=np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])):
        """
        Updates the grid using the chosen method for neighbours

        Args:
            actor: the actor that effect the update
            weight: weighting of neighbours to consider
        """
        neighbours = self.get_neighbours_of_value(actor, weight)
        rules_vec = np.vectorize(self.rules)
        self._array = rules_vec(self.array, neighbours)

    def sequential_update(self, actor, weight=np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])):
        """
        Sequentially updates the grid by randomly choosing a cell and applying the update rule.
        Repeats this process N times
        Args:
            actor: the actor that effect the update
            weight: weighting of neighbours to consider
        """
        X = self.shape[1]
        Y = self.shape[0]
        for _ in range(X * Y):
            # randomly choose a point on the grid
            x = np.random.randint(X)
            y = np.random.randint(Y)
            # get the neighbours of the cell
            i_x = [(x-1) % X, x, (x+1) % X]
            i_y = [(y-1) % Y, y, (y+1) % Y]
            neighbours = self.array[i_y][:, i_x]
            # remove any irrelevant neighbours and count
            neighbours = neighbours*weight
            neighbours = sum(neighbours[neighbours == actor])
            self._array[x, y] = self.rules(self.array[x, y], neighbours)

    def find_equilibrium(self, actor, effector, weight=np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]), steps=10, tol=1):
        """
        Updates the cells n times until it reaches equilibrium and returns
        the number of steps required to do so
        Args:
            actor: actor value to monitor
            effector: actor which causes changes
            weight: weighting of a neighbour to consider
            steps: number of updates to check
            tol: the degree to which the number of active cells must be the same
        Returns:
            The number of steps required to reach equilibrium
        """
        num_active = [self.count(actor)]
        self.update(effector, weight)
        num_active.append(self.count(actor))
        count = 1
        while not np.allclose(num_active, num_active[0], atol=tol):
            self.update(effector, weight)
            num_active.append(self.count(actor))
            if len(num_active) > steps:
                del num_active[0]
            count += 1
        return count

    def CoM(self, actor: int, on_grid=False):
        """
        Returns the position of the centre of mass of a specific actor
        Args:
            actor: the value of which actor to monitor
            on_grid: whether or not to round the position to the nearest int
        Returns:
            the position of the centre of mass
        """
        # find all the actors on the grid
        x = np.where(self == actor)
        A = np.empty(len(x[0]), dtype=object)
        for i, v in enumerate(x[0]):
            A[i] = np.array([v, x[1][i]])
        # find the number of actors
        count = self.count(actor)
        if on_grid:
            return np.round(sum(A / count)).astype(int)
        else:
            return sum(A / count)

    def animate(self, CELL_COLOUR, BG_COLOUR, steps, title, patches, effector, update_method='c'):
        """
        using matplotlib, animate the cellular automata over a given number of steps
        Args:
            CELL_COLOUR: colours for each type of active cell
            BG_COLOUR: colour for the background/dead cells
            steps: number of frames to animate for
            title: title on the graph
            patches: name of actor and colour to display in a legend
            effector: the actor that causes updates
            update_method: the method used to update the display 'c' concurrent 's' sequential.
        """
        if type(CELL_COLOUR) == list:
            c = [BG_COLOUR]
            c.extend(CELL_COLOUR)
        else:
            c = [BG_COLOUR, CELL_COLOUR]
        cols = ListedColormap(c)
        fig, ax = plt.subplots()
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        ax.set_title(title)
        fig.legend(handles=patches)
        im = ax.imshow(self, cmap=cols)
        fig.colorbar(im)
        if update_method == 'c':
            method = self.update
        else:
            method = self.sequential_update

        def animate(i):
            method(effector)
            im.set_array(self)
            return im,

        a = animation.FuncAnimation(fig, animate, frames=steps, interval=1)
        plt.show()

    def animateCoM(self, CELL_COLOURS, BG_COLOUR, steps, title, patches, actor, effector, update_method='c'):
        """
        using matplotlib, animate the Centre of mass of the automata over a given number of steps
        Args:
            CELL_COLOURS: colours for each type of active cell
            BG_COLOUR: colour for the background/dead cells
            steps: number of frames to animate for
            title: title on the graph
            actor: actor to monitor CoM
            effector: actor that causes updates
            update_method: the method used to update the display 'c' concurrent 's' sequential.
        """
        cols = ListedColormap([BG_COLOUR, CELL_COLOURS])
        fig, ax = plt.subplots()
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        ax.set_title(title)
        im = ax.imshow(self, cmap=cols)
        fig.legend(handles=patches)
        if update_method == 'c':
            method = self.update
        else:
            method = self.sequential_update

        def animate(i):
            method(effector)
            X = tuple(self.CoM(actor, True))
            new = self.__class__(self.shape, self._actors[1:])
            new[X] = 1
            im.set_array(new)
            return im,

        a = animation.FuncAnimation(fig, animate, frames=steps, interval=1)
        plt.show()
