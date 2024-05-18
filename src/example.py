from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt

#define what we want to graph
x=[11,22,33,44,55,66,77,88,99,100]
y=[12,6,9,15,23,67,11,90,34,91]

plt.plot(x,y)
plt.ylabel("Y axis")
plt.xlabel("X axis")

#Build our app

class Matty(FloatLayout):
   def __init__(self,**kwargs):
      super().__init__(**kwargs)

      box=self.ids.box
      box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
   

   def save_it(self):
      pass

class MainApp(MDApp):
   def build(self):
      self.theme_cls.theme_style = "Dark"
      self.theme_cls.primary_palette="Tan"
      Builder.load_file('matty.kv')
      return Matty()

MainApp().run()