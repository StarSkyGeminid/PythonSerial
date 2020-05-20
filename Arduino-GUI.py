#!/usr/bin/python3

import os
import re
import json
import time
import serial
import threading
import serial.tools.list_ports

import tkinter as tk

from queue   import Empty
from tkinter import ttk
from tkinter import *

os.system("clear")
gui = Tk()

var_vibsens = StringVar()
var_hum     = StringVar()
var_tem     = StringVar()
var_red     = IntVar()
var_green   = IntVar()
var_blue    = IntVar()

vibration_sensor   = None
temperature_sensor = None
humidity_sensor    = None
serial_set         = None

scale_length = 370
new_time     = 0

class Arduino_Connection:
    def __init__(self, master):

        self.master = Frame(master, borderwidth = 2, relief = "groove")
        self.master.place(x = 0, y = 475, height = 25, width = 500)
        self.Json_Data_Update = Arduino_Json(self.master)

        port = serial.tools.list_ports.comports()

        self.serial_port = ttk.Combobox(self.master, values = port)
        self.serial_baud = ttk.Combobox(self.master, width = 10)
        self.button_connect = Button(self.master, text = "Connect", command = self.Arduino_Connect, width = 10, pady = -10)
        self.button_disconenct = Button(self.master, text = "Disconnect", command = self.Arduino_Disconnect, width = 9, pady = -10)

        self.serial_baud['values'] = (300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 74880, 115200)

        self.button_disconenct.place(x = 0, y = 0)
        self.button_connect.place(x = 390, y = 0) 
        self.serial_baud.place(x = 290, y = 0)
        self.serial_port.place(x = 100, y = 0)

        if bool(port):
                    self.serial_port.current(0)
                    self.serial_baud.current(4)

    def Arduino_Connect(self):
        global serial_set
        selected_port = re.findall("/dev/ttyACM[0-9]", self.serial_port.get())
        self.serial_set = serial.Serial(selected_port[0], self.serial_baud.get(), timeout = 1)
        if self.serial_set.isOpen():
            Arduino_GUI(self.serial_set)
            serial_set = self.serial_set
            self.Json_Data_Update.Start_Threading(self.serial_set)

    def Arduino_Disconnect(self):
        gui.destroy()

class Arduino_GUI:
    def __init__(self, serial_set):

        self.master1 = Frame(gui, borderwidth = 2, relief = "groove")
        self.master2 = Frame(gui, borderwidth = 2, relief =  "groove")
        self.master1.place(x = 0, y = 0,  height = 80, width  = 500)
        self.master2.place(x = 0, y = 90, height = 200, width = 500)

        self.serial_set = serial_set
        self.Arduino_Set = Arduino_Set(self.serial_set)
        
        self.sensor()
        self.adj_led()


    def sensor(self):
        global vibration_sensor
        global humidity_sensor
        global temperature_sensor

        vibration_sensor   = Label(self.master1, width = 20)
        humidity_sensor    = Label(self.master1, width = 20)
        temperature_sensor = Label(self.master1, width = 20)

        vibration_sensor.pack()
        humidity_sensor.pack()
        temperature_sensor.pack()

    def adj_led(self):
        tk.Label(self.master2, text = "Red  ", width = 5, bg = "#FF0000", fg = "#000000").place(x = 10, y = 30)
        tk.Label(self.master2, text = "Green", width = 5, bg = "#00FF00", fg = "#000000").place(x = 10, y = 75)
        tk.Label(self.master2, text = "Blue ", width = 5, bg = "#0000FF", fg = "#000000").place(x = 10, y = 120)
        
        self.scale_red   = Scale(self.master2, orient = HORIZONTAL, from_ = 0, to = 255, variable = var_red,   length = scale_length)
        self.scale_green = Scale(self.master2, orient = HORIZONTAL, from_ = 0, to = 255, variable = var_green, length = scale_length)
        self.scale_blue  = Scale(self.master2, orient = HORIZONTAL, from_ = 0, to = 255, variable = var_blue,  length = scale_length) 

        self.entry_red   = Entry(self.master2, textvariable = var_red, width = 5)
        self.entry_green = Entry(self.master2, textvariable = var_green, width = 5)
        self.entry_blue  = Entry(self.master2, textvariable = var_blue, width = 5)

        self.scale_red.place(  x = 70,  y = 8)
        self.scale_green.place(x = 70,  y = 54)
        self.scale_blue.place( x = 70,  y = 98)
        self.entry_red.place(  x = 430, y = 28)
        self.entry_green.place(x = 430, y = 74)
        self.entry_blue.place( x = 430, y = 118)

        self.submit_button = Button(self.master2, text = "Submit ", command = self.bar_auto_adj)
        self.led_off       = Button(self.master2, text = "Led OFF", command = self.Arduino_Set.led_off)

        self.submit_button.place(x = 170, y = 150)
        self.led_off.place(      x = 270, y = 150)

    def bar_auto_adj(self):
        self.Arduino_Set.led_threading()

class Arduino_Set:
    def __init__(self, serial_set):
        self.serial_set = serial_set
        self.master     = gui
        self.last_red   = 0
        self.last_green = 0
        self.last_blue  = 0
        self.new_time   = 0

    def led_threading(self):
        self.serial_set = serial_set
        self.thread2 = threading.Thread(target = self.led_set)
        self.thread2.start()

    def led_set(self):
        self.new_time
        while(1):
            if time.time() - new_time >= 50:
                if var_red != self.last_red:
                    self.serial_set.write(bytes('merah'+str(var_red.get())+'\n', "utf-8"))
                    self.last_red = var_red.get()
                if var_green != self.last_green:
                    self.serial_set.write(bytes('hijau'+str(var_green.get())+'\n', "utf-8"))
                    self.last_green = var_green.get()
                if var_blue != self.last_blue:
                    self.serial_set.write(bytes('biru'+str(var_blue.get())+'\n', "utf-8"))
                    self.last_blue = var_blue.get()
                self.new_time = time.time()

    def led_off(self):
        var_red.set(0)
        var_green.set(0)
        var_blue.set(0)
        self.serial_set.write(bytes('ledoff\n', "utf-8"))

class Arduino_Json:
    def __init__(self, master):
        self.master     = master
        self.running    = 1

    def Start_Threading(self, serial_set):
        self.serial_set = serial_set
        self.thread1 = threading.Thread(target = self.Thread_queue)
        self.thread1.start()

    def Thread_queue(self):
        global vibration_sensor
        global humidity_sensor
        global temperature_sensor

        while self.running:
            try:
                data_json = self.serial_set.readline().decode("ascii")
                if bool(re.findall("{.*}", data_json)):
                    try:
                        v_sensor = json.loads(data_json)['vib_sens']
                        vibration_sensor["text"] = "Vibration : "+v_sensor

                    except:
                        h_sensor = json.loads(data_json)['hum']
                        t_sensor = json.loads(data_json)['tem']

                        humidity_sensor["text"] = "Humidity : "+h_sensor+"%"
                        temperature_sensor["text"] = "Temperature :"+t_sensor+"°C"
            except:
                pass
           
if __name__ == "__main__":

    Arduino_Connection(gui)
    gui.geometry("500x500")
    gui.mainloop()
