import tkinter as tk
from tkinter import ttk
from matplotlib import colors
from GameOfLife import GameOfLife
from SIRS import SIRS
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pickle
import os.path
from concurrent.futures import ProcessPoolExecutor, as_completed
import threading
import sys
from scipy.stats import sem

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

class GoLFrame(tk.Frame):
    def __init__(self, parent, Options, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.O = Options
        self.progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.l = ttk.Label(self, text="Initalise with:")
        self.methods = ["Random", "Beehive", "Blinker", "Glider"]
        self.choices = ttk.Combobox(self, values=self.methods)
        self.choices.current(0)
        self.Run = ttk.Button(self, text="Run", command=self.begin)
        self.mlabel = ttk.Label(self, text="Measure equilibrium\nWARNING: can take some time")
        self.mthread = threading.Thread(target=self.measure)
        self.mbutton = ttk.Button(self, text="Measure", command=self.mthread.start)
        self.CoMButton = ttk.Button(self, text="Run CoM", command=self.CoM)
        self.speedlabel = ttk.Label(self, text="Speed of a glider moving across the grid")
        self.speedbutton = ttk.Button(self, text="Speed", command=self.speed)
        self.speedval = tk.Text(self, height=1, borderwidth=0, state='disabled', width=10)
        self.l.grid(column=0, row=0)
        self.choices.grid(column=0, row=1)
        self.mlabel.grid(column=0, row=2, pady=20)
        self.mbutton.grid(column=0, row=3)
        self.Run.grid(column=0, row=4, pady=20)
        self.CoMButton.grid(column=0, row=7, pady=10)
        self.speedlabel.grid(column=0, row=8, pady=10)
        self.speedbutton.grid(column=1, row=8, pady=10)
        self.speedval.grid(column=2, row=8, pady=10)

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
        G.animateCoM(params['fg_colour'], params['bg_colour'], params['steps'], "Game of Life", patches, 1, 1)

    def measure(self):
        """
        Measure the number of alive cells until they come to equilibrium a given number of times
        to generate a histogram
        """
        self.progressbar.grid(column=0, row=9, columnspan=2)
        params = self.O.get_params()
        steps = []
        tasks = []
        with ProcessPoolExecutor() as e:
            for i in range(params['measurements']):
                G = GameOfLife((params['x'], params['y']))
                G.randomise()
                tasks.append(e.submit(G.find_equilibrium, 1, 1))
            progress = 0
            for t in as_completed(tasks):
                progress += 1
                x = progress/len(tasks)*100
                self.progressbar['value'] = x
                steps.append(t.result())
        print("done")
        self.progressbar.grid_forget()
        with open('equilibrium.txt', 'w') as outfile:
            outfile.write(','.join(map(str, steps)))
        sys.exit()

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
        G.animate(params['fg_colour'], params['bg_colour'], params['steps'], "Game of Life", patches, 1)


class SIRSFrame(tk.Frame):
    def __init__(self, parent, Options, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.O = Options
        self.progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate')
        sets = ["Absorbing", "Dynamic Equilibrium", "Cyclic Waves", "Custom"]
        self.choices = ttk.Combobox(self, values=sets)
        self.choices.current(3)
        self.choices.bind('<<ComboboxSelected>>', self.set_values)
        self.p1 = tk.Scale(self, label="p1", from_=0, to_=1, resolution=0.02, orient=tk.HORIZONTAL)
        self.p2 = tk.Scale(self, label="p2", from_=0, to_=1, resolution=0.02, orient=tk.HORIZONTAL)
        self.p3 = tk.Scale(self, label="p3", from_=0, to_=1, resolution=0.02, orient=tk.HORIZONTAL)
        self.f_immune = tk.Scale(self, label="Fraction immune", from_=0.0, to_=1, resolution=0.05, orient=tk.HORIZONTAL)
        self.runs = tk.Scale(self, label="Immune runs", from_=1, to_=10, resolution=1, orient=tk.HORIZONTAL)
        self.animButton = ttk.Button(self, text="Run", command=self.run)
        self.mthread = threading.Thread(target=self.measure_infections)
        self.varthread = threading.Thread(target=self.variance_precise)
        self.imthread = threading.Thread(target=self.measure_immune)
        self.measureButton = ttk.Button(self, text="Measure", command=self.mthread.start)
        self.varButton = ttk.Button(self, text="Precise variance", command=self.varthread.start)
        self.immuneButton = ttk.Button(self, text="Measure immunity", command=self.imthread.start)

        self.choices.grid(row=0, column=1)
        self.p1.grid(row=1, column=1, pady=5)
        self.p2.grid(row=2, column=1, pady=5)
        self.p3.grid(row=3, column=1, pady=5)
        self.f_immune.grid(row=4, column=1, pady=5)
        self.runs.grid(row=5, column=1, pady=5)
        self.animButton.grid(row=6, column=0)
        self.measureButton.grid(row=6, column=1, padx=10)
        self.varButton.grid(row=6, column=2)
        self.immuneButton.grid(row=6, column=3, padx=10)

    def set_values(self, event):
        choice = self.choices.get()
        self.p1.configure(state='normal')
        self.p2.configure(state='normal')
        self.p3.configure(state='normal')
        if choice == "Absorbing":
            self.p1.set(0.3)
            self.p2.set(0.7)
            self.p3.set(0.04)
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
            self.p1.set(0.8)
            self.p2.set(0.36)
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
        f_immune = float(self.f_immune.get())
        S = SIRS((params['x'], params['y']), p1, p2, p3)
        S.randomise(f_immune)
        susceptible_patch = mpatches.Patch(color=params['fg_colour'], label='Susceptible')
        infected_patch = mpatches.Patch(color=params['inf_colour'], label="Infected")
        recovered_patch = mpatches.Patch(color=params['bg_colour'], label='Recovered')
        immune_patch = mpatches.Patch(color=params['im_colour'], label='Immune')
        if f_immune > 0:
            patches = [susceptible_patch, infected_patch, recovered_patch, immune_patch]
            cols = [params['fg_colour'], params['inf_colour'], params['im_colour']]
        else:
            patches = [susceptible_patch, infected_patch, recovered_patch]
            cols = [params['fg_colour'], params['inf_colour']]
        S.animate(cols, params['bg_colour'], params['steps'], "SIRS", patches, 2, update_method='s')

    def variance_precise(self):
        """
        Measure the variance of infections over a short range of p1 [0.2-0.5]
        """
        self.progressbar.grid(row=7, column=0, columnspan=2)
        self.progressbar['value'] = 0
        params = self.O.get_params()
        size = params['x'] * params['y']
        p1s = np.round(np.arange(0.2, 0.5, params['precision']), 3)
        p2 = 0.5
        p3 = 0.5
        self.p2.set(p2)
        self.p3.set(p3)
        f_immune = float(self.f_immune.get())
        var = []
        error = []
        tasks = []
        with ProcessPoolExecutor() as e:
            for p1 in p1s:
                self.p1.set(p1)
                S = SIRS((params['x'], params['y']), p1, p2, p3)
                S.randomise(f_immune)
                tasks.append(e.submit(S.measure_infections, 100, params['measurements']))
            progress = 0
            for t in as_completed(tasks):
                progress += 1
                self.progressbar['value'] = progress/len(tasks)*100
                inf = t.result()[0]
                av_inf = np.mean(inf)
                av_inf_squared = np.mean(np.power(inf, 2))
                var.append(round((av_inf_squared-av_inf)/size, 3))
                # calculate errors using bootstrap method and 1000 resamples
                xs = []
                for _ in range(1000):
                    resamples = np.random.choice(inf, len(inf))
                    av = np.mean(resamples)
                    av_squared = np.mean(np.power(resamples, 2))
                    xs.append((av_squared-av)/S.size)
                x_squares = np.power(xs, 2)
                av_x = np.mean(xs)
                av_x2 = np.mean(x_squares)
                error.append(round((av_x2 - av_x ** 2) ** 0.5, 3))
        self.progressbar.grid_forget()
        with open("SIRSVar.txt", 'w') as outfile:
            out = ','.join(map(str, p1s))+'\n'
            out += ','.join(map(str, var))+'\n'
            out += ','.join(map(str, error))
            outfile.write(out)
        sys.exit()

    def measure_infections(self):
        """
        Measure the infection population and the variance for constant p2
        """
        params = self.O.get_params()
        self.progressbar.grid(row=7, column=0, columnspan=2)
        self.progressbar['value'] = 0
        p1s = np.round(np.arange(0, 1, params['precision']), 3)
        p3s = np.round(np.arange(0, 1, params['precision']), 3)
        p2 = 0.5
        self.p2.set(p2)
        f_immune = float(self.f_immune.get())
        data = {p1: {p3: {'val': 0, 'var': 0} for p3 in p3s} for p1 in p1s}
        tasks = []
        with ProcessPoolExecutor() as e:
            for p1 in p1s:
                for p3 in p3s:
                    S = SIRS((params['x'], params['y']), p1, p2, p3)
                    S.randomise(f_immune)
                    tasks.append(e.submit(S.measure_infections, 100, params['measurements']))
            progress = 0
            for f in as_completed(tasks):
                progress += 1
                self.progressbar['value'] = progress/len(tasks)*100
                inf, p1, p3 = f.result()
                self.p1.set(p1)
                self.p3.set(p3)
                av_inf = np.mean(inf)
                av_inf_squared = np.mean(np.power(inf, 2))

                data[p1][p3]['val'] = round(av_inf/S.size, 3)
                data[p1][p3]['var'] = round((av_inf_squared-av_inf)/S.size, 3)
        with open("SIRSMeasurements", 'wb') as outfile:
            pickle.dump(data, outfile)
        self.progressbar.grid_forget()
        sys.exit()

    def measure_immune(self):
        """
        Measure how the infected fraction changes with increasing immunised population
        """
        params = self.O.get_params()
        self.progressbar.grid(row=7, column=0, columnspan=2)
        self.progressbar['value'] = 0
        p1 = float(self.p1.get())
        p2 = float(self.p2.get())
        p3 = float(self.p3.get())
        runs = int(self.runs.get())
        f_immune = np.arange(0, 1, params['precision'])
        infs = []
        errors = []
        tasks = []
        with ProcessPoolExecutor() as e:
            progress = 0
            for f in f_immune:
                self.f_immune.set(f)
                progress += 1
                self.progressbar['value'] = progress/len(f_immune)*100
                x = []
                for _ in range(runs):
                    S = SIRS((params['x'], params['y']), p1, p2, p3)
                    S.randomise(f)
                    tasks.append(e.submit(S.measure_infections, 100, params['measurements']))
                for t in as_completed(tasks):
                    x.append(np.mean(t.result()[0]))
                infs.append(np.mean(x))
                errors.append(sem(x))
        self.progressbar.grid_forget()

        with open(f"Immune({p1},{p2},{p3}).txt", 'w') as outfile:
            out = ','.join(map(str, f_immune))+'\n'
            out += ','.join((map(str, infs)))+'\n'
            out += ','.join((map(str, errors)))

            outfile.write(out)
        sys.exit()


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
        self.labimcol = ttk.Label(self, text="Immune Colour")
        self.immuneColMenu = ttk.Combobox(self, values=self.colours)
        self.immuneColMenu.current(3)
        self.steps = tk.Scale(self, label="Display Steps", from_=500, to_=10_000, resolution=500, orient=tk.HORIZONTAL)
        self.steps.set(1000)
        self.measurements = tk.Scale(self, label="Measurement Sweeps", from_=100, to_=10_000, resolution=100,
                                     orient=tk.HORIZONTAL, length=150)
        self.measurements.set(100)
        self.precision = tk.Scale(self, label="Precision", from_=0.01, to_=1, resolution=0.01, orient=tk.HORIZONTAL,
                                  length=150)
        self.measurements.set(0.02)
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
        self.labimcol.grid(column=0, row=5)
        self.immuneColMenu.grid(column=1, row=5, columnspan=4)
        self.steps.grid(column=0, row=6, columnspan=2)
        self.measurements.grid(column=0, row=7, columnspan=2)
        self.precision.grid(column=0, row=8, columnspan=2)
        self.ApplyButton.grid(column=0, row=9, pady=50)
        self.params = {'x': int(self.ex.get()), 'y': int(self.ey.get()), 'bg_colour': self.BgColMenu.get(),
                       'fg_colour': self.ColMenu.get(), 'inf_colour': self.infMenu.get(),
                       'im_colour': self.immuneColMenu.get(), 'steps': int(self.steps.get()),
                       'measurements': int(self.measurements.get()), 'precision': float(self.precision.get())}

    def get_params(self):
        return self.params

    def apply_settings(self):
        self.params = {'x': int(self.ex.get()), 'y': int(self.ey.get()), 'bg_colour': self.BgColMenu.get(),
                       'fg_colour': self.ColMenu.get(), 'inf_colour': self.infMenu.get(),
                       'im_colour': self.immuneColMenu.get(), 'steps': int(self.steps.get()),
                       'measurements': int(self.measurements.get()), 'precision': float(self.precision.get())}


class GraphFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.graphs = ttk.Combobox(self, values=[], postcommand=self.update_options)
        self.plot_button = ttk.Button(self, text="Plot", command=self.plot)
        self.graphs.bind('<<ComboboxSelected>>', self.showdir)
        self.dir = EntryWithPlaceholder(self, "p1,p2,p3...")
        self.dir.configure(width=25)
        self.graphs.grid(row=0, column=0, pady=10)
        self.plot_button.grid(row=2, column=0)

    def showdir(self,event):
        choice = self.graphs.get()
        if choice == "Immunisations Plot":
            self.dir.grid(row=1, column=0)
        else:
            self.dir.grid_forget()

    def plot(self):
        choice = self.graphs.get()
        if choice == "Game of Life Histogram":
            self.game_of_life_hist()
        elif choice == "Game of Life Glider Plot":
            self.game_of_life_glider_plot()
        elif choice == "SIRS heat-map":
            self.SIRS_heatmap()
        elif choice == "SIRS contour":
            self.SIRS_contor()
        elif choice == "SIRS Variance Plot (0.2-0.5)":
            self.SIRS_var_plot()
        elif choice == "Immunisations Plot":
            self.plot_immunisations()

    def update_options(self):
        graphs = ["Immunisations Plot"]
        # check if the data for the histogram is available
        if os.path.isfile("equilibrium.txt"):
            graphs.append("Game of Life Histogram")
        # check if the centre of mass data is available
        if os.path.isfile("glidercom.txt"):
            graphs.append("Game of Life Glider Plot")
        # check if data for SIRS heatmap is available
        if os.path.isfile("SIRSMeasurements"):
            graphs.append("SIRS heat-map")
            graphs.append("SIRS contour")
        if os.path.isfile("SIRSVar.txt"):
            graphs.append("SIRS Variance Plot (0.2-0.5)")
        self.graphs['values'] = graphs

    def game_of_life_hist(self):
        with open("equilibrium.txt", 'r') as infile:
            times = list(map(int, infile.read().split(',')))
        plt.hist(times)
        plt.xlabel("Count")
        plt.ylabel("Time to complete (Steps)")
        plt.title("Number of Steps for Game of Life to Reach Equilibrium")
        plt.savefig('equilibrium.jpg')
        plt.show()

    def game_of_life_glider_plot(self):
        with open("glidercom.txt", 'r') as infile:
            data = infile.readlines()
            speed = float(data.pop(-1))
            xs = [int(p.split(',')[0]) for p in data]
            ys = [int(p.split(',')[1]) for p in data]
        plt.scatter(xs, ys)
        plt.xlabel("x-distance along grid")
        plt.ylabel("y-distance along grid")
        plt.title("Glider Centre-of-Mass")
        plt.show()

    def SIRS_heatmap(self):
        with open("SIRSMeasurements", 'rb') as infile:
            data = pickle.load(infile)
        xs = list(data)
        ys = list(data[0])
        im = [[data[x][y]['val'] for y in ys] for x in xs]
        plt.imshow(im)
        plt.xlabel("p1")
        plt.ylabel("p3")
        plt.title("SIRS p1-p3 Phase diagram")
        plt.savefig("SIRS Phase Diagram.jpg")
        plt.show()

    def SIRS_contor(self):
        with open("SIRSMeasurements",'rb') as infile:
            data = pickle.load(infile)
        xs = list(data)
        ys = list(data[0])
        zs = [[data[x][y]['var'] for y in ys] for x in xs]
        cs = plt.contour(xs, ys, zs)
        plt.clabel(cs,inline=1,fontsize=10)
        plt.xlabel("p1")
        plt.ylabel("p3")
        plt.title("SIRS contour")
        plt.savefig("SIRS Contour.jpg")
        plt.show()

    def SIRS_var_plot(self):
        with open("SIRSVar.txt", 'r') as infile:
            xs = list(map(float, infile.readline().split(',')))
            ys = list(map(float, infile.readline().split(',')))
            error = list(map(float, infile.readline().split(',')))
        plt.errorbar(xs, ys, yerr=error)
        plt.xlabel("p1")
        plt.ylabel("Infections variance")
        plt.title("Variance of infections over p1=[0.2-0.5]")
        plt.savefig("SIRS variance plot.jpg")
        plt.show()

    def plot_immunisations(self):
        ps = self.dir.get()
        with open(f"Immune({ps}).txt",'r') as infile:
            xs = list(map(float, infile.readline().split(',')))
            ys = list(map(float, infile.readline().split(',')))
            ys = [y/2500 for y in ys]
            error = list(map(float, infile.readline().split(',')))
            error = [e/2500 for e in error]
        plt.errorbar(xs, ys, yerr=error)
        plt.xlabel("Fraction of immune population")
        plt.ylabel("Number of infected")
        plt.title("Variation of Infections with Immunisation")

        plt.savefig(f"Infections-Immunisation{ps}.jpg")
        plt.show()


class Main(ttk.Notebook):

    def __init__(self, parent, *args, **kwargs):
        ttk.Notebook.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        Options = OptionsFrame(self, height=200, width=100)
        Game_Of_Life = GoLFrame(self, Options, height=200, width=100)
        SIRS = SIRSFrame(self, Options, height=200, width=100)
        Graphs = GraphFrame(self,height=200, width=100)

        self.add(Game_Of_Life, text="Game of Life")
        self.add(SIRS, text="SIRS")
        self.add(Graphs, text="Graphing")
        self.add(Options, text="Options")


def main():
    root = tk.Tk()
    tc = Main(root)
    tc.pack()
    root.resizable(False, False)
    root.mainloop()

if __name__ == "__main__":
    main()
