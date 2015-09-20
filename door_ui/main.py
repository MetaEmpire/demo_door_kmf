import kivy
kivy.require('1.9.0')  # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.label import Label
import time
from kivy.uix.behaviors import ButtonBehavior

#from cobs_serial import cobs_serial

'''
main.py

Demo Door wip GUI.

Uses Kivy 1.9.0
'''

class NearDevices(Label):
	my_text = "Test"
	
class DoorStatus(ButtonBehavior, Image):
	#examples of controlling widget image content
	def on_press(self):
		self.source = "unlocked.png"
	def on_release(self):
		self.source = "locked.png"
	
class EventLog(Widget):
	my_text3 = StringProperty(None)
	
	#probably crashing the program, should probably use a list
	def update(self, dt):
		self.my_text3 = self.my_text3 + "\nExample Event " + time.strftime("%H:%M:%S")
		#attempt to read cobs frame from serial
		#if whitelisted open door, post to even log either way, ex "unauthorized attempt, #ID @ <timestamp>"
		
		
class DemoApp(App):

    def build(self):
		layout = GridLayout(cols=2)
		inner_layout = GridLayout(rows=2)
		
		#right hand top widget
		#inner_layout.add_widget(Button(text='Hello 1')) 
		#inner_layout.add_widget(Image(source='locked.png'))
		#wimg = Image(source = "locked.png")
		wimg = DoorStatus()
		wimg.source = "locked.png"
		inner_layout.add_widget(wimg)
		#wimg.source = "unlocked.png" #changes the image, no need to reload here, maybe elsewhere
		
		#right hand bottom widget
		#inner_layout.add_widget(Button(text='World 1')) 
		wlab = Label(text = "Nearby devices: \nBadge 1337\nBadge 2")
		#wlab.halign = 'right' #aligns text, but not widget position
		#wlab.valign = 'top'
		
		#wlab = NearDevices()
		inner_layout.add_widget(wlab)
		
		el = EventLog()
		#st = ScrollView()
		#st.add_widget(el)
		Clock.schedule_interval(el.update, 60.0 / 60.0)
		#layout.add_widget(el) #top level left widget
		layout.add_widget(el)
		layout.add_widget(inner_layout) #top level right widget
		return layout
	
if __name__ == '__main__':
    DemoApp().run()
