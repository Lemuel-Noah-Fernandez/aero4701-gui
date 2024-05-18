import json
import os
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

# Define what we want to graph
x = [11, 22, 33, 44, 55, 66, 77, 88, 99, 100]
y = [12, 6, 9, 15, 23, 67, 11, 90, 34, 91]

plt.plot(x, y)
plt.ylabel("Y axis")
plt.xlabel("X axis")

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
            'misc_data.json': self.ids.misc_data_layout
        }

        for file_name, layout in data_files.items():
            file_path = os.path.join(data_dir, file_name)
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if data:
                        self.display_data(layout, data[-1], layout)  # Get the last entry
                    else:
                        self.display_data(layout, None, layout)
            except (FileNotFoundError, json.JSONDecodeError):
                self.display_data(layout, None, layout)

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

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"  
        self.theme_cls.primary_palette = "Beige"
        Builder.load_file('gui.kv')
        return Gui()

if __name__ == '__main__':
    MainApp().run()
