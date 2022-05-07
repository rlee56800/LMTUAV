# TODO: graph waypoints (find + print wp to log output)

from tkinter import *
from tkinter import colorchooser
from tkinter import ttk
import UAV

master = Tk(className="Graph Options")

########## VARS ########## 
textbox_width = 70
graph_name = StringVar(master)
file_name = StringVar(master)
predicted_indices = StringVar(master)
plot_point_long = StringVar(master)
plot_point_lat = StringVar(master)
plot_points = StringVar(master)
map_intruder = IntVar(master)
predicted_collision_point = StringVar(master)
pp_list = []
pc_list = []

# https://www.geeksforgeeks.org/python-tkinter-checkbutton-widget/

########## FUNCTIONS ########## 
def enter_info():
    #print(graph_name.get(), file_name.get(), predicted_indices.get())
    if not file_name.get(): # if no file is given
        show_error('Please enter a file name')
    
    if predicted_indices.get():
        try:
            pi_list = [int(i) for i in predicted_indices.get().split(' ')]
        except ValueError:
            show_error('Only numbers may be indices')
    else:
        pi_list = []

    try:
        UAV.main(graph_name.get(), file_name.get(), map_intruder.get(), pi_list, pp_list, pc_list)
    except FileNotFoundError:
        show_error('Please enter a VALID file name', '(including parent folder and .txt on the end and excluding quotation marks)')
    except IndexError:
        show_error('Point specified is out of bounds')

def show_error(error_msg: str, error_msg2: str = ''):
    error = Tk(className='Error')
    Label(error, text=error_msg).grid(column=0, row=0)
    if error_msg2:
        Label(error, text=error_msg2).grid(column=0, row=1)
    error.mainloop()
    
def append_coord():
    if plot_point_long.get() and plot_point_lat.get():
        color_code = colorchooser.askcolor(title="Choose color")
        pp_list.append([plot_point_long.get(), plot_point_lat.get(), color_code[1]])
        print(pp_list)
        e_pp_longitude.delete(0, END)
        e_pp_lattitude.delete(0, END)

def get_combo_values():
    if file_name.get():
        a['state']='readonly'
        lst = UAV.predicted_collision_points_dropdown(file_name.get())
        a.config(value=lst)
    else:
        a['state'] = 'disabled'

def add_collision_point():
    pc_list.append(predicted_collision_point.get())
    print(pc_list)

def remove_collision_point():
    pc_list.remove(predicted_collision_point.get())
    print(pc_list)

########## GUI ##########

# graph_name: str
Label(master, text = 'Title of Graph:').grid(column=0, row=1, padx=5, pady=5)
e_graph = Entry(master, width=textbox_width, textvariable=graph_name)
e_graph.grid(column=1, row=1, padx=5, pady=5)

# file_name: str
Label(master, text='Name of File:').grid(column=0, row=2, padx=5, pady=5)
e_file = Entry(master, width=textbox_width, textvariable=file_name)
e_file.grid(column=1, row=2, padx=5, pady=5)

# predicted_indices: list[int]
Label(master, text='Index of Point(s) Showing Predicted Path:\n(separate with spaces)').grid(column=0, row=3, padx=5, pady=5)
e_indices = Entry(master, width=textbox_width, textvariable=predicted_indices)
e_indices.grid(column=1, row=3, padx=5, pady=5)

'''
Plot points begin
'''
plot_points_frame = LabelFrame(master, text="Plot Points")
plot_points_frame.grid(row=4, columnspan=3, ipadx=30, ipady=2)

# longitude: list[int]
Label(plot_points_frame, text='Longitude').grid(column=0, row=0, padx=5, pady=5)
e_pp_longitude = Entry(plot_points_frame, width=textbox_width, textvariable=plot_point_long)
e_pp_longitude.grid(column=1, row=0, padx=5, pady=5)

# lattitude: list[int]
Label(plot_points_frame, text='Lattitude').grid(column=0, row=1, padx=5, pady=5)
e_pp_lattitude = Entry(plot_points_frame, width=textbox_width, textvariable=plot_point_lat)
e_pp_lattitude.grid(column=1, row=1, padx=5, pady=5)

# add point button
add_point = Button(plot_points_frame, text='Add Point', command=append_coord).grid(column = 3, row=1)
'''
Plot points end
'''

'''
Predicted collision points begin
'''
predicted_collision_frame = LabelFrame(master, text="Predicted Collision Points")
predicted_collision_frame.grid(row=5, columnspan=2, ipadx=0, ipady=2)

Label(predicted_collision_frame, text='Point List').grid(column=0, row=0, padx=5, pady=5)

a = ttk.Combobox(predicted_collision_frame, textvariable=predicted_collision_point, state='readonly', postcommand=get_combo_values, width=textbox_width)
a.grid(column=1, row=0, padx=5, pady=5)

add_predicted_col_point = Button(predicted_collision_frame, text='Add Point', command=add_collision_point)
add_predicted_col_point.grid(column=2, row=0, padx=5, pady=5)

add_predicted_col_point = Button(predicted_collision_frame, text='Delete', command=remove_collision_point)
add_predicted_col_point.grid(column=3, row=0, padx=5, pady=5)
'''
Predicted collision points begin
'''

# map_intruder: bool
# checkbox for whether or not intruder is mapped
e_intruder = Checkbutton(master, text = 'Map intruder vehicle?', variable = map_intruder, onvalue=1, offvalue=0)
e_intruder.grid(column=0, row=6, padx=5, pady=5)

# confirmation button
confirm = Button(master, text='Create Graph', command=enter_info).grid(column = 0, row=7)


master.mainloop()