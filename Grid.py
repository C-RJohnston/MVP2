import numpy as np

class Grid:
    """
    An implementation of a gridspace to host cellular automata using ints to represent states
    0 empty
    Args:
        - shape: the size of the grid as a tuple 
        - valid states: states the grid is allowed to be comprised of
    """

    def __init__(self,shape : tuple, actors = 1):
        self._shape = shape
        self._actors=actors
        if(type(self._actors) == int):
            self._actors = [0,self._actors]
        else:
            self._actors = [0]+self._actors
        self._array = np.full(self._shape,0,dtype=int)

    def __len__(self):
        return len(self.array)

    def __getitem__(self,index):
        """
        returns the row/element from the array at position given by the index.
        Args:
            - index: int/tuple specifies desired row/element
        Returns:
            row/element
        """
        return self.array[index]
    
    def __setitem__(self,index,value):
        """
        sets the row/element of the array at given index.
        Args:
            - index: int/tuple specifies the row/element to modify
            -value: array/int new value to set at index
        """
        self.array[index] = value
    
    @property
    def shape(self):
        """
        The shape of the grid
        """
        return self._shape
    
    @property
    def array(self):
        return self._array

    def __repr__(self):
        """
        printable form of the grid
        """
        return self.array.__str__()

    def info(self):
        """
        stats about the grid
        """
        rep = " x ".join(list(map(str,self.shape)))+" Grid\n"
        for s in self._actors:
            rep+=f"Number of {s} states: {self.count(s)}\n"
        return rep
    
    def randomise(self):
        """
        Randomly assigns a state to each cell in the grid uniformly
        """
        self._array = np.random.choice(self._actors,self.shape)

    def clear(self):
        """
        Resets the grid back to default value
        """
        self._array = np.full(self._shape,self._actors[0],dtype=int)

    def count(self,state):
        """
        Returns the number of given states in the grid
        Args:
            state - a valid state specified in the constructor
        Returns:
            count - the number of occurences of the states in the grid
        """
        unique, counts = np.unique(self.array, return_counts=True)
        counts = dict(zip(unique, counts))
        try:
            return counts[state]
        except:
            return 0
