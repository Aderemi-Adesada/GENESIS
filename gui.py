from tkinter import *
from genesis import project_files_gen
from PIL import ImageTk, Image

root = Tk()
root.title('GENESIS')
root.iconbitmap('./icons/eaxum_icon.ico')

#create labels
label_gazu_host = Label(root, text='Host Url')
label_username = Label(root, text='Username')
label_password = Label(root, text='Password')
label_blender_dir = Label(root, text='Blender Directory')
label_project_name = Label(root, text='Project Name')

#display label
label_gazu_host.grid(row=0, column=0)
label_username.grid(row=1, column=0)
label_password.grid(row=2, column=0)
label_blender_dir.grid(row=3, column=0)
label_project_name.grid(row=4, column=0)

#create input box
input_gazu_host = Entry(root, width=50)
input_username = Entry(root, width=50)
input_password = Entry(root, width=50)
input_blender_dir = Entry(root, width=50)
input_project_name = Entry(root, width=50)

#display input box
input_gazu_host.grid(row=0, column=1)
input_username.grid(row=1, column=1)
input_password.grid(row=2, column=1)
input_blender_dir.grid(row=3, column=1)
input_project_name.grid(row=4, column=1)

#create run button
input_blender_dir.insert(0, "C:/Program Files/Blender Foundation/Blender 2.82/blender.exe")
input_gazu_host.insert(0, 'https://eaxum.cg-wire.com/api')
input_username.insert(0, 'aderemi@eaxum.com')
input_password.insert(0, 'efosadiya')
input_project_name.insert(0, 'tao')

button_run = Button(root, text='run programme', command=lambda: project_files_gen(
    username=input_username.get(),
    password=input_password.get(),
    gazu_host=input_gazu_host.get(),
    blender=input_blender_dir.get(),
    project_name=input_project_name.get()
))

#display button
button_run.grid(row=5, column=0, columnspan=2)





#set button

#display





root.mainloop()