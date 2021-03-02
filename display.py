import tkinter as tk
from tkinter import ttk
from matplotlib import colors
from GameOfLife import GameOfLife
from SIRS import SIRS
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches


class GoLFrame(tk.Frame):
    def __init__(self, parent, Options, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.O = Options
        self.l = ttk.Label(self, text="Initalise with:")
        self.methods = ["Random", "Beehive", "Blinker", "Glider"]
        self.choices = ttk.Combobox(self, values=self.methods)
        self.choices.current(0)
        self.Run = ttk.Button(self, text="Run", command=self.begin)
        self.mlabel = ttk.Label(self, text="Measure equilibriums\nWARNING: can take some time")
        self.mbutton = ttk.Button(self, text="Measure", command=self.measure)
        self.CoMButton = ttk.Button(self, text="Run CoM", command=self.CoM)
        self.speedlabel = ttk.Label(self, text="Speed of a glider moving across the grid")
        self.speedbutton = ttk.Button(self, text="Speed", command=self.speed)
        self.speedval = tk.Text(self, height=1, borderwidth=0, state='disabled', width=10)
        self.graphbutton = ttk.Button(self, text="Histogram", command=self.plot)
        self.graphlabel = ttk.Label(self, text="Enter filename of measurements")
        self.dir = ttk.Entry(self, width='15')
        self.l.grid(column=0, row=0)
        self.choices.grid(column=0, row=1)
        self.mlabel.grid(column=0, row=2, pady=20)
        self.mbutton.grid(column=0, row=3)
        self.Run.grid(column=0, row=4, pady=20)
        self.graphbutton.grid(column=1, row=6, pady=10)
        self.graphlabel.grid(column=0, row=5)
        self.dir.grid(column=0, row=6, pady=10)
        self.CoMButton.grid(column=0, row=7, pady=10)
        self.speedlabel.grid(column=0, row=8, pady=10)
        self.speedbutton.grid(column=1, row=8, pady=10)
        self.speedval.grid(column=2, row=8, pady=10)

    def plot(self):
        p = self.dir.get()
        name = p.split('.')[0]
        with open(p, 'r') as infile:
            times = list(map(int, infile.read().split(',')))
        plt.hist(times)
        plt.savefig(name + '.jpg')
        plt.show()

    def speed(self):
        params = self.O.get_params()
        G = GameOfLife((params['x'], params['y']))
        v = G.glider_CoM(params['measurements'])
        self.speedval.configure(state='normal')
        self.speedval.insert(1.0, str(round(v, 2)))
        self.speedval.configure(state='disabled')

    def CoM(self):
        params = self.O.get_params()
        G = GameOfLife((params['x'], params['y']))
        # choose method to initalise the CA with
        switch = self.choices.get()
        if switch == "Random":
            G.randomise()
        elif switch == "Beehive":
            G.beehive()
        elif switch == "Blinker":
            G.blinker()
        else:
            G.glider()
        alive_patch = mpatches.Patch(color=params['fg_colour'], label="Alive")
        dead_patch = mpatches.Patch(color=params['bg_colour'], label="Dead")
        patches = [alive_patch, dead_patch]
        G.animateCoM(params['fg_colour'], params['bg_colour'], params['steps'], "Game of Life", patches, 1)

    def measure(self):
        params = self.O.get_params()
        steps = []
        for i in range(params['measurements']+1):
            G = GameOfLife((params['x'], params['y']))
            G.randomise()
            steps.append(G.find_equilibrium(1))
            print(f"{i}/{params['measurements']}")
        with open('equilibrium.txt', 'w') as outfile:
            outfile.write(','.join(map(str, steps)))

    def begin(self):
        params = self.O.get_params()
        G = GameOfLife((params['x'], params['y']))
        # choose method to initialise the CA with
        switch = self.choices.get()
        if switch == "Random":
            G.randomise()
        elif switch == "Beehive":
            G.beehive()
        elif switch == "Blinker":
            G.blinker()
        else:
            G.glider()
        alive_patch = mpatches.Patch(color=params['fg_colour'], label="Alive")
        dead_patch = mpatches.Patch(color=params['bg_colour'], label="Dead")
        patches = [alive_patch, dead_patch]
        G.animate(params['fg_colour'], params['bg_colour'], params['steps'], "Game of Life", patches)


class SIRSFrame(tk.Frame):
    def __init__(self, parent, Options, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.O = Options
        sets = ["Absorbing", "Dynamic Equilibrium", "Cyclic Waves", "Custom"]
        self.choices = ttk.Combobox(self, values=sets)
        self.choices.current(3)
        self.choices.bind('<<ComboboxSelected>>', self.set_values)
        self.p1 = tk.Scale(self, label="p1", from_=0, to_=1, resolution=0.02, orient=tk.HORIZONTAL)
        self.p2 = tk.Scale(self, label="p2", from_=0, to_=1, resolution=0.02, orient=tk.HORIZONTAL)
        self.p3 = tk.Scale(self, label="p3", from_=0, to_=1, resolution=0.02, orient=tk.HORIZONTAL)
        self.animButton = ttk.Button(self, text="Run", command=self.run)
        self.choices.grid(row=0, column=0)
        self.p1.grid(row=1, column=0, pady=5)
        self.p2.grid(row=2, column=0, pady=5)
        self.p3.grid(row=3, column=0, pady=5)
        self.animButton.grid(row=4, column=0)

    def set_values(self, event):
        choice = self.choices.get()
        self.p1.configure(state='normal')
        self.p2.configure(state='normal')
        self.p3.configure(state='normal')
        if choice == "Absorbing":
            self.p1.set(0.50)
            self.p2.set(0.50)
            self.p3.set(0.02)
            self.p1.configure(state='disabled')
            self.p2.configure(state='disabled')
            self.p3.configure(state='disabled')
        elif choice == "Dynamic Equilibrium":
            self.p1.set(0.10)
            self.p2.set(0.10)
            self.p3.set(0.10)
            self.p1.configure(state='disabled')
            self.p2.configure(state='disabled')
            self.p3.configure(state='disabled')
        elif choice == "Cyclic Waves":
            self.p1.set(0.32)
            self.p2.set(0.12)
            self.p3.set(0.02)
            self.p1.configure(state='disabled')
            self.p2.configure(state='disabled')
            self.p3.configure(state='disabled')
        else:
            self.p1.set(0.00)
            self.p2.set(0.00)
            self.p3.set(0.00)

    def run(self):
        params = self.O.get_params()
        p1 = float(self.p1.get())
        p2 = float(self.p2.get())
        p3 = float(self.p3.get())
        S = SIRS((params['x'], params['y']), p1, p2, p3)
        S.randomise()
        susceptible_patch = mpatches.Patch(color=params['fg_colour'], label='Susceptible')
        infected_patch = mpatches.Patch(color=params['inf_colour'], label="Infected")
        recovered_patch = mpatches.Patch(color=params['bg_colour'], label='Recovered')
        patches = [susceptible_patch, infected_patch, recovered_patch]
        S.animate([params['fg_colour'], params['inf_colour']], params['bg_colour'], params['steps'],
                  "SIRS", patches, neighbour_method=4, update_method='s')




class OptionsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.colours = list(colors.CSS4_COLORS)
        self.labx = ttk.Label(self, text="Grid X")
        self.laby = ttk.Label(self, text="Grid Y")
        self.ex = ttk.Entry(self, width="5")
        self.ex.insert(0, "50")
        self.ey = ttk.Entry(self, width="5")
        self.ey.insert(0, "50")
        self.labcol = ttk.Label(self, text="Cell/Susceptible colour")
        self.ColMenu = ttk.Combobox(self, values=self.colours)
        self.ColMenu.current(1)
        self.infcol = ttk.Label(self, text="Infected colour")
        self.infMenu = ttk.Combobox(self, values=self.colours)
        self.infMenu.current(2)
        self.labbgcol = ttk.Label(self, text="Background/Recovered colour")
        self.BgColMenu = ttk.Combobox(self, values=self.colours)
        self.BgColMenu.current(0)
        self.steps = tk.Scale(self, label="#Steps", from_=0, to_=10_000, resolution=500, orient=tk.HORIZONTAL)
        self.steps.set(1000)
        self.measurements = tk.Scale(self, label="#Measurements", from_=0, to_=1000, resolution=100,orient=tk.HORIZONTAL)
        self.measurements.set(100)
        self.ApplyButton = ttk.Button(self, text="Apply", command=self.apply_settings)
        self.labx.grid(column=0, row=0)
        self.ex.grid(column=1, row=0, padx=5, pady=40)
        self.laby.grid(column=2, row=0)
        self.ey.grid(column=3, row=0, pady=40)
        self.labcol.grid(column=0, row=1)
        self.ColMenu.grid(column=1, row=1, columnspan=4)
        self.infcol.grid(column=0, row=2)
        self.infMenu.grid(column=1, row=2, columnspan=4)
        self.labbgcol.grid(column=0, row=4)
        self.BgColMenu.grid(column=1, row=4, columnspan=4)
        self.steps.grid(column=0, row=5, columnspan=2)
        self.measurements.grid(column=0, row=6, columnspan=2)
        self.ApplyButton.grid(column=0, row=7, pady=50)
        self.params = {'x': int(self.ex.get()), 'y': int(self.ey.get()), 'bg_colour': self.BgColMenu.get(),
                       'fg_colour': self.ColMenu.get(), 'inf_colour': self.infMenu.get(),
                       'steps': int(self.steps.get()),'measurements': int(self.measurements.get())}

    def get_params(self):
        return self.params

    def apply_settings(self):
        self.params = {'x': int(self.ex.get()), 'y': int(self.ey.get()), 'bg_colour': self.BgColMenu.get(),
                       'fg_colour': self.ColMenu.get(), 'inf_colour': self.infMenu.get(),
                       'steps': int(self.steps.get()),'measurements': int(self.measurements.get())}


class Main(ttk.Notebook):

    def __init__(self, parent, *args, **kwargs):
        ttk.Notebook.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        Options = OptionsFrame(self, height=200, width=100)
        Game_Of_Life = GoLFrame(self, Options, height=200, width=100)
        SIRS = SIRSFrame(self, Options, height=200, width=100)

        self.add(Game_Of_Life, text="Game of Life")
        self.add(SIRS, text="SIRS")
        self.add(Options, text="Options")


def main():
    root = tk.Tk()
    tc = Main(root)
    tc.pack()
    root.resizable(False, False)
    root.mainloop()


main()
