""""
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""
import os.path
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from tkinter.filedialog import askopenfile
import time
import uuid
from SDA_location import *
import PySimpleGUI as sg

def open_file():
    fileName = uuid.uuid4()
    file_path = askopenfile(mode='r', filetypes=[('CSV', '*csv')])
    file_path = file_path.name
    if file_path is not None:
        tf = open(file_path, 'r')
        data = tf.read()
        tw = open('../resources/{}.csv'.format(fileName),'w')
        tw.write(data)
        tw.close()
        return '../resources/{}.csv'.format(fileName)



def uploadFiles(filePathDNAC, filePathRooms):
    files = []
    newPaths = []
    files.append(filePathDNAC)
    files.append(filePathRooms)

    for x in files:
        fileName = uuid.uuid4()
        if x is not None:
            tf = open(x, 'r')
            data = tf.read()
            tw = open('../tmp/{}.csv'.format(fileName),'w')
            tw.write(data)
            tw.close()
            newPaths.append('../tmp/{}.csv'.format(fileName))

    return process_client_list(newPaths[0], newPaths[1])




def loadGUI():
    sg.theme("Default1")
    layout = [[sg.T("")],
            [sg.Text("DNAC Client .CSV"), sg.Input(key="-IN2-", change_submits=True), sg.FileBrowse(key="-IN3-")],
            [[sg.T("")],

            [sg.Text("MAC:Room .CSV "), sg.Input(key="-IN4-", change_submits=True), sg.FileBrowse(key="-IN5-")],
            [sg.Button("Submit")]],
            [[sg.T("", key='-FinalText-')]]]

    ###Building Window
    window = sg.Window('Kari\'s Law E911 GUI', layout, size=(600, 300))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            dirs = '../tmp'
            for f in os.listdir(dirs):
                os.remove(os.path.join(dirs, f))
            break
        elif event == "Submit":
            uploadFiles(values['-IN3-'], values['-IN5-'])
            window['-FinalText-'].update("Process completed, You may now close this window")

if __name__ == "__main__":
    loadGUI()