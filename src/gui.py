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
            'debris_found_data.json': None,
            'raw_lidar_data.json': None,
            'wod_data.json': None
        }

        lidar_data = {1: None, 2: None, 3: None, 4: None}
        debris_data = {1: None, 2: None, 3: None, 4: None}

        for file_name in data_files.keys():
            file_path = os.path.join(data_dir, file_name)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if data and isinstance(data, list):
                        if file_name == 'wod_data.json':
                            self.plot_data(data[-1])
                            self.display_wod_info(data[-1])
                        elif file_name == 'debris_found_data.json':
                            for item in data:
                                label = item['lidar_label']
                                debris_data[label] = item
                        elif file_name == 'raw_lidar_data.json':
                            for item in data:
                                label = item['lidar_num']
                                lidar_data[label] = item
                        else:
                            self.display_data(data_files[file_name], data[-1], data_files[file_name])
                    else:
                        if file_name not in ['wod_data.json', 'debris_found_data.json', 'raw_lidar_data.json']:
                            self.display_data(data_files[file_name], None, data_files[file_name])
            except (FileNotFoundError, json.JSONDecodeError) as e:
                if file_name not in ['wod_data.json', 'debris_found_data.json', 'raw_lidar_data.json']:
                    self.display_data(data_files[file_name], None, data_files[file_name])
                print(f"Error reading {file_name}: {e}")

        for label in [1, 2, 3, 4]:
            if lidar_data[label] and debris_data[label]:
                self.plot_lidar_and_debris_data(lidar_data[label], debris_data[label], label)

    def display_data(self, layout, data, title):
        layout.clear_widgets()

        if title == self.ids.pose_data_layout:
            layout.add_widget(Label(text="Pose Data", color=(0, 0, 0, 1), font_size='35sp'))
        elif title == self.ids.science_data_layout:
            layout.add_widget(Label(text="Science Data", color=(0, 0, 0, 1), font_size='35sp'))
        elif title == self.ids.misc_data_layout:
            return

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

    def plot_lidar_and_debris_data(self, lidar_data, debris_data, label):
        if not lidar_data or not debris_data:
            print("Insufficient data for plotting lidar and debris data")
            return

        lidar_distances = np.array(lidar_data["distances"]).reshape(8, 8)
        blob_positions = np.array([debris_data["blob_position"]])

        fig, ax = plt.subplots()
        ax.imshow(lidar_distances, cmap='viridis', interpolation='nearest')
        ax.scatter(blob_positions[:, 1], blob_positions[:, 0], marker='x', color='r')
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.set_title(f'Lidar {label}')
        fig.colorbar(ax.imshow(lidar_distances, cmap='viridis', interpolation='nearest'), label='Value')

        lidar_layout_id = f'lidar{label}'
        self.ids[lidar_layout_id].clear_widgets()  # Clear previous plot
        self.ids[lidar_layout_id].add_widget(FigureCanvasKivyAgg(fig))  # Add new plot

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
