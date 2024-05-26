import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import cv2
import subprocess
import requests
import os
import threading
from datetime import datetime
from tkinter import ttk, messagebox
import sqlite3
import cv2
import ctypes
import sys
import subprocess

class LoginPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Configuration")
        self.username = "config"  # Hardcoded username
        self.password = "c0nf1g"  # Hardcoded password

        self.create_widgets()

    def create_widgets(self):
        height = self.winfo_screenheight()
        const1 = int(height / 33.23)  # 26
        const2 = int(height / 8.64)  # 100
        const3 = int(height / 43.2)  # 20
        const4 = int(height / 54)  # 16
        const5 = int(height / 21.6)  # 40

        # print(const1,const2,const3,const4,const5)

        label = ttk.Label(self, text="Login to Configure", font=('Times New Roman', const1))  # Increased font size
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
        username = self.username_entry.get()
        password = self.password_entry.get()

        print("Entered Username:", username)
        print("Entered Password:", password)

        if username == self.username and password == self.password:
            print("Login successful")
            self.destroy()  # Hide the login page
            ip_address_page = IPAddressPage(self.master)
            ip_address_page.pack(fill='both', expand=True)
        else:
            print("Login failed")
            messagebox.showerror("Login Failed", "Invalid username or password.")


class IPAddressPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.count = 0  # Initialize count attribute
        self.list = []
        self.list_plc = []
        self.ip_status = [0, 0, 0, 0]
        height = self.winfo_screenheight()
        const1 = int(height / 72)  # 12
        const3 = int(height / 43.2)  # 20
        const2 = int(height / 57.6)  # 15
        const4 = int(height / 54)

        label = ttk.Label(self, text="Configuration", font=('Helvetica', const3))  # Increased font size
        label.pack(pady=10)

        ip_frame = ttk.Frame(self)
        ip_frame.pack(pady=10)

        ip_labels = ["IP Address 1:", "MODEL_IP1", "IP Address 2:", "MODEL_IP2", "IP Address 3:", "MODEL_IP3",
                     "IP Address 4:", "MODEL_IP4", "PLC_IP:", "Jam_Check_Time: "]
        self.ip_entries = []
        self.success_labels = []  # Store success labels

        for i in range(len(ip_labels)):
            ip_label = ttk.Label(ip_frame, text=ip_labels[i], font=("Times New Roman", const1))
            ip_label.grid(row=i, column=0, padx=const1, pady=const1)

            ip_entry = ttk.Entry(ip_frame, font=('Helvetica', const4), width=const3)
            ip_entry.grid(row=i, column=1, padx=const1, pady=const1)
            self.ip_entries.append(ip_entry)

            if i == 0 or i == 2 or i == 4 or i == 6:
                test_button = ttk.Button(ip_frame, text="Test", width=const2, style="test.TButton",
                                         command=lambda i=i: self.handle_test(i))
                test_button.grid(row=i, column=2, padx=const1, pady=const1)
                button_font = ("Times New Roman", const1)
                style = ttk.Style()
                style.configure('test.TButton', font=button_font)

                update_button = ttk.Button(ip_frame, text="UPDATE", width=const2, style="update.TButton",
                                           command=lambda i=i: self.update_ips(i))
                update_button.grid(row=i, column=4, padx=const1, pady=const1)
                button_font = ("Times New Roman", const1)
                style = ttk.Style()
                style.configure('update.TButton', font=button_font)
            elif i == 1 or i == 3 or i == 5 or i == 7:
                update_button = ttk.Button(ip_frame, text="UPDATE", width=const2, style="update2.TButton",
                                           command=lambda i=i: self.update_model(i))
                update_button.grid(row=i, column=4, padx=const1, pady=const1)
                button_font = ("Times New Roman", const1)
                style = ttk.Style()
                style.configure('update2.TButton', font=button_font)
            elif i == 8:
                test_button = ttk.Button(ip_frame, text="Test", width=const2, style="test.TButton",
                                         command=lambda i=i: self.handle_plc(i))
                test_button.grid(row=i, column=2, padx=const1, pady=const1)
                button_font = ("Times New Roman", const1)
                style = ttk.Style()
                style.configure('test.TButton', font=button_font)

                update_button = ttk.Button(ip_frame, text="UPDATE", width=const2, style="update.TButton",
                                           command=lambda i=i: self.update_ips(i))
                update_button.grid(row=i, column=4, padx=const1, pady=const1)
                button_font = ("Times New Roman", const1)
                style = ttk.Style()
                style.configure('update.TButton', font=button_font)
            elif i == 9:
                update_button = ttk.Button(ip_frame, text="UPDATE", width=const2, style="update.TButton",
                                           command=lambda i=i: self.update_ips(i))
                update_button.grid(row=i, column=4, padx=const1, pady=const1)
                button_font = ("Times New Roman", const1)
                style = ttk.Style()
                style.configure('update.TButton', font=button_font)
            else:
                update_button = ttk.Button(ip_frame, text="UPDATE", width=const2, style="update.TButton",
                                           command=lambda i=i: self.update_demo(i))
                update_button.grid(row=i, column=4, padx=const1, pady=const1)
                button_font = ("Times New Roman", const1)
                style = ttk.Style()
                style.configure('update.TButton', font=button_font)

                success_label = ttk.Label(ip_frame, text="", font=const1)
                success_label.grid(row=i, column=2, padx=const2, pady=const2)
                self.success_labels.append(success_label)

            # Create and pack success labels initially empty
            success_label = ttk.Label(ip_frame, text="", font=const1)
            success_label.grid(row=i, column=3, padx=const2, pady=const2)
            self.success_labels.append(success_label)

            new_button = ttk.Button(ip_frame, text="SAVE CHANGES", width=const2, style="update5.TButton",
                                       command=lambda i=i: self.restart())
            new_button.grid(row=10, column=1, padx=const1, pady=const1)
            button_font = ("Times New Roman", const1)
            style = ttk.Style()
            style.configure('update5.TButton', font=button_font)

            new_button2 = ttk.Button(ip_frame, text="Configure IP ", width=const2, style="update6.TButton",
                                    command=lambda i=i: self.configure_ip())
            new_button2.grid(row=10, column=2, padx=const1, pady=const1)
            button_font = ("Times New Roman", const1)
            style = ttk.Style()
            style.configure('update6.TButton', font=button_font)

            new_button3 = ttk.Button(ip_frame, text="Patches", width=const2, style="update7.TButton",
                                    command=lambda i=i: self.update_demo())
            new_button3.grid(row=10, column=3, padx=const1, pady=const1)
            button_font = ("Times New Roman", const1)
            style = ttk.Style()
            style.configure('update7.TButton', font=button_font)


        # Set the size of the frame to occupy the center of the screen
        self.grid(row=0, column=0, sticky="nsew", padx=200, pady=100)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def configure_ip(self):
        subprocess.Popen('control.exe /name Microsoft.NetworkAndSharingCenter', shell=True)

    def close_window(self):
        root.destroy()

    def restart(self):
        messagebox.showinfo("Alert!", "Manually restart the application")
        self.close_window()

    def update_demo(self,index):
        print("Button clicked")
    def download_threaded(self, url, ind):
        try:
            self.success_labels[ind].config(text="Inprogress...", foreground="blue")
            # Make a GET request to the URL to download the file
            DOWNLOAD_PATH = "D:\My Workspace\Projects\Flask - Framework\GUI_interface\models"
            response = requests.get(url)

            # Generate filename with current time
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = current_time + ".pt"
            print(requests.get(url).status_code)
            if requests.get(url).status_code == 200:
                # Write the content to the file
                with open(os.path.join(DOWNLOAD_PATH, filename), 'wb') as file:
                    file.write(response.content)
                    store_path = f"models\{filename}"
                    print(store_path)
                    conn = sqlite3.connect('config.db')
                    c = conn.cursor()

                    if ind == 1:
                        c.execute('''UPDATE model SET model_1=? WHERE rowid=1''', (store_path,))
                    elif ind  == 3:
                        c.execute('''UPDATE model SET model_2=? WHERE rowid=1''', (store_path,))
                    elif ind == 5:
                        c.execute('''UPDATE model SET model_3=? WHERE rowid=1''', (store_path,))
                    elif ind == 7:
                        c.execute('''UPDATE model SET model_4=? WHERE rowid=1''', (store_path,))
                    else:
                        print("index not found")

                    conn.commit()
                    conn.close()
                print("File downloaded successfully!")
                print("Inside if",requests.get(url).status_code)
                self.success_labels[ind].config(text="Downloaded", foreground="green")
            else:
                print("failed")
                self.success_labels[ind].config(text="Failed!", foreground="red")
                
        except Exception as e:
            print("Error occurred while downloading:", e)
            self.success_labels[ind].config(text="Failed!", foreground="red")
            print("After exception",response.status_code)

    def update_model(self, index):
        model_link = self.ip_entries[index].get()
        print(model_link)
        download_thread = threading.Thread(target=self.download_threaded, args=(model_link,index))
        download_thread.start()


    def update_ips(self, index):

        ip = self.ip_entries[index].get()
        conn = sqlite3.connect("config.db")
        cursor = conn.cursor()
        if index in (0,2,4,6):
            if ip != "" and ip == self.list[index-(index//2)]:
                if self.ip_status[index - (index // 2)] == 1:
                    respective_ip = int((index - (index//2)) + 1)
                    cursor.execute("UPDATE cameras SET ip{}=? WHERE id=1".format(respective_ip),
                                   (ip,))
                    messagebox.showinfo("Updated Successful", "IP addresses updated successfully.")
                else:
                    messagebox.showerror("IP Failed", "Recheck the IP")
            else:
                messagebox.showerror("No URL Found!", "Please enter the valid tested url")
        elif index == 8:
            cursor.execute("UPDATE cameras SET plcip=? WHERE id=1",
                           (ip,))
            messagebox.showinfo("Updated Successful", "PLC addresses updated successfully.")
        elif index == 9:
            cursor.execute("UPDATE cameras SET jam_check_time=? WHERE id=1",
                           (ip,))
            messagebox.showinfo("Updated Successful", "Jam checking time updated successfully.")
        conn.commit()
        conn.close()

    def handle_update(self):
        # Connect to the database
        if self.count >= 4:
            if len(self.list) == 4:
                conn = sqlite3.connect("config.db")
                cursor = conn.cursor()
                # Get the IP addresses from the entries
                ip_addresses = [entry.get() for entry in self.ip_entries]
                plcip = self.ip_entries[-1].get()
                plcport = 5000  # Hardcoded plcport
                # Update the first row of the cameras table with the IP addresses
                cursor.execute("UPDATE cameras SET ip1=?, ip2=?, ip3=?, ip4=?, plcip=?, plcport=? WHERE id=1",
                               (*ip_addresses, plcport))

                conn.commit()
                conn.close()

                messagebox.showinfo("Update Successful", "IP addresses updated successfully.")

        else:
            messagebox.showerror("IP Failed", "Check the ip address")

    def handle_plc(self, index):
        plc = self.ip_entries[index].get()
        print(plc)
        self.success_labels[index].config(text="Pinging", foreground="green")

    def handle_test(self, index):
        print(index-(index//2))
        print(self.ip_status)
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
            self.list[index-(index//2)] = ip_address
            print(self.list)
            self.count += 1  # Increment count
            self.success_labels[index].config(text="Success", foreground="green")
            self.ip_status[index-(index//2)] = 1
        elif content == "0":
            self.success_labels[index].config(text="Failed", foreground="red")
            self.ip_status[index-(index//2)] = 0
        else:
            print("Database couldn't be read")


def get_screen_resolution():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Login System")
    width, height = get_screen_resolution()
    root.geometry(f"{width}x{height}+0+0")
    root.state('zoomed')  # Open in fullscreen mode without hiding close, minimize elements
    login_page = LoginPage(root)
    login_page.pack(fill='both', expand=True)
    root.mainloop()