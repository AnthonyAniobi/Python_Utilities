class PdfTranslator :
    def __init__(self, path:str) -> None:
        pass

    def read_cli(self):
        pass

    def read_gui(self):
        pass
# import os
# import tkinter
# import tkinter.ttk as ttk
# root = tkinter.Tk()
# root.configure(background='black')
# # style configuration
# style = ttk.Style(root)
# style.configure('TLabel', background='black', foreground='white')
# style.configure('TFrame', background='white')
# frame = ttk.Frame(root)
# frame.grid(column=0, row=0)
# ttk.Button(frame, text="Open file", command=None).grid(column=0, row=1)
# lab = ttk.Label(frame, text="test test test test test test ")
# lab.grid(column=0, row=2)
# root.mainloop()
import tkinter

def func1():
   win = tkinter.Tk()
   win.geometry("300x200")
   win.configure(bg='blue')
   button_win = tkinter.Button(win,text='Go',command=lambda:func2(win))
   button_win.pack()
   win.mainloop()

def func2(win):
   win.configure(bg = 'green')
   win.after(5000,lambda:func3(win))

def func3(win):
   win.configure(bg = 'yellow')

func1()