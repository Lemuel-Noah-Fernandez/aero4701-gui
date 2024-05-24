import json
import os
import numpy as np
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

class Gui(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_data, 0.5)

    def on_kv_post(self, base_widget):
        self.ids.plot_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def update_data(self, dt):
        data_dir = '../data'
        data_files = {
            'pose_data.json': self.ids.pose_data_layout,
            'science_data.json': self.ids.science_data_layout,
            'debris_found_data.json': None,  # For plotting
            'raw_lidar_data.json': None,  # For plotting
            'wod_data.json': None  # For plotting and displaying ID and time
        }

        lidar_data = None
        debris_data = None

        for file_name, layout in data_files.items():
            file_path = os.path.join(data_dir, file_name)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if data and isinstance(data, list):
                        if file_name == 'wod_data.json':
                            self.plot_data(data[-1])
                            self.display_wod_info(data[-1])
                        elif file_name == 'debris_found_data.json':
                            debris_data = data
                        elif file_name == 'raw_lidar_data.json':
                            lidar_data = data
                        else:
                            self.display_data(layout, data[-1], layout)  # Get the last entry
                    else:
                        if file_name != 'wod_data.json' and file_name != 'debris_found_data.json' and file_name != 'raw_lidar_data.json':
                            self.display_data(layout, None, layout)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                if file_name != 'wod_data.json' and file_name != 'debris_found_data.json' and file_name != 'raw_lidar_data.json':
                    self.display_data(layout, None, layout)
                print(f"Error reading {file_name}: {e}")

        if lidar_data and debris_data:
            self.plot_lidar_and_debris_data(lidar_data[-1], debris_data)

    def display_data(self, layout, data, title):
        layout.clear_widgets()

        if title == self.ids.pose_data_layout:
            layout.add_widget(Label(text="Pose Data", color=(0, 0, 0, 1), font_size='35sp'))
        elif title == self.ids.science_data_layout:
            layout.add_widget(Label(text="Science Data", color=(0, 0, 0, 1), font_size='35sp'))
        elif title == self.ids.misc_data_layout:
            return  # Skip for misc_data_layout

        if not data:
            layout.add_widget(Label(text="No data available", color=(0, 0, 0, 1)))
            return

        for key, value in data.items():
            layout.add_widget(Label(text=f"{key}: {value}", color=(0, 0, 0, 1)))

    def plot_data(self, data):
        if not data:
            print("No WOD data available for plotting")
            return

        datasets = data.get("datasets", [])
        if not datasets:
            print("No datasets available for plotting")
            return

        times = range(len(datasets))

        battery_voltages = [dataset["battery_voltage"] for dataset in datasets]
        battery_currents = [dataset["battery_current"] for dataset in datasets]
        bus_current_3v3 = [dataset["regulated_bus_current_3v3"] for dataset in datasets]
        bus_current_5v = [dataset["regulated_bus_current_5v"] for dataset in datasets]
        temperature_comm = [dataset["temperature_comm"] for dataset in datasets]
        temperature_eps = [dataset["temperature_eps"] for dataset in datasets]
        temperature_battery = [dataset["temperature_battery"] for dataset in datasets]

        plt.clf()  # Clear the current figure

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

        ax1.plot(times, temperature_comm, label="Comm Temperature (°C)", marker='o')
        ax1.plot(times, temperature_eps, label="EPS Temperature (°C)", marker='o')
        ax1.plot(times, temperature_battery, label="Battery Temperature (°C)", marker='o')
        ax1.set_ylabel("Temperature (°C)")
        ax1.legend()

        ax2.plot(times, battery_voltages, label="Battery Voltage (V)", marker='o')
        ax2.set_ylabel("Voltage (V)")
        ax2.legend()

        ax3.plot(times, battery_currents, label="Battery Current (A)", marker='o')
        ax3.plot(times, bus_current_3v3, label="3.3V Bus Current (A)", marker='o')
        ax3.plot(times, bus_current_5v, label="5V Bus Current (A)", marker='o')
        ax3.set_xlabel("Dataset number (0-32)")
        ax3.set_ylabel("Current (A)")
        ax3.legend()

        plt.tight_layout()

        self.ids.plot_box.clear_widgets()  # Clear previous plot
        self.ids.plot_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))  # Add new plot

    def plot_lidar_and_debris_data(self, lidar_data, debris_data):
        if not lidar_data or not debris_data:
            print("Insufficient data for plotting lidar and debris data")
            return

        # Example plotting of lidar distances
        lidar_distances = np.array(lidar_data["distances"]).reshape(8, 8)
        blob_positions = np.array([item["blob_position"] for item in debris_data])

        plt.clf()  # Clear the current figure

        plt.figure()
        plt.imshow(lidar_distances, cmap='viridis', interpolation='nearest')
        plt.colorbar(label='Value')
        plt.scatter(blob_positions[:, 1], blob_positions[:, 0], marker='x', color='r')
        plt.xlabel('Column')
        plt.ylabel('Row')
        plt.title('2D Plot of Lidar and Debris Data')

        self.ids.misc_data_layout.clear_widgets()  # Clear previous plot
        self.ids.misc_data_layout.add_widget(FigureCanvasKivyAgg(plt.gcf()))  # Add new plot

    def display_wod_info(self, data):
        self.ids.wod_info_layout.clear_widgets()

        if data is None:
            self.ids.wod_info_layout.add_widget(Label(text="No data available", color=(0, 0, 0, 1), font_size='25sp'))
            return

        satellite_id = data.get("satellite_id", "Unknown")
        time_field = data.get("time_field", "Unknown")

        datasets = data.get("datasets", [])
        satellite_mode = datasets[0].get("satellite_mode", "Unknown") if datasets else "Unknown"

        self.ids.wod_info_layout.add_widget(Label(text=f"Satellite ID: {satellite_id}", color=(0, 0, 0, 1), font_size='20sp'))
        self.ids.wod_info_layout.add_widget(Label(text=f"Time: {time_field}", color=(0, 0, 0, 1), font_size='20sp'))
        self.ids.wod_info_layout.add_widget(Label(text=f"Satellite Mode: {satellite_mode}", color=(0, 0, 0, 1), font_size='20sp'))

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Beige"
        Builder.load_file('gui.kv')
        return Gui()

if __name__ == '__main__':
    MainApp().run()
