from cgitb import text
import filecmp
import os


import os
import shutil
import tkinter as tk
from tkinter import StringVar, filedialog
from pathlib import Path
import json
import time
from pystray import MenuItem as item
import pystray
from PIL import Image
from threading import Thread
import sys

def copy_master(sink_from,sink_to , status_variable , master_kill_switch):
    for root , directory , files in os.walk(sink_from):
        for file in files:
            if(master_kill_switch == True):
                print('Kill Switch')
                return
            target_remote_file_path = os.path.join(root , file)
            stripped_remote_path = target_remote_file_path.split(sink_from+"\\")[1]
            possible_local_path = os.path.join(sink_to , stripped_remote_path)
            if(not os.path.exists(possible_local_path)):
                copy_to_dirname = os.path.dirname(possible_local_path)
                if(os.path.isdir(copy_to_dirname) == False):
                    os.makedirs(os.path.normpath(copy_to_dirname))
                shutil.copy2(target_remote_file_path , copy_to_dirname)
                status_variable.set(f"Copying...{os.path.basename(target_remote_file_path)} to {os.path.dirname(possible_local_path)}")
            elif(os.path.exists(possible_local_path)):
                #compare two files
                print(f"Comparing .. {os.path.basename(possible_local_path)} Remote {os.path.basename(target_remote_file_path)}")
                filecmp.clear_cache()
                if(filecmp.cmp(possible_local_path , target_remote_file_path)==False):
                    status_variable.set("Downloading again...."+os.path.basename(possible_local_path))
                    shutil.copy2(target_remote_file_path , possible_local_path)


def delete_master(sink_from,sink_to):
    for root , dirs , files in os.walk(sink_to):
        for file in files:
            local_path = os.path.join(root , file)
            stripped_local_path = local_path.split(sink_to+"\\")[1]
            possible_global_path = os.path.join(sink_from , stripped_local_path)
            if(not os.path.exists(possible_global_path)):
                os.remove(local_path)
        
        for dir in dirs:
            possible_empty_dir = os.listdir(os.path.join(root,dir))
            if(len(possible_empty_dir) == 0):
                os.rmdir(os.path.join(root , dir))





class Application(tk.Tk):
    def __init__(self):
        self.home_directory = str(Path.home())
        self.desktop_directory = os.path.join(self.home_directory , 'Desktop')
        self.json_db_location = os.path.join(self.desktop_directory , 'sinker.json')
        self.json_connection = None
        self.source_directory = None
        self.destination_directory = None
        self.sink_from = None
        self.sink_to = None
        tk.Tk.__init__(self)
        self.geometry('800x500')
        self.title('DDS-Sinker')
        
        select_sink_from_button = tk.Button(text='Source Directory' , command= self.select_sink_from)
        select_sink_from_button.pack()

        select_sink_to_button = tk.Button(text='Destination Directory' , command= self.select_sink_to)
        select_sink_to_button.pack()

        select_start_sink_button = tk.Button(text="Start Sync",command= self.start_sink)
        select_start_sink_button.pack()

        self.status_variable = StringVar()
        status_label = tk.Label(textvariable=self.status_variable)
        status_label.pack()

        self.master_kill_switch = False
        self.runner_thread = None

        if(os.path.exists(self.json_db_location)):
            self.json_connection = open(self.json_db_location,'r')
            json_db = json.load(self.json_connection)
            try:
                if(not os.path.exists(json_db['sink_from']) or os.path.exists(json_db['sink_to'])):
                    print('valid locations detected')
                    self.sink_from = json_db['sink_from']
                    self.sink_to = json_db['sink_to']
                    self.run_infinitely()
            except Exception as e:
                print(e)
                pass

        else:
            print('Database Missing')

    def select_sink_from(self):
        self.source_directory = tk.filedialog.askdirectory()

    def select_sink_to(self):
        self.destination_directory = tk.filedialog.askdirectory()

    def start_sink(self):
        if(self.source_directory or self.destination_directory !=None):
            self.json_connection = open(self.json_db_location , 'w')
            sink_locations = {'sink_from' : self.source_directory , 'sink_to':self.destination_directory}
            json.dump(sink_locations , self.json_connection)
            self.json_connection.close()

            self.sink_from = self.source_directory
            self.sink_to = self.destination_directory

            self.run_infinitely()

    def show_popup(self):
        self.run_main_loop()

    def run_thread(self):
        print('Thread Started')
        while(self.master_kill_switch == False):
            delete_master(sink_from=self.sink_from , sink_to=self.sink_to)
            copy_master(sink_from=self.sink_from , sink_to=self.sink_to , status_variable=self.status_variable , master_kill_switch=self.master_kill_switch)
            delete_master(sink_from=self.sink_from , sink_to=self.sink_to)
            time.sleep(2)

    def run_infinitely(self):
        self.runner_thread = Thread(target=self.run_thread)
        self.runner_thread.start()

    def kill_thread(self):
        print('Killing thread now')
        self.master_kill_switch = True
        self.runner_thread.join()
    
    def run_main_loop(self):
        pass


app = Application()
window = app

def quit_window(icon, item):
    icon.stop()
    print('Quit Window')
    window.kill_thread()
    window.destroy()
    sys.exit()

def show_window(icon, item):
    icon.stop()
    window.after(0,window.deiconify)

def withdraw_window():  
    window.withdraw()
    image = Image.new(mode = "RGB", size = (200,70), color = "red")
    menu = (item('Quit', quit_window), item('Show', show_window))
    icon = pystray.Icon("name", image, "title", menu)
    icon.run()

window.protocol('WM_DELETE_WINDOW', withdraw_window)
window.mainloop()
