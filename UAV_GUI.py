from tkinter import *
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
        show_error('Please enter a file name')
    
    try:
        pi_list = [int(i) for i in predicted_indices.get().split(' ')]
    except ValueError:
        show_error('Only numbers may be indices')

    try:
        UAV.main(graph_name.get(), file_name.get(), pi_list)
    except FileNotFoundError:
        show_error('Please enter a VALID file name', '(including parent folder and .txt on the end and excluding quotation marks)')
    except IndexError:
        show_error('Predicted index is out of bounds')

def show_error(error_msg: str, error_msg2: str = ''):
    error = Tk(className='Error')
    Label(error, text=error_msg).grid(column=0, row=0)
    if error_msg2:
        Label(error, text=error_msg2).grid(column=0, row=1)
    error.mainloop()

########## GUI ########## 

# graph_name: str
Label(master, text = 'Title of Graph:').grid(column=0, row=1, padx=5, pady=5)
e_graph = Entry(master, width=textbox_width, textvariable=graph_name)
e_graph.grid(column=1, row=1, padx=5, pady=5)

# file_name: str
Label(master, text = 'Name of File: ').grid(column=0, row=2, padx=5, pady=5)
e_file = Entry(master, width=textbox_width, textvariable=file_name)
e_file.grid(column=1, row=2, padx=5, pady=5)

# predicted_indices: list[int]
Label(master, text = 'Index/Indices Showing Predicted Path (separate with spaces)').grid(column=0, row=3, padx=5, pady=5)
e_indices = Entry(master, width=textbox_width, textvariable=predicted_indices)
e_indices.grid(column=1, row=3, padx=5, pady=5)

confirm = Button(master, text='Create Graph', command=enter_info).grid(column = 0, row=4)


master.mainloop()