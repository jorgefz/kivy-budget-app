
from multiprocessing.managers import DictProxy
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivy.properties import (
	NumericProperty,
	OptionProperty,
	ObjectProperty,
	StringProperty,
	BooleanProperty,
	ListProperty,
	VariableListProperty,
	ReferenceListProperty,
)

from kivy.properties import *

from kivymd.uix.button import MDTextButton, MDFlatButton, MDRaisedButton
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu

from graph import *

from functools import partial

import calendar



class MonthDropdown(MDDropdownMenu):

	def __init__(self, *args, **kwargs):
		self.month_names = [calendar.month_name[i] for i in range(1,13)]
		self.choice = self.month_names[0]
		self.select_callback = kwargs.get("on_select", lambda _:None)
		kwargs['items'] = [{
			"text": m,
			"viewclass": "OneLineListItem",
			"on_release": lambda x=m: self.on_select(x)	
		} for m in self.month_names]
		super().__init__(*args, **kwargs)

	def on_select(self, text):
		self.caller.text = text
		self.choice = text
		self.select_callback(text)
		self.dismiss()

	def get_choice(self):
		return self.choice



class GraphScreen(MDScreen):

	dataset = ObjectProperty(None)

	each_day = ObjectProperty(None)

	def setup_month_menu(self):
		month_options = ["All Year"] + [calendar.month_name[i] for i in range(1,13)]

		month_items = [ dict(
			text = m,
			viewclass = "OneLineListItem",
			on_release = partial(self.on_month_select, m)
		) for m in month_options ]

		self.month_dropdown = MDDropdownMenu(
			caller =self.ids.month_selection,
			items = month_items,
			width_mult = 2,
		)

	
	def on_month_select(self, text):
		print(text)
		if (text == "All Year"):
			x = self.each_day['date']
			y = self.each_day['balance']
		else:
			x = self.each_day['day'][self.each_day['month'] == text]
			y = self.each_day['balance'][self.each_day['month'] == text]
		
		self.balance_plot.clear()
		self.balance_plot.plot(x, y, c='b')
		self.balance_plot.show()

	def setup_year_menu(self):
		years = sorted(self.each_day['year'].unique())
		year_options = ['All'] + [str(y) for y in years]

		year_items = [ dict(
			text = m,
			viewclass = "OneLineListItem",
			on_release = partial(self.on_year_select, m)
		) for m in year_options ]

		self.year_dropdown = MDDropdownMenu(
			caller =self.ids.year_selection,
			items = year_items,
			width_mult = 2,
		)

	def on_year_select(self, text):
		print(text)
		if (text == "All"):
			x = self.each_day['date']
			y = self.each_day['balance']
		else:
			x = self.each_day['date'][self.each_day['year'] == text]
			y = self.each_day['balance'][self.each_day['year'] == text]
		
		self.balance_plot.clear()
		self.balance_plot.plot(x, y, c='b')
		self.balance_plot.show()

	def on_enter(self):
		self.balance_plot = PlotWidget(
			size = (700,500),
			size_hint = (None,None),
			pos_hint  = {'center_x': 0.6, 'center_y': 0.5}
		)
		self.add_widget(self.balance_plot)
		self.balance_plot.set_theme('dark')

		self.balance_plot.plot([1,2,3])
		
		self.setup_month_menu()
		self.setup_year_menu()






