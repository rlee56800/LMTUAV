from tkinter import *
from tokenize import String
from turtle import width
import UAV

master = Tk(className="Graph Options")


########## VARS ########## 
textbox_width = 70
graph_name = StringVar(master)
file_name = StringVar(master)
predicted_indices = StringVar(master)


########## FUNCTIONS ########## 
def enter_info():
    #print(graph_name.get(), file_name.get(), predicted_indices.get())
    if not file_name.get(): # if no file is given
        error = Tk(className='Error')
        Label(error, text='Please enter a file name').grid(column=0, row=0)
        error.mainloop()

    try:
        UAV.main(graph_name.get(), file_name.get())#, predicted_indices.get())
    except FileNotFoundError:
        error = Tk(className='Error')
        Label(error, text='Please enter a VALID file name').grid(column=0, row=0)
        error.mainloop()

########## GUI ########## 

# graph_name: str
Label(master, text = 'Title of Graph: (str) ').grid(column=0, row=1, padx=5, pady=5)
e_graph = Entry(master, width=textbox_width, textvariable=graph_name)
e_graph.grid(column=1, row=1, padx=5, pady=5)

# file_name: str
Label(master, text = 'Name of File (containing data): ').grid(column=0, row=2, padx=5, pady=5)
e_file = Entry(master, width=textbox_width, textvariable=file_name)
e_file.grid(column=1, row=2, padx=5, pady=5)

# predicted_indices: list[int]
# Label(master, text = 'Index/Indices Showing Predicted Path').grid(column=0, row=3, padx=5, pady=5)
# e_indices = Entry(master, width=textbox_width, textvariable=predicted_indices)
#e_indices.grid(column=1, row=3, padx=5, pady=5)

confirm = Button(master, text='Create Graph', command=enter_info).grid(column = 0, row=4)


master.mainloop()