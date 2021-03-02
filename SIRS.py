import numpy as np
from CellularAutomata import CellularAutomata


class SIRS(CellularAutomata):
    """
    A Cellular automata model to simulate the spread of an infection through a population. Each cell can have one of
    three states
    Susceptible
    Infected
    Recovered
    as the SIR model. The SIRS model introduces the probability for a return to susceptible after recovered.
    """

    def __init__(self, shape: tuple, p1: float, p2: float, p3: float, susceptible=1, infected=2):
        """
        Args:
            shape: the size of the grid
            p1: Probability S->I
            p2: Probability I->R
            p3: Probability R->S
            susceptible: value to denote susceptible
            infected: value to denote infected

            recovered will always be denoted by a 0
        """
        super().__init__(shape, [susceptible, infected])
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def rules(self, x, y, N):
        # check the state of the cell
        state = self[x, y]
        # roll a dice
        p = np.random.random()
        # the state is susceptible
        if state == self.actors[1]:
            # check if any of the neighbours around the cell are infected
            if N[self.actors[2]] > 0:
                if p <= self.p1:
                    return self.actors[2]
                else:
                    return state
            else:
                return state
        # the state is infected
        elif state == self.actors[2]:
            # check to see if the state recovers
            if p <= self.p2:
                # return a recovered state
                return self.actors[0]
            else:
                return state
        # the state is recovered
        elif state == self.actors[0]:
            # check to see if the state becomes susceptible again
            if p <= self.p3:
                # return a susceptible state
                return self.actors[1]
            else:
                return state
