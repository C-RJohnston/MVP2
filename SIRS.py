import numpy as np
from CellularAutomata import CellularAutomata
import time

class SIRS(CellularAutomata):
    """
    A Cellular automata model to simulate the spread of an infection through a population. Each cell can have one of
    three states
    Susceptible
    Infected
    Recovered
    as the SIR model. The SIRS model introduces the probability for a return to susceptible after recovered.
    """

    def __init__(self, shape: tuple, p1: float, p2: float, p3: float, susceptible=1, infected=2, immune=3):
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
        super().__init__(shape, [susceptible, infected, immune])
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def randomise(self, immunised: float):
        """
        Args:
            immunised: fraction of immunised people in the grid
        """
        x = (1-immunised)/3
        self._array = np.random.choice(self.actors, self.shape, p=[x, x, x, immunised])

    def measure_infections(self, equilibrate_sweeps: int, measurements: int):
        """
        Args:
            equilibrate_sweeps: the number of sweeps to perform before taking measurements
            measurements: the number of measurements to make

        Returns: the number of infected for each measurement
        """
        # first come to equilibrium
        for _ in range(equilibrate_sweeps):
            self.sequential_update(self.actors[2])
        infected = np.zeros(measurements)
        # measure the number of infected
        for i in range(measurements):
            self.sequential_update(self.actors[2])
            infected[i] = self.count(self.actors[2])
            if infected[i] == 0:
                break
        return infected, self.p1, self.p3

    def rules(self, c, neighbours):
        # check the state of the cell
        # roll a dice
        p = np.random.random()
        # the state is susceptible
        if c == self.actors[1]:
            # check if any of the neighbours around the cell are infected
            if neighbours > 0:
                if p <= self.p1:
                    return self.actors[2]
                else:
                    return c
            else:
                return c
        # the state is infected
        elif c == self.actors[2]:
            # check to see if the state recovers
            if p <= self.p2:
                # return a recovered state
                return self.actors[0]
            else:
                return c
        # the state is recovered
        elif c == self.actors[0]:
            # check to see if the state becomes susceptible again
            if p <= self.p3:
                # return a susceptible state
                return self.actors[1]
            else:
                return c
        # the state is immune
        elif c == self.actors[3]:
            return c
