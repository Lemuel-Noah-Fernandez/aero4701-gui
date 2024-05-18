import json
import os
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
        Clock.schedule_interval(self.update_data, 1)

    def on_kv_post(self, base_widget):
        self.ids.plot_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def update_data(self, dt):
        data_dir = '../data'
        data_files = {
            'pose_data.json': self.ids.pose_data_layout,
            'science_data.json': self.ids.science_data_layout,
            'misc_data.json': self.ids.misc_data_layout,
            'wod_data.json': None  # For plotting and displaying ID and time
        }

        for file_name, layout in data_files.items():
            file_path = os.path.join(data_dir, file_name)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if data and isinstance(data, list):
                        if file_name == 'wod_data.json':
                            self.plot_data(data[-1])
                            self.display_wod_info(data[-1])
                        else:
                            self.display_data(layout, data[-1], layout)  # Get the last entry
                    else:
                        if file_name != 'wod_data.json':
                            self.display_data(layout, None, layout)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                if file_name != 'wod_data.json':
                    self.display_data(layout, None, layout)
                print(f"Error reading {file_name}: {e}")

    def display_data(self, layout, data, title):
        layout.clear_widgets()

        # Title
        if title == self.ids.pose_data_layout:
            layout.add_widget(Label(text="Pose Data", color=(0, 0, 0, 1), font_size='35sp'))
        elif title == self.ids.science_data_layout:
            layout.add_widget(Label(text="Science Data", color=(0, 0, 0, 1), font_size='35sp'))
        elif title == self.ids.misc_data_layout:
            layout.add_widget(Label(text="Misc Data", color=(0, 0, 0, 1), font_size='35sp'))

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

        # Extract values
        battery_voltages = [dataset["battery_voltage"] for dataset in datasets]
        battery_currents = [dataset["battery_current"] for dataset in datasets]
        bus_current_3v3 = [dataset["regulated_bus_current_3v3"] for dataset in datasets]
        bus_current_5v = [dataset["regulated_bus_current_5v"] for dataset in datasets]
        temperature_comm = [dataset["temperature_comm"] for dataset in datasets]
        temperature_eps = [dataset["temperature_eps"] for dataset in datasets]
        temperature_battery = [dataset["temperature_battery"] for dataset in datasets]

        plt.clf()  # Clear the current figure
        plt.plot(times, battery_voltages, label="Battery Voltage (V)", marker='o')
        plt.plot(times, battery_currents, label="Battery Current (A)", marker='o')
        plt.plot(times, bus_current_3v3, label="3.3V Bus Current (A)", marker='o')
        plt.plot(times, bus_current_5v, label="5V Bus Current (A)", marker='o')
        plt.plot(times, temperature_comm, label="Comm Temperature (°C)", marker='o')
        plt.plot(times, temperature_eps, label="EPS Temperature (°C)", marker='o')
        plt.plot(times, temperature_battery, label="Battery Temperature (°C)", marker='o')

        plt.title("WOD Data Over Time")
        plt.xlabel("Dataset number (0-32)")
        plt.ylabel("Values")
        plt.legend()
        plt.tight_layout()

        self.ids.plot_box.clear_widgets()  # Clear previous plot
        self.ids.plot_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))  # Add new plot

    def display_wod_info(self, data):
        self.ids.wod_info_layout.clear_widgets()

        satellite_id = data.get("satellite_id", "Unknown")
        time_field = data.get("time_field", "Unknown")

        self.ids.wod_info_layout.add_widget(Label(text=f"Satellite ID: {satellite_id}\n", color=(0, 0, 0, 1), font_size='30sp'))
        self.ids.wod_info_layout.add_widget(Label(text=f"Time: {time_field}", color=(0, 0, 0, 1), font_size='30sp'))

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Beige"
        Builder.load_file('gui.kv')
        return Gui()

if __name__ == '__main__':
    MainApp().run()
