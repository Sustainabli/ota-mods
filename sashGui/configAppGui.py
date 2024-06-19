import tkinter as tk
from tkinter import messagebox
import threading
import queue
import time


class ESP32ConfigApp:
    def __init__(self, master):
        self.master = master
        master.title("ESP32 Config")

        self.mock_data_queue = queue.Queue()
        self.mock_data_list = [
            "CONFIG:WAITING-WIFI",
            "CONFIG:SUCCESS-WIFI",
            "CONFIG:WAITING-BLACK",
            "CONFIG:GOT-BLACK",
            "CONFIG:WAITING-GREY",
            "CONFIG:GOT-GREY",
            "CONFIG:WAITING-WHITE",
            "CONFIG:GOT-WHITE",
            "CONFIG:WAITING-0",
            "CONFIG:SET-FULLY-CLOSE",
            "CONFIG:WAITING-100",
            "CONFIG:SET-FULLY-OPEN",
            "CONFIG:DIST"
        ]

        for data in self.mock_data_list:
            self.mock_data_queue.put(data)

        self.label = tk.Label(master, text="ESP32 Configuration")
        self.label.pack()

        self.log_text = tk.Text(master, state='disabled', height=15, width=50)
        self.log_text.pack()

        self.ssid_label = tk.Label(master, text="SSID")
        self.ssid_label.pack()
        self.ssid_entry = tk.Entry(master)
        self.ssid_entry.pack()

        self.password_label = tk.Label(master, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(master, show='*')
        self.password_entry.pack()

        self.use_last_button = tk.Button(master, text="Use Last Config", command=self.use_last_config)
        self.use_last_button.pack()

        self.submit_button = tk.Button(master, text="Submit", command=self.submit_config)
        self.submit_button.pack()

        self.start_distance_button = tk.Button(master, text="Start Distance Readings",
                                               command=self.start_distance_readings)
        self.start_distance_button.pack()

        self.stop_distance_button = tk.Button(master, text="Stop Distance Readings",
                                              command=self.stop_distance_readings)
        self.stop_distance_button.pack()

        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)
        self.log_text.config(state='disabled')

    def read_serial(self):
        while not self.mock_data_queue.empty():
            line = self.mock_data_queue.get()
            self.log(line)
            self.process_serial_data(line)
            time.sleep(1)  # Simulate delay

    def process_serial_data(self, data):
        if data.startswith("CONFIG:WAITING-WIFI"):
            self.prompt_wifi_credentials()
        elif data.startswith("CONFIG:SUCCESS-WIFI"):
            self.request_color_alignment("black")
        elif data.startswith("CONFIG:WAITING-BLACK"):
            self.prompt_align_sensor("black")
        elif data.startswith("CONFIG:GOT-BLACK"):
            self.request_color_alignment("grey")
        elif data.startswith("CONFIG:WAITING-GREY"):
            self.prompt_align_sensor("grey")
        elif data.startswith("CONFIG:GOT-GREY"):
            self.request_color_alignment("white")
        elif data.startswith("CONFIG:WAITING-WHITE"):
            self.prompt_align_sensor("white")
        elif data.startswith("CONFIG:GOT-WHITE"):
            self.mock_data_queue.put("CONFIG:WAITING-0")
        elif data.startswith("CONFIG:WAITING-0"):
            self.prompt_fume_hood("fully close")
        elif data.startswith("CONFIG:SET-FULLY-CLOSE"):
            self.mock_data_queue.put("CONFIG:WAITING-100")
        elif data.startswith("CONFIG:WAITING-100"):
            self.prompt_fume_hood("fully open")
        elif data.startswith("CONFIG:SET-FULLY-OPEN"):
            self.mock_data_queue.put("CONFIG:SEE-DIST")
        elif data.startswith("CONFIG:ERR"):
            self.show_error(data)
        elif data.startswith("CONFIG:DIST"):
            self.log(data)
        # Handle other cases as needed

    def prompt_wifi_credentials(self):
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()

        if ssid and password:
            self.log(f"CONFIG:SSID:{ssid}")
            self.log(f"CONFIG:PSW:{password}")
        else:
            messagebox.showwarning("Input Error", "Please enter both SSID and Password")

    def use_last_config(self):
        self.log("CONFIG:USE-LAST")

    def request_color_alignment(self, color):
        self.log(f"CONFIG:COLOR")

    def prompt_align_sensor(self, color):
        response = messagebox.askyesno("Align Sensor",
                                       f"Align the sensor with the top of the {color} square and press Yes")
        if response:
            self.log(f"CONFIG:ALIGNED-{color}")

    def request_distance_config(self):
        self.log("CONFIG:DIST")

    def prompt_fume_hood(self, action):
        response = messagebox.askyesno("Fume Hood", f"Please {action} the fume hood and press Yes")
        if response:
            self.log(f"CONFIG:SET-{action.replace(' ', '-')}")

    def show_error(self, error_message):
        messagebox.showerror("Error", error_message)

    def submit_config(self):
        self.log("CONFIG:WIFI")
        self.ssid_label.pack_forget()
        self.ssid_entry.pack_forget()
        self.password_label.pack_forget()
        self.password_entry.pack_forget()
        self.submit_button.pack_forget()

    def start_distance_readings(self):
        self.log("CONFIG:SEE-DIST")

    def stop_distance_readings(self):
        self.log("CONFIG:STOP-DIST")

    def on_closing(self):
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32ConfigApp(root)
    root.mainloop()
