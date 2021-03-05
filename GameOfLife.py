import numpy as np
from CellularAutomata import CellularAutomata


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
        x = self.shape[0] // 2
        y = self.shape[1] // 2
        self[y, x - 1] = alive
        self[y - 1, x] = alive
        self[y - 1, x + 1] = alive
        self[y + 1, x] = alive
        self[y + 1, x + 1] = alive
        self[y, x + 2] = alive

    def blinker(self):
        """
        Initialise the grid to be empty apart from the blinker shape
        010
        010
        010
        """
        alive = self._actors[1]
        self.clear()
        x = self.shape[0] // 2
        y = self.shape[1] // 2
        self[y, x] = alive
        self[y + 1, x] = alive
        self[y + 2, x] = alive

    def glider(self):
        """
        Initialise the grid to be empty apart from the glider shape
        001
        101
        011
        """
        alive = self.actors[1]
        self.clear()
        self[0, 2] = alive
        self[1, 0] = alive
        self[1, 2] = alive
        self[2, 1] = alive
        self[2, 2] = alive

    def rules(self, c, neighbours):
        if c == self.actors[1]:
            if neighbours == 2 or neighbours == 3:
                return self.actors[1]
            else:
                return self.actors[0]
        else:
            if neighbours == 3:
                return self.actors[1]
            else:
                return self.actors[0]

    def glider_CoM(self, steps):
        """
        Measures the centre of mass of the glider over time, accounting for the periodic boundary conditions
        Args:
            -steps: number of timesteps to measure for
        """
        self.glider()
        end = np.array(self.shape) - 2
        pos = []
        for _ in range(steps):
            self.update(1)
            x = self.CoM(1, True)
            pos.append(x)
            if np.array_equal(pos[-1], end) and np.array_equal(pos[-2], end):
                break
        with open("glidercom.txt", 'w') as outfile:
            out = ''
            for r in pos:
                out += f"{r[0]},{r[1]}\n"
            v = np.linalg.norm(pos[0]-pos[-1]) / len(pos)
            out += str(v)
            outfile.write(out)

        return v
