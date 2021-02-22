import tkinter as tk
from tkinter import ttk
from matplotlib import colors
from GameOfLife import GameOfLife
from matplotlib import pyplot as plt
class GoLFrame(tk.Frame):
    def __init__(self, parent,Options, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.O = Options
        self.l = ttk.Label(self,text="Initalise with:")
        self.methods = ["Random","Beehive","Blinker","Glider"]
        self.choices = ttk.Combobox(self,values=self.methods)
        self.choices.current(0)
        self.Run = ttk.Button(self,text="Run",command=self.begin)
        self.mlabel = ttk.Label(self,text="Measure equilibriums\nWARNING: can take some time")
        self.mbutton = ttk.Button(self,text="Measure",command=self.measure)
        self.l.grid(column=0,row=0)
        self.choices.grid(column=0,row=1)
        self.mlabel.grid(column=0,row=2,pady=20)
        self.mbutton.grid(column=0,row=3)
        self.Run.grid(column=0,row=4,pady=20)

    def measure(self):
        params = self.O.get_params()
        steps = []
        for i in range(params['measurements']):
            G = GameOfLife((params['x'],params['y']))
            G.randomise()
            steps.append(G.find_equilibrium(1))
            print(f"{i}/{params['measurements']}")
        with(open('measurements.txt','w') as outfile):
            outfile.write(','.join(map(str,steps)))
        


    def begin(self):
        params = self.O.get_params()
        G = GameOfLife((params['x'],params['y']))
        #choose method to initalise the CA with
        switch = self.choices.get()
        if(switch == "Random"):
            G.randomise()
        elif(switch == "Beehive"):
            G.beehive()
        elif(switch == "Blinker"):
            G.blinker()
        else:
            G.glider()
        G.animate(params['fg_colour'],params['bg_colour'],params['steps'],"Game of Life")


class SIRSFrame(tk.Frame):
    def __init__(self, parent,Options, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent

class OptionsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent
        self.colours = list(colors.CSS4_COLORS)
        self.labx = ttk.Label(self,text="Grid X")
        self.laby = ttk.Label(self,text="Grid Y")
        self.ex = ttk.Entry(self,width="5")
        self.ex.insert(0,"50")
        self.ey = ttk.Entry(self,width="5")
        self.ey.insert(0,"50")
        self.labcol = ttk.Label(self,text="Cell colour")
        self.ColMenu = ttk.Combobox(self,values=self.colours)
        self.ColMenu.current(1)
        self.labbgcol = ttk.Label(self,text="Background colour")
        self.BgColMenu = ttk.Combobox(self,values=self.colours)
        self.BgColMenu.current(0)
        self.steps = tk.Scale(self,label="#Steps",from_=0,to_=10_000,resolution=500,orient=tk.HORIZONTAL)
        self.steps.set(1000)
        self.measurements = tk.Scale(self,label="#Measurements",from_=0,to_=1000,resolution=100,orient=tk.HORIZONTAL)
        self.measurements.set(100)
        self.ApplyButton = ttk.Button(self,text="Apply",command=self.update)
        self.labx.grid(column=0,row=0)
        self.ex.grid(column=1,row=0,padx=5)
        self.laby.grid(column=2,row=0)
        self.ey.grid(column=3,row=0)
        self.labcol.grid(column=0,row=1,pady=40)
        self.ColMenu.grid(column=1,row=1,columnspan=4)
        self.labbgcol.grid(column=0,row=2)
        self.BgColMenu.grid(column=1,row=2,columnspan=4)
        self.steps.grid(column=0,row=3,columnspan=2)
        self.measurements.grid(column=0,row=4,columnspan=2)
        self.ApplyButton.grid(column=0,row=5,pady=50)
        self.params = {'x':int(self.ex.get()),'y':int(self.ey.get()),'bg_colour':self.BgColMenu.get(),'fg_colour':self.ColMenu.get(),'steps':int(self.steps.get()),'measurements':int(self.measurements.get())}
    
    def get_params(self):
        return self.params

    def update(self):
        self.params = {'x':int(self.ex.get()),'y':int(self.ey.get()),'bg_colour':self.BgColMenu.get(),'fg_colour':self.ColMenu.get(),'steps':int(self.steps.get()),'measurements':int(self.measurements.get())}



class Main(ttk.Notebook):

    def __init__(self, parent, *args, **kwargs):
        ttk.Notebook.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        Options = OptionsFrame(self,height=200,width=100)
        Game_Of_Life = GoLFrame(self,Options,height=200,width=100)
        SIRS = SIRSFrame(self,Options,height=200,width=100)


        self.add(Game_Of_Life,text="Game of Life")
        self.add(SIRS,text="SIRS")
        self.add(Options,text="Options")



def main():
    root = tk.Tk()
    tc = Main(root)
    tc.pack()
    root.resizable(False, False)
    root.mainloop()

main()
