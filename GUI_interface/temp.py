import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import requests
import os

def check_for_updates():

    url_list = ["https://model.viyugha.tech/gui", "https://model.viyugha.tech/config","https://model.viyugha.tech/db","https://model.viyugha.tech/configuration"]
    print("Entered")
    # Directory to save downloaded files
    DOWNLOAD_PATH = "D:/My Workspace/Projects/Flask - Framework/GUI_interface"

    for url in url_list:
        response = requests.get(url)
        print(response.status_code)
        try:
            if response.status_code == 200:
                # Extract filename from the URL
                filename = os.path.basename(url)
                print(filename)
                if filename == "gui":
                    filename += "1.py"
                elif filename == "configuration":
                    filename += "1.py"
                elif filename == "db":
                    filename += "1.txt"
                elif filename == "config":
                    filename += "1.db"
                # Write the content to the file
                with open(os.path.join(DOWNLOAD_PATH, filename), 'wb') as file:
                    file.write(response.content)
                print("File downloaded successfully:", filename)


        except Exception as e:
            print("Error:", e)

    root.withdraw()
    subprocess.Popen([sys.executable, "gui.py"])
    # Hide the Tkinter window and open gui.py


# Create the main Tkinter window
root = tk.Tk()
root.title("Check for Updates")

# Get screen resolution
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate padding and dialog box size
padding = min(screen_width, screen_height) // 20  # Adjust as needed
dialog_width = min(screen_width // 2, 400)  # Set maximum width
dialog_height = min(screen_height // 2, 300)  # Set maximum height

# Function to show the dialog box
def show_dialog():
    messagebox.showinfo("Update Check", "Checking for updates...")

# Create a label to display "Make your system up to date"
info_label = tk.Label(root, text="Make your system up to date")
info_label.pack(pady=10)
# Create a button to check for updates
check_button = tk.Button(root, text="Check for Updates", command=check_for_updates)
check_button.pack(side="bottom", padx=padding, pady=padding)

root.geometry(f"{dialog_width}x{dialog_height}")

root.mainloop()
