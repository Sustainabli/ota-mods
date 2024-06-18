import tkinter as tk
from tkinter import messagebox
import threading
import serial


class ESP32ConfigApp:
    def __init__(self, master):
        self.master = master
        master.title("ESP32 Config")

        try:
            self.serial_port = serial.Serial('/dev/tty.usbserial-XXXX', 115200, timeout=1)  # Change to the correct port
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", str(e))
            master.destroy()
            return

        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

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

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)
        self.log_text.config(state='disabled')

    def read_serial(self):
        while True:
            if self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                self.log(line)
                self.process_serial_data(line)

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
            self.serial_port.write("CONFIG:WAITING-0\n".encode('utf-8'))
        elif data.startswith("CONFIG:WAITING-0"):
            self.prompt_fume_hood("fully close")
        elif data.startswith("CONFIG:SET-FULLY-CLOSE"):
            self.serial_port.write("CONFIG:WAITING-100\n".encode('utf-8'))
        elif data.startswith("CONFIG:WAITING-100"):
            self.prompt_fume_hood("fully open")
        elif data.startswith("CONFIG:SET-FULLY-OPEN"):
            self.serial_port.write("CONFIG:SEE-DIST\n".encode('utf-8'))
        elif data.startswith("CONFIG:ERR"):
            self.show_error(data)
        elif data.startswith("CONFIG:DIST"):
            self.log(data)
        # Handle other cases as needed

    def prompt_wifi_credentials(self):
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()

        if ssid and password:
            self.serial_port.write(f"CONFIG:SSID:{ssid}\n".encode('utf-8'))
            self.serial_port.write(f"CONFIG:PSW:{password}\n".encode('utf-8'))
        else:
            messagebox.showwarning("Input Error", "Please enter both SSID and Password")

    def use_last_config(self):
        self.serial_port.write("CONFIG:USE-LAST\n".encode('utf-8'))

    def request_color_alignment(self, color):
        self.serial_port.write("CONFIG:COLOR\n".encode('utf-8'))

    def prompt_align_sensor(self, color):
        response = messagebox.askyesno("Align Sensor",
                                       f"Align the sensor with the top of the {color} square and press Yes")
        if response:
            self.serial_port.write(f"CONFIG:ALIGNED-{color}\n".encode('utf-8'))

    def request_distance_config(self):
        self.serial_port.write("CONFIG:DIST\n".encode('utf-8'))

    def prompt_fume_hood(self, action):
        response = messagebox.askyesno("Fume Hood", f"Please {action} the fume hood and press Yes")
        if response:
            self.serial_port.write(f"CONFIG:SET-{action.replace(' ', '-')}\n".encode('utf-8'))

    def show_error(self, error_message):
        messagebox.showerror("Error", error_message)

    def submit_config(self):
        self.serial_port.write("CONFIG:WIFI\n".encode('utf-8'))
        self.ssid_label.pack_forget()
        self.ssid_entry.pack_forget()
        self.password_label.pack_forget()
        self.password_entry.pack_forget()
        self.submit_button.pack_forget()

    def start_distance_readings(self):
        self.serial_port.write("CONFIG:SEE-DIST\n".encode('utf-8'))

    def stop_distance_readings(self):
        self.serial_port.write("CONFIG:STOP-DIST\n".encode('utf-8'))

    def on_closing(self):
        if self.serial_port.is_open:
            self.serial_port.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32ConfigApp(root)
    root.mainloop()
