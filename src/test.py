from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

# Define what we want to graph
x = [11, 22, 33, 44, 55, 66, 77, 88, 99, 100]
y = [12, 6, 9, 15, 23, 67, 11, 90, 34, 91]

plt.plot(x, y)
plt.ylabel("Y axis")
plt.xlabel("X axis")

class Gui(FloatLayout):
    def on_kv_post(self, base_widget):
        self.ids.plot_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Tan"
        Builder.load_file('test.kv')
        return Gui()

if __name__ == '__main__':
    MainApp().run()
