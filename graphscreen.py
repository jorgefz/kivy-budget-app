
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
import datetime as dt


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
		self.balance_plot.clear()

		# Display the data for one full year
		if (text == "All Year"):
			x = [ dt.datetime.strptime(d, "%d/%m/%Y")
				  for d in self.each_day['date']]
			y = list(self.each_day['balance'])

			# format the time axis using month abbreviations on each 15th day.
			self.balance_plot.ax.xaxis.set_major_locator(
				mdates.MonthLocator(bymonthday=15))
			self.balance_plot.ax.xaxis.set_major_formatter(
				mdates.DateFormatter('%b'))
			label_fmt = lambda x,y: f"{x.strftime('%b %d')}\n£{y:.2f}"
		
		# Display the data for a single month
		else:
			idx = self.each_day['month'] == text
			x = self.each_day['day'][idx]
			y = self.each_day['balance'][idx]
			# Choose roughly the days at the beginning of each week plus the last one
			xticks = [1, 7, 14, 21, 29]
			self.balance_plot.ax.set_xticks(xticks)
			label_fmt = lambda x,y: f"{text} {x:0d}\n£{y:.2f}"

		self.balance_plot.plot(x, y, c='cyan', marker='o', ms=8, mec='k', lw=3,
			hover_labels = dict(fmt = label_fmt))
		self.balance_plot.ax.set_xlabel(text, fontsize=15, c="white")
		self.balance_plot.ax.grid(visible=True, axis='y', c='white', alpha=0.5)
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
		self.balance_plot.clear()

		if (text == "All"):
			x = self.each_day['date']
			y = self.each_day['balance']
		else:
			idx = self.each_day['year'] == int(text)
			x = self.each_day['date'][idx]
			y = self.each_day['balance'][idx]
		
		self.balance_plot.plot(x, y, c='cyan', marker='o', ms=8, mec='k', lw=3)
		self.balance_plot.ax.set_xlabel(text, fontsize=15, c="white")
		self.balance_plot.ax.grid(visible=True, axis='y', c='white', alpha=0.5)
		self.balance_plot.ax.set_xticks([1, 7, 14, 21, 28])
		self.balance_plot.show()

	def on_pre_enter(self):
		self.balance_plot = self.ids.balance_plot
		self.balance_plot.set_theme('dark')

		self.setup_month_menu()
		self.setup_year_menu()

		# set initial plot option
		self.on_month_select("All Year")






