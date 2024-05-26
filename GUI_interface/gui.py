import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import cv2
# import self as self
import wmi as wmi
import pythoncom
import os
from datetime import datetime
from PIL import ImageTk, Image
from tkcalendar import DateEntry
from ultralytics import YOLO
import time
import warnings
import subprocess
import shutil
import webbrowser
import sys
import pandas as pd
from pycomm3 import LogixDriver

# Creating database ----------------------------------------------------------------------------------------------------


plc_status = False
plc_status_count = 0

conveyor_status = True  # to be reviewed
confirmation_of_no_tyres_jam = 0
detected_feed = []


def plc_trigger_thread_override(data_to_send):
    global plc_status, plc_status_count
    target_ip = '172.22.17.10'
    custom_port = 2222
    data_path = 'TYRE_JAM_UP_DETECTED'
    with LogixDriver(target_ip, port=custom_port) as plc:
        try:
            txt = open("log.txt", 'a')
            txt.write(f"Plc Triggered with value in overide : {data_to_send} \n")
            txt.close()
            plc.write(data_path, data_to_send)

        except Exception as e:
            print()
        finally:
            plc.close()


def plc_trigger_thread(data_to_send, cam_name="", jam_count="", screenshot_location=""):
    global plc_status, plc_status_count
    target_ip = '172.22.17.10'
    custom_port = 2222
    data_path = 'TYRE_JAM_UP_DETECTED'
    if plc_status_count == 0 and data_to_send:
        plc_status_count += 1
        detected_feed.append(cam_name)
        with LogixDriver(target_ip, port=custom_port) as plc:
            try:
                txt = open("log.txt", 'a')
                txt.write(f"Plc Triggered with value : {data_to_send} \n")
                txt.close()
                plc.write(data_path, data_to_send)
                insert_record(cam_name, jam_count, screenshot_location)

            except Exception as e:
                txt = open("log.txt", 'a')
                txt.write(f'PLC Trigger Error {e} \n')
                txt.close()
            finally:
                plc.close()

    elif plc_status_count == 1 and not data_to_send:
        plc_status_count += 1
        with LogixDriver(target_ip, port=custom_port) as plc:
            try:
                txt = open("log.txt", 'a')
                txt.write(f"Plc Triggered with value : {data_to_send} \n")
                txt.close()
                plc.write(data_path, data_to_send)

            except Exception as e:
                txt = open("log.txt", 'a')
                txt.write(f'PLC Trigger Error {e} \n')
                txt.close()
            finally:
                plc.close()

    if plc_status_count == 2 and plc_status_count != 0:
        plc_status = True
        plc_status_count = 0


def plc_trigger(data_to_send, cam_name="", jam_count="", screenshot_location=""):
    threading.Thread(target=plc_trigger_thread, args=(data_to_send, cam_name, jam_count, screenshot_location)).start()


def plc_trigger_override(data_to_send):
    threading.Thread(target=plc_trigger_thread_override, args=(data_to_send,)).start()


def conveyor_read():
    global conveyor_status
    while True:
        with LogixDriver('172.22.17.10', port=2222) as plc:
            try:
                plc.open()
                data = plc.read("TRENCH_CONVEYOR1_RUNNING")
                data = list(data)
                conveyor_status = data[1]
            except Exception as e:
                txt = open("log.txt", 'a')
                txt.write(f'line 447 error {e} \n')
                txt.close()
            finally:
                plc.close()


con_read = threading.Thread(target=conveyor_read)
con_read.start()


def create_database_and_tables():
    # Connect to SQLite database (creates it if not exists)
    conn = sqlite3.connect('config.db')
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    # Check if users table exists
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='users' ''')
    users_table_exists = cursor.fetchone()

    # Check if cameras table exists
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='cameras' ''')
    cameras_table_exists = cursor.fetchone()
    check = 0
    # Create users table if not exists
    if not users_table_exists:
        cursor.execute('''CREATE TABLE users (
                            id INTEGER PRIMARY KEY,
                            username TEXT UNIQUE,
                            password TEXT,
                            uuid TEXT DEFAULT 0,
                            initial_state INTEGER DEFAULT 0
                        )''')

    # Create cameras table if not exists
    if not cameras_table_exists:
        cursor.execute('''CREATE TABLE cameras (
                            id INTEGER PRIMARY KEY,
                            ip1 TEXT,
                            ip2 TEXT,
                            ip3 TEXT,
                            ip4 TEXT,
                            plcip TEXT,
                            plcport INTEGER,
                            jam_check_time INTEGER
                        )''')

    # Commit changes and close connection
    cursor.execute('''CREATE TABLE IF NOT EXISTS records
                      (id INTEGER PRIMARY KEY,
                       camera TEXT,
                       screenshot_location TEXT,
                       timestamp TEXT,
                       No_of_Tyres_Jammed INTEGER(20))''')
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='model' ''')
    model_table_exists = cursor.fetchone()
    if not model_table_exists:
        check = 1
    cursor.execute('''CREATE TABLE IF NOT EXISTS model (
                        model_1 TEXT,
                        model_2 TEXT,
                        model_3 TEXT,
                        model_4 TEXT 
                    )''')
    if check == 1:
        model_data = ('models\\1.pt', 'models\\2.pt', 'models\\3.pt', 'models\\4.pt')
        cursor.execute('''INSERT INTO model (model_1, model_2, model_3, model_4) VALUES (?, ?, ?, ?)''', model_data)
    conn.commit()
    conn.close()


def create_table():
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('rtsp://c1', 'location1.jpg', '2024-03-08 10:00:00', 3)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('rtsp://c2', 'location2.jpg', '2024-03-08 10:05:00', 2)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('rtsp://c3', 'location3.jpg', '2024-03-08 10:10:00', 1)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                      VALUES ('rtsp://c4', 'https://sqliteviewer.app/#/config.db/table/users/', '2024-03-08 10:15:00', 4)''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('config.db')
    conn.row_factory = sqlite3.Row
    return conn


def login_post(user, password_1):
    username = user
    password = password_1

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the username exists in the database
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()

        if user:
            user_password = user_row['password']
            if user_password == password:
                # Passwords match, redirect to the next page
                print("Password correct")
                return True
            else:
                return False
        else:
            print("User not found in the database")
            return False
    except Exception as e:
        print("Error:", e)
        return False
    finally:
        conn.close()


def get_system_id():
    try:
        # Initialize the COM library
        pythoncom.CoInitialize()

        # Connect to Windows Management Instrumentation (WMI)
        c = wmi.WMI()

        # System UUID (Universally Unique Identifier)
        for system in c.Win32_ComputerSystemProduct():
            system_info = system.UUID
            print(system_info)

    except Exception as e:
        print(f"Error: {e}")
        system_info = "0"

    finally:
        # Uninitialize the COM library
        pythoncom.CoUninitialize()

    return system_info


def add_uuid_to_users(uuid, username):
    # Connect to SQLite database
    print("added uuid")
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    # Update the row corresponding to the username with the UUID
    cursor.execute('''UPDATE users SET uuid = ?, initial_state = 0 WHERE username = ?''', (uuid, username))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"UUID '{uuid}' added to users table for username '{username}' with initial state 0.")


def check_uuid_and_initial_state(uuid, username):
    # Connect to SQLite database
    print("Checking uuid.........")
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    print(uuid)
    # Check if UUID exists in users table
    cursor.execute('''SELECT uuid, initial_state FROM users WHERE uuid = ?''', (uuid,))
    user_data = cursor.fetchone()

    # Close connection
    conn.close()

    if user_data is None:
        # If UUID not found, add it to the table with initial_state as 0
        add_uuid_to_users(uuid, username)
        return "Load"
        # return render_template("load.html")  # Redirect to load.html
    else:
        _, initial_state = user_data
        if initial_state == 1:
            return "Live"
            # return render_template("live_feed.html")  # Redirect to live_feed.html
        else:
            return "Load"  # Redirect to load.html


def update_initial_state(uuid, new_state):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Update initial state for the given username
    cursor.execute('''UPDATE users SET initial_state = ? WHERE uuid = ?''', (new_state, uuid))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Initial state for user '{uuid}' updated successfully.")


def store_camera_ips(ip1, ip2, ip3, ip4, plcip, plcport):
    # Connect to SQLite database
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()

    # Insert IP addresses into the cameras table
    cursor.execute('''INSERT INTO cameras (ip1, ip2, ip3, ip4, plcip, plcport)
                      VALUES (?, ?, ?, ?, ?, ?)''', (ip1, ip2, ip3, ip4, plcip, plcport))

    # Commit changes and close connection
    conn.commit()
    conn.close()


def retrieve_ip(camera):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    if camera == 0:
        cursor.execute("""
                SELECT ip1  
                FROM cameras
                LIMIT 1
            """)
    elif camera == 1:
        cursor.execute("""
                SELECT ip2
                FROM cameras
                LIMIT 1
            """)
    elif camera == 2:
        cursor.execute("""
                SELECT ip3 
                FROM cameras
                LIMIT 1
            """)
    elif camera == 3:
        cursor.execute("""
                SELECT ip4  
                FROM cameras
                LIMIT 1
            """)
    else:
        print("Camera limit exceed")

    ip = cursor.fetchone()
    print(ip)  # Fetching one IP address
    conn.close()
    return ip[0] if ip else None


def insert_record(camera, no_of_tyres_jammed, screenshot_location=""):
    if camera == "" or no_of_tyres_jammed == "":
        return
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    timestamp = datetime.now()
    # target_directory = 'images'
    # if not os.path.exists(target_directory):
    #     os.makedirs(target_directory)
    # Get the filename from the image path
    sql_command = '''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                        VALUES (?, ?, ?, ?)'''
    cursor.execute(sql_command, (camera, screenshot_location, timestamp, no_of_tyres_jammed))
    conn.commit()
    conn.close()


def retrieve_jam_check_time():
    try:
        conn = sqlite3.connect('config.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cameras LIMIT 1")
        row = cursor.fetchone()
        if row:
            index_of_jam_check_time = cursor.description.index(('jam_check_time', None, None, None, None, None, None))
            jam_check_time = row[index_of_jam_check_time]
            print(jam_check_time, "adaf")
            if (jam_check_time == None or jam_check_time == ''):
                jam_check_time = 40
            return int(jam_check_time)
        else:
            return 40
    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        if conn:
            conn.close()


# ----------------------------------------------------------------------------------------------------------------------
create_database_and_tables()
create_table()


class Detection:
    def __init__(self, video_path):
        self.jam_confirmed_count = 0
        self.jam_confirmed_limit = 3
        self.id_check_time = 5
        _time = retrieve_jam_check_time() // 2
        self.jam_check_time = _time
        self.jam_confirm_time = _time
        self.id_confirm_time = 10
        self.tyre_management = {}
        self.jam_management = {}
        self.id_management = {}
        self.last_frame = []
        self.tracking_lineFront = [43, 54, 68, 91, 115, 152, 196, 263]
        self.tracking_lineBack = [250, 196, 155, 128, 101, 74, 61, 47]
        self.frame_number = None
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        if video_path != None:
            self.cam_name = video_path + "_Camera"

    def create_capture(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        return self.cap

    def set_model(self, model_path):
        try:
            self.model = YOLO(model_path)
        except Exception:
            warnings.warn("Could not find the specified model. Loaded default model")
            self.model = YOLO("models/4.pt")

    def delete_id(self, id):
        if id in self.id_management:
            del self.id_management[id]

    def delete_jam(self, id):
        if id in self.jam_management:
            if self.jam_management[id]['is jam confirmed']:
                self.jam_confirmed_count -= 1
            del self.jam_management[id]

    def delete_tyre(self, id):
        del self.tyre_management[id]
        self.delete_id(id)
        self.delete_jam(id)

    def jam_manager(self, current_time):
        jam_management_id = self.jam_management.keys()
        for i in self.tyre_management:
            if self.tyre_management[i]['is jam detected']:
                if (i not in jam_management_id):
                    self.jam_management[i] = {}
                    self.jam_management[i]['time when jam detected'] = current_time
                    self.jam_management[i]['is jam confirmed'] = False
        # if any jam is persisted more than 1 minute, then confirm the jam and incremented the jam count
        for i in self.jam_management:
            if int(current_time - self.jam_management[i]['time when jam detected']) > int(self.jam_confirm_time):
                print("Tyre Jam detected id", i)
                if (not self.jam_management[i]['is jam confirmed']):
                    self.jam_confirmed_count += 1
                    print("jam count when increasing:", self.jam_confirmed_count)
                self.jam_management[i]['is jam confirmed'] = True
        if self.jam_confirmed_count >= self.jam_confirmed_limit:
            print("Jam count when signal:", self.jam_confirmed_count)
            print("Signal from:", self.cam_name)
            return True
        return False

    def id_manager(self, current_time):
        # for removing the false detected id and unused id
        # get the the currently stored id's
        # current_frame_ids is the ids detected in the current frame or iteration
        # if any stored id is not present in the current frame id, then insert the id in the id management with time
        if self.frame_number % (int(self.fps) * self.id_check_time) == 0:
            currently_stored_ids = list(self.tyre_management.keys())
            self.current_frame_ids = [str(i) for i in self.current_frame_ids]
            for i in currently_stored_ids:
                if i not in self.current_frame_ids:
                    self.tyre_management[i]['is id present in the current frame'] = False
                    self.id_management[i] = {}
                    self.id_management[i]['time when id disappeared'] = current_time
                    print(i, "from id manager", dir)
                    self.delete_jam(i)
                else:
                    if not self.tyre_management[i]['is id present in the current frame']:
                        self.tyre_management[i]['is id present in the current frame'] = True
                        self.delete_id(i)
        self.id_manager_deletion(current_time)

    def id_manager_deletion(self, current_time):
        # if id is not present for more than 1 min, remove the id  from the id and tyre management
        id_to_be_removed = []
        for i in self.id_management:
            if current_time - self.id_management[i]['time when id disappeared'] > self.id_confirm_time:
                id_to_be_removed.append(i)
        for i in id_to_be_removed:
            print(i, "from id manager deletion of tyres", dir)
            self.delete_tyre(i)

    def detectBack(self, frame):
        results = self.model.track(frame, persist=True)
        # for pos in self.tracking_lineBack:
        #     cv2.line(frame, (0, pos), (frame.shape[1], pos), (0, 255, 0), 2)
        current_time = time.time()
        self.frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        for result in results:
            if result.boxes.id == None:
                return frame
            self.current_frame_ids = result.boxes.id.tolist()
            for box in result.boxes:
                box_id = str(box.id.tolist()[0])
                box_coords = box.xyxy.tolist()
                center_x = int((box_coords[0][0] + box_coords[0][2]) / 2)
                center_y = int((box_coords[0][1] + box_coords[0][3]) / 2)
                # cv2.putText(frame, box_id, (center_x, center_y),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                              (int(box_coords[0][2]), int(box_coords[0][3])), (0, 255, 0), 1)
                # if box_id is already detected and present in the tyre managemet
                if box_id in self.tyre_management:
                    # if box has crossed the last tracking line, then del the id
                    if box_coords[0][1] < self.tracking_lineBack[-1]:
                        self.delete_tyre(box_id)
                        continue
                    # if box has crossed the upcoming tracking line, then change the next line to be crossed and the time
                    if self.tyre_management[box_id]['next line to cross'] > box_coords[0][3]:
                        idx = self.tracking_lineBack.index(self.tyre_management[box_id]['next line to cross'])
                        self.tyre_management[box_id]['next line to cross'] = self.tracking_lineBack[idx + 1]
                        self.tyre_management[box_id]['time when the tyre cross the line'] = current_time
                        if self.tyre_management[box_id]['is jam detected']:
                            self.tyre_management[box_id]['is jam detected'] = False
                            self.delete_jam(box_id)
                    else:
                        if current_time - self.tyre_management[box_id][
                            'time when the tyre cross the line'] > self.jam_check_time:
                            if not self.tyre_management[box_id]['is jam detected']:
                                self.tyre_management[box_id]['is jam detected'] = True
                            if box_id in self.jam_management and self.jam_management[box_id]['is jam confirmed']:
                                cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                                              (int(box_coords[0][2]), int(box_coords[0][3])), (0, 0, 255), 3)
                else:
                    for pos in self.tracking_lineBack:
                        if box_coords[0][3] > pos:
                            self.tyre_management[box_id] = {}
                            self.tyre_management[box_id]['next line to cross'] = pos
                            self.tyre_management[box_id]['time when the tyre cross the line'] = current_time
                            self.tyre_management[box_id]['is jam detected'] = False
                            self.tyre_management[box_id]['is id present in the current frame'] = True
                            break
            # fake detection also comes under the jam , if it comes to id, then jam should delete
            # backup the data if any error occured and initialize
            if self.jam_manager(current_time):
                plc_trigger(True, self.cam_name, self.jam_confirmed_count, "")
                print()
            self.id_manager(current_time)
        return frame

    def detectFront(self, frame):
        results = self.model.track(frame, persist=True)

        # for pos in self.tracking_lineFront:
        #     cv2.line(frame, (0, pos), (frame.shape[1], pos), (0, 255, 0), 2)
        # ...
        current_time = time.time()

        self.frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        for result in results:
            if result.boxes.id == None:
                return frame
            self.current_frame_ids = result.boxes.id.tolist()
            for box in result.boxes:
                box_id = str(box.id.tolist()[0])
                box_coords = box.xyxy.tolist()
                cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                              (int(box_coords[0][2]), int(box_coords[0][3])), (0, 255, 0), 1)
                # if box_id is already detected and present in the tyre managemet
                if box_id in self.tyre_management:
                    # if box has crossed the last tracking line, then del the id
                    if box_coords[0][1] > self.tracking_lineFront[-1]:
                        self.delete_tyre(box_id)
                        continue
                    # if box has crossed the upcoming tracking line, then change the next line to be crossed and the time
                    if self.tyre_management[box_id]['next line to cross'] < box_coords[0][1]:
                        idx = self.tracking_lineFront.index(self.tyre_management[box_id]['next line to cross'])
                        self.tyre_management[box_id]['next line to cross'] = self.tracking_lineFront[idx + 1]
                        self.tyre_management[box_id]['time when the tyre cross the line'] = current_time
                        if self.tyre_management[box_id]['is jam detected']:
                            self.tyre_management[box_id]['is jam detected'] = False
                            self.delete_jam(box_id)
                    else:
                        if current_time - self.tyre_management[box_id][
                            'time when the tyre cross the line'] > self.jam_check_time:
                            if not self.tyre_management[box_id]['is jam detected']:
                                self.tyre_management[box_id]['is jam detected'] = True
                            if box_id in self.jam_management and self.jam_management[box_id]['is jam confirmed']:
                                cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                                              (int(box_coords[0][2]), int(box_coords[0][3])), (0, 0, 255), 3)
                else:
                    for pos in self.tracking_lineFront:
                        if box_coords[0][1] < pos:
                            self.tyre_management[box_id] = {}
                            self.tyre_management[box_id]['next line to cross'] = pos
                            self.tyre_management[box_id]['time when the tyre cross the line'] = current_time
                            self.tyre_management[box_id]['is jam detected'] = False
                            self.tyre_management[box_id]['is id present in the current frame'] = True
                            break
            # fake detection also comes under the jam , if it comes to id, then jam should delete
            # backup the data if any error occured and initialize
            if self.jam_manager(current_time):
                plc_trigger(True, self.cam_name, self.jam_confirmed_count, "")
                print()
            # else:
            #     plc_trigger(False)
            self.id_manager(current_time)
        return frame


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Apollo Tyres")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Calculate the frame size based on screen resolution
        frame_width = int(screen_width)  # 80% of screen width
        frame_height = int(screen_height)  # 80% of screen height
        print(frame_height)
        print(frame_width)
        # Calculate the x and y coordinates to center the window
        x_coordinate = (screen_width - frame_width) // 2
        y_coordinate = (screen_height - frame_height) // 2
        # Set the geometry of the main window and align it to the center
        self.geometry(f"{frame_width}x{frame_height}+{x_coordinate}+{y_coordinate}")
        self.frames = {}
        self.login_frame = LoginPage(self)
        self.ip_address_frame = IPAddressPage(self)
        self.welcome_frame = WelcomePage(self)
        # self.records_frame = RecordsPage(self)
        self.show_frame("login")

    def show_frame(self, frame_name):
        if frame_name == "login":
            self.login_frame.pack(fill='both', expand=True)
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack_forget()
        elif frame_name == "ip_address":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack(fill='both', expand=True)
            self.welcome_frame.pack_forget()

        elif frame_name == "welcome":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack(fill='both', expand=True)
            self.welcome_frame.show_menu()
            self.welcome_frame.start_camera_feeds()

        # elif frame_name == "records":
        #     self.login_frame.pack_forget()
        #     self.ip_address_frame.pack_forget()
        #     self.welcome_frame.pack_forget()
        #     self.records_frame.pack(fill='both', expand=True)


class LoginPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        height = self.winfo_screenheight()
        const1 = int(height / 33.23)  # 26
        const2 = int(height / 8.64)  # 100
        const3 = int(height / 43.2)  # 20
        const4 = int(height / 54)  # 16
        const5 = int(height / 21.6)  # 40

        # print(const1,const2,const3,const4,const5)

        label = ttk.Label(self, text="Login Page", font=('Times New Roman', const1))  # Increased font size
        label.pack(pady=(const2, const3))  # Increased top padding

        username_label = ttk.Label(self, text="Username:", font=('Times New Roman', const4))  # Increased font size
        username_label.pack()
        self.username_entry = ttk.Entry(self, font=('Times New Roman', const4))  # Increased font size
        self.username_entry.pack()

        password_label = ttk.Label(self, text="Password:", font=('Times New Roman', const4))  # Increased font size
        password_label.pack()
        self.password_entry = ttk.Entry(self, show="*", font=('Times New Roman', const4))  # Increased font size
        self.password_entry.pack()

        self.login_button = ttk.Button(self, text="Login", command=self.handle_login, style='Login.TButton', width=14, )
        self.login_button.pack(pady=(const3, const5))
        button_font = ("Arial", const4)
        style = ttk.Style()
        style.configure('Login.TButton', font=button_font)

    def handle_login(self):
        # Your login logic goes here
        # For now, I'm just simulating successful login
        # Set to True if login successful, else set to False
        username = self.username_entry.get()  # Retrieve username
        password = self.password_entry.get()  # Retrieve password
        print("Username:", username)
        print("Password:", password)
        login_status = login_post(username, password)
        # username and password stored in database
        if login_status:
            messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
            current_uuid = get_system_id()
            print(current_uuid)
            val = check_uuid_and_initial_state(current_uuid, username)
            if val == "Load":
                self.master.show_frame("ip_address")
            elif val == "Live":
                self.master.show_frame("welcome")
            else:
                print("Problem in database or getting ip ")

        else:
            print("invalid username and password")
            messagebox.showerror("Login Failed", "Invalid username or password.")


class IPAddressPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.count = 0  # Initialize count attribute
        self.list = [0, 0, 0, 0]
        self.list_plc = []
        height = self.winfo_screenheight()
        const1 = int(height / 72)  # 12
        const3 = int(height / 43.2)  # 20
        const2 = int(height / 57.6)  # 15
        const4 = int(height / 54)  # 16

        label = ttk.Label(self, text="IP Address", font=('Helvetica', 20))  # Increased font size
        label.pack(pady=(100, 20))

        ip_frame = ttk.Frame(self)
        ip_frame.pack(pady=10)

        ip_labels = ["IP Address 1:", "IP Address 2:", "IP Address 3:", "IP Address 4:"]
        self.ip_entries = []
        self.success_labels = []  # Store success labels

        for i in range(4):
            ip_label = ttk.Label(ip_frame, text=ip_labels[i], font=("Times New Roman", const1))
            ip_label.grid(row=i, column=0, padx=const2, pady=const2)

            ip_entry = ttk.Entry(ip_frame, font=('Helvetica', const4), width=const3)
            ip_entry.grid(row=i, column=1, padx=const2, pady=const2)
            self.ip_entries.append(ip_entry)

            test_button = ttk.Button(ip_frame, text="Test", width=const2, style="test.TButton",
                                     command=lambda i=i: self.handle_test(i))
            test_button.grid(row=i, column=2, padx=const2, pady=const2)
            button_font = ("Times New Roman", const1)
            style = ttk.Style()
            style.configure('test.TButton', font=button_font)
            # Create and pack success labels initially empty
            success_label = ttk.Label(ip_frame, text="", font=const1)
            success_label.grid(row=i, column=3, padx=const2, pady=const2)
            self.success_labels.append(success_label)

        # Display success message
        self.proceed_button = ttk.Button(self, text="Proceed", style="proceed.TButton", width=const3,
                                         command=self.handle_proceed)
        self.proceed_button.pack(pady=const2)
        button_font = ("Times New Roman", const2)
        style = ttk.Style()
        style.configure('proceed.TButton', font=button_font)

    def handle_proceed(self):
        # Your proceed logic goes here
        # For now, I'm just simulating successful proceed
        # Set to True if proceed successful, else set to False
        if self.count >= 4:
            if len(self.list) == 4:
                ip1 = str(self.list[0])
                ip2 = str(self.list[1])
                ip3 = str(self.list[2])
                ip4 = str(self.list[3])
                plcip = "172.16.200"
                plcport = 5000
                store_camera_ips(ip1, ip2, ip3, ip4, plcip, plcport)
                sys_uuid = get_system_id()
                update_initial_state(sys_uuid, 1)

                self.master.show_frame("welcome")
        else:
            messagebox.showerror("IP Failed", "Check the ip address")

    def handle_plc(self, index):
        plc = self.ip_entries[index].get()
        self.list_plc.append(plc)
        print(self.list)
        print(plc)
        self.success_labels[index].config(text="Success", foreground="green")

    def handle_test(self, index):
        ip_address = self.ip_entries[index].get()  # Get the IP address from the entry
        print("Testing IP:", ip_address)

        # Initialize the list with empty strings if it hasn't been initialized yet
        if not self.list:
            self.list = [""] * 4

        camera_url = ip_address
        cap = cv2.VideoCapture(camera_url)
        print(self.count)

        while True:
            ret, frame = cap.read()

            if ret:
                with open("db.txt", 'w') as file:
                    file.write('1\n')
                    break
            else:
                with open("db.txt", 'w') as file:
                    file.write('0\n')
                    break

        with open("db.txt", 'r') as file:
            content = file.read().strip()

        if content == "1":
            self.list[index] = ip_address
            print(self.list)
            self.count += 1  # Increment count
            self.success_labels[index].config(text="Success", foreground="green")
        elif content == "0":
            self.success_labels[index].config(text="Failed", foreground="red")
        else:
            print("Database couldn't be read")


class WelcomePage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ht = self.winfo_screenheight()
        const2 = int(ht / 86.4)
        const3 = int(ht / 172.8)
        self.const4 = int(ht / 21.6)
        self.playing = True

        self.frame = tk.Frame(self)
        self.frame.grid(row=1, column=0, columnspan=2, padx=const2, pady=const2)

        self.labels = []  # Clear the labels list

        # Get list of video files
        # ip1 = retrieve_ip(0)
        # ip2 = retrieve_ip(1)
        # ip3 = retrieve_ip(2)
        # ip4 = retrieve_ip(3)
        ip1 = "C:/Users/SIVA/Downloads/WhatsApp Image 2024-05-06 at 10.09.38 AM.jpeg"
        ip2 = "C:/Users/SIVA/Downloads/WhatsApp Image 2024-05-06 at 10.09.38 AM (1).jpeg"
        ip3 = "C:/Users/SIVA/Downloads/WhatsApp Image 2024-05-06 at 10.09.39 AM.jpeg"
        ip4 =  "C:/Users/SIVA/Downloads/WhatsApp Image 2024-05-06 at 10.09.38 AM (2).jpeg"
        self.video_files = [ip1, ip2, ip3, ip4]

        # Create labels for each camera feed and add them to the list
        for i, cap in enumerate(self.video_files):
            label = tk.Label(self.frame)
            label.grid(row=i // 2, column=i % 2, padx=const3, pady=const3)
            self.labels.append(label)

        # Start threads to update each camera feed
        # self.start_camera_feeds(capture_objects)

    def stop_camera_feeds(self):
        if self.playing:
            self.playing = False

    def start_camera_feeds_button(self):
        if not self.playing:
            self.playing = True
            self.start_camera_feeds()

    def restart_camera_feeds(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def heartbeat(self):
        target_ip = '172.22.17.10'
        custom_port = 2222
        data_path_1 = 'AI_PC_HEART_BEAT_PULSE_1'
        data_path_2 = 'AI_PC_HEART_BEAT_PULSE_2'

        try:
            with LogixDriver(target_ip, port=custom_port) as plc:
                while (self.playing):
                    data_to_send_1 = True
                    data_to_send_2 = False
                    plc.write(data_path_1, data_to_send_1)
                    plc.write(data_path_2, data_to_send_2)
                    time.sleep(1)
                    data_to_send_1 = False
                    data_to_send_2 = True
                    plc.write(data_path_1, data_to_send_1)
                    plc.write(data_path_2, data_to_send_2)
                    time.sleep(1)
        except Exception as e:
            txt = open("log.txt", 'a')
            txt.write(f'line 831 pulse error {e} \n')
            txt.close()
        txt = open("log.txt", 'a')
        txt.write(f'Heart Pulse Stopped \n')
        txt.close()
        plc_trigger_override(False)
        self.start_camera_feeds_button()

    def start_camera_feeds(self):
        global confirmation_of_no_tyres_jam
        confirmation_of_no_tyres_jam = 0
        self.capture_objects = [Detection(file) for file in self.video_files]
        for label, cap, model in zip(self.labels, self.capture_objects, [1, 2, 3, 4]):
            t = threading.Thread(target=self.update_image, args=(label, cap, model))
            t.daemon = True
            t.start()
        heart = threading.Thread(target=self.heartbeat)
        heart.start()

    def update_image(self, label, cap: Detection, model):
        global conveyor_status
        global confirmation_of_no_tyres_jam
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        width = int(width // 2.11)
        height = int(height // 2.46)
        # cap.set_model(f"{model}.pt")
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM model WHERE rowid=1''')
        row = c.fetchone()
        model_1 = row[0]
        model_2 = row[1]
        model_3 = row[2]
        model_4 = row[3]
        conn.close()
        if model == 1:
            cap.set_model(model_1)
        elif model == 2:
            cap.set_model(model_2)
        elif model == 3:
            cap.set_model(model_3)
        elif model == 4:
            cap.set_model(model_4)
        else:
            print("no model found!")
        while self.playing:
            try:
                ret, frame = cap.cap.read()
                if conveyor_status:
                    if ret:
                        # Resize the frame to fit the label
                        if (model == 1 or model == 2):
                            frame = cap.detectBack(frame)
                        elif (model == 3 or model == 4):
                            frame = cap.detectFront(frame)
                        if (cap.jam_confirmed_count < cap.jam_confirmed_limit and cap.cam_name in detected_feed):
                            plc_trigger(False)
                            idx = detected_feed.index(cap.cam_name)
                            del detected_feed[idx]
                        frame = cv2.resize(frame, (width, height))  # Adjust dimensions as needed
                        # Convert frame to RGB format
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Convert frame to ImageTk format
                        img = Image.fromarray(frame)
                        img_tk = ImageTk.PhotoImage(image=img)
                        # Update the label with the new frame
                        label.config(image=img_tk)
                        label.image = img_tk
                    else:
                        txt = open("log.txt", 'a')
                        txt.write(f"Frame missed : \n")
                        txt.close()
                        self.playing = False
                        break
                else:
                    if ret:
                        txt = open("log.txt", 'a')
                        txt.write(f"Conveyor Stopped so no detection taking place : \n")
                        txt.close()
                        plc_trigger(False)
                        cap.jam_management.clear()
                        cap.id_management.clear()
                        cap.tyre_management.clear()
                        cap.jam_confirmed_count = 0
                        frame = cv2.resize(frame, (width, height))  # Adjust dimensions as needed
                        # Convert frame to RGB format
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Convert frame to ImageTk format
                        img = Image.fromarray(frame)
                        img_tk = ImageTk.PhotoImage(image=img)
                        # Update the label with the new frame
                        label.config(image=img_tk)
                        label.image = img_tk
                    else:
                        txt = open("log.txt", 'a')
                        txt.write(f"Frame missed in without detection: \n")
                        txt.close()
                        self.playing = False
                        break
            except Exception as e:
                print("Error:", e)
                txt = open("log.txt", 'a')
                txt.write(f"Exception while reading frame : {e}\n")
                txt.close()
                self.playing = False
                break
        cap.cap.release()

    def show_menu(self, show=True):
        if show:
            self.menubar = tk.Menu(self.master)
            self.master.config(menu=self.menubar)
            # Create File menu
            self.file_menu = tk.Menu(self.menubar, tearoff=0)
            self.file_menu.add_command(label="Start", command=self.start_camera_feeds_button)
            self.file_menu.add_command(label="Stop", command=self.stop_camera_feeds)
            self.file_menu.add_command(label="Restart", command=self.restart_camera_feeds)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Show Records", command=self.show_records)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Download Report", command=self.download_records_to_excel)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Configuration", command=self.configuration)
            self.menubar.add_cascade(label="Tools", menu=self.file_menu)
        else:
            self.master.config(menu=None)
        # Add File menu to the menubar

    def configuration(self):
        subprocess.Popen(['python', 'configuration.py'])

    def show_records(self):
        records_page = self.create_records_page(self.master)
        records_page.grid(row=1, column=0, columnspan=2, padx=self.const4, pady=self.const4)

    def download_records_to_excel(self):
        directory_path = "Records"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        conn = sqlite3.connect('config.db')
        query = "SELECT * FROM records"
        df = pd.read_sql_query(query, conn)
        conn.close()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        excel_path = os.path.join(directory_path, f"records_{timestamp}.xlsx")
        df.to_excel(excel_path, index=False)
        print("Record downloaded successfully")
        messagebox.showinfo("Download Successful", "Report downloaded Successfully")
        try:
            os.system(f'explorer {os.path.abspath(directory_path)}')  # for Windows
        except Exception as e:
            print("An error occurred:", e)
        
    def create_records_page(self, master):
        self.master.withdraw()
        self.newwindow = tk.Toplevel(master)

        ht1 = self.winfo_screenheight()
        const1 = int(ht1 / 54)  # 16
        const2 = int(ht1 / 43.2)  # 20
        const3 = int(ht1 / 86.4)  # 10
        const4 = int(ht1 / 72)  # 12
        const5 = int(ht1 / 432)  # 2
        const6 = int(ht1 / 172.8)  # 5

        # Hide the close and minimize buttons
        self.newwindow.overrideredirect(True)

        # Get the screen width and height
        screen_width = self.newwindow.winfo_screenwidth()
        screen_height = self.newwindow.winfo_screenheight()

        # Set the size of the window to fullscreen
        self.newwindow.geometry(f"{screen_width}x{screen_height}")

        records_frame = ttk.Frame(self.newwindow)
        records_frame.pack(expand=True, fill='both')
        self.filter_records
        label = ttk.Label(records_frame, text="Records", font=('Helvetica', const1))
        label.grid(row=0, column=0, pady=const2, columnspan=3)

        # Create a Combobox for selecting filter criteria
        filter_criteria = ttk.Combobox(records_frame, values=["Date", "Month", "Camera"])
        filter_criteria.grid(row=1, column=2, pady=const3, padx=const3)
        filter_criteria.set("Date")  # Set default value

        # Create a DateEntry widget for selecting date
        date_entry = DateEntry(records_frame, width=const4, background='blue', foreground='white', borderwidth=const5)
        date_entry.grid(row=2, column=2, pady=const3, padx=const3)
        date_entry.grid_remove()  # Hide initially

        # Create a Combobox for selecting camera
        camera_combobox = ttk.Combobox(records_frame, values=["Camera 1", "Camera 2", "Camera 3", "Camera 4"])
        camera_combobox.grid(row=2, column=2, pady=const3, padx=const3)
        camera_combobox.grid_remove()  # Hide initially

        # Toggle visibility of DateEntry or Combobox based on selected filter criteria
        filter_criteria.bind("<<ComboboxSelected>>",
                             lambda event: self.toggle_filter_options(filter_criteria, date_entry, camera_combobox))

        # Add filter button
        filter_button = ttk.Button(records_frame, text="Filter", style="filter.TButton",
                                   command=lambda: self.filter_records(tree, filter_criteria, camera_combobox,
                                                                       date_entry))
        filter_button.grid(row=1, column=1, pady=const3)
        button_font = ("Arial", const3)
        style = ttk.Style()
        style.configure('filter.TButton', font=button_font)

        back_button = ttk.Button(records_frame, text="Back", style="back.TButton", command=self.back)
        back_button.grid(row=1, column=0, pady=const5)
        button_font = ("Arial", const3)
        style = ttk.Style()
        style.configure('back.TButton', font=button_font)

        # Create a treeview widget to display records
        tree = ttk.Treeview(records_frame,
                            columns=("Camera", "Screenshot Location", "Timestamp", "No. of Tyres Jammed"))
        tree.grid(row=4, column=0, columnspan=3, sticky="nsew")
        records_frame.grid_rowconfigure(4, weight=1)  # Allow the row to expand vertically
        records_frame.grid_columnconfigure((0, 1, 2), weight=1)  # Allow the columns to expand horizontally

        for col in ("Camera", "Screenshot Location", "Timestamp", "No. of Tyres Jammed"):
            tree.heading(col, anchor="center")
            tree.column(col, anchor="center")
        # Add column headings
        tree.heading("#0", text="ID")
        tree.heading("Camera", text="Camera")
        tree.heading("Screenshot Location", text="Screenshot Location")
        tree.heading("Timestamp", text="Timestamp")
        tree.heading("No. of Tyres Jammed", text="No. of Tyres Jammed")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(records_frame, orient="vertical", command=tree.yview)
        vsb.grid(row=4, column=3, sticky="ns")
        tree.configure(yscrollcommand=vsb.set)

        tree.bind("<ButtonRelease-1>", lambda event: self.open_link(event, tree))
        self.filter_records(tree, filter_criteria, camera_combobox, date_entry)

    def open_link(self, event, tree):
        # Get the item that was clicked
        item = tree.selection()[0]
        # Get the value of the "Screenshot Location" column for the clicked item
        screenshot_location = tree.item(item, "values")[1]
        # Open the link in the default web browser
        webbrowser.open_new_tab(screenshot_location)

    def toggle_filter_options(self, filter_criteria, date_entry, camera_combobox):
        # Get the selected filter criteria
        criteria = filter_criteria.get()

        # Toggle visibility of DateEntry or Combobox based on selected filter criteria
        if criteria == "Date" or criteria == "Month":
            # date_entry.grid()
            date_entry.grid()
            camera_combobox.grid_remove()
        elif criteria == "Camera":
            camera_combobox.grid()
            date_entry.grid_remove()

    def filter_records(self, tree, filter_criteria, camera_combobox, date_entry):
        # Get the selected filter criteria
        criteria = filter_criteria.get()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve records from the database based on the selected filter criteria
        if criteria == "Date":
            selected_date = date_entry.get_date().strftime("%Y-%m-%d")
            cursor.execute("SELECT * FROM records WHERE DATE(timestamp) = ?", (selected_date,))
        elif criteria == "Month":
            selected_month = date_entry.get_date().strftime("%Y-%m")
            cursor.execute("SELECT * FROM records WHERE strftime('%Y-%m', timestamp) = ?", (selected_month,))
        elif criteria == "Camera":
            selected_camera = int(camera_combobox.get().split()[1])
            cursor.execute("SELECT * FROM records WHERE camera = ?", (f"Camera {selected_camera}",))

        records = cursor.fetchall()

        # Clear existing items in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # Insert filtered records into the treeview
        for record in records:
            cam = "none"
            if "c1" in record[1]:
                cam = "Camera 1"
            elif "c2" in record[1]:
                cam = "Camera 2"
            elif "c3" in record[1]:
                cam = "Camera 3"
            elif "c4" in record[1]:
                cam = "Camera 4"
            else:
                print("error: The camera path is not a rtsp link")
            tree.insert("", "end", text=record[0], values=(cam, record[2], record[3], record[4]))

        conn.close()

    def back(self):
        self.newwindow.destroy()
        self.master.deiconify()


if __name__ == "__main__":
    app = Application()
    app.mainloop()