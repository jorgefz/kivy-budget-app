from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import (
	MDFlatButton,
	MDRaisedButton,
	MDIconButton,
	MDRectangleFlatButton,
	MDFillRoundFlatButton,
	MDTextButton
)
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.uix.label import Label as KivyLabel

from kivy.metrics import dp, sp

from kivy.core.window import Window
#Window.size = (1000, 600)

import glob
import pandas as pd
import datetime as dt
import calendar
import numpy as np

from kivy.properties import (
	NumericProperty,
	OptionProperty,
	ObjectProperty,
	StringProperty,
	ListProperty,
	BooleanProperty,
	VariableListProperty,
	ReferenceListProperty
)

from typing import Union

from graph import PlotWidget, DonutPlot
from graphscreen import GraphScreen
from datascreen import DataScreen
from functools import partial


class MonthDialogContent(MDBoxLayout):

	big_date_label = ObjectProperty(None)
	year_label = ObjectProperty(None)
	
	def __init__(self, *args, month=None, year=None, **kwargs):
		super().__init__(*args, **kwargs)

		self.today = dt.datetime.today()
		self.month = self.today.month if month is None else month
		self.year  = self.today.year  if year is None else year

		self.load_month_buttons()

	def load_month_buttons(self):
		calendar_grid = self.ids.monthdiag_calendar
		item_count = calendar_grid.rows * calendar_grid.cols
		month_abbr = [calendar.month_abbr[i] for i in range(1,item_count+1)]

		calendar_grid.clear_widgets()

		for i in range(item_count):
			month = i+1

			if (month == self.month):
				button_cls = MDFillRoundFlatButton
			elif (month == self.today.month and self.year == self.today.year):
				button_cls = MDRectangleFlatButton
			else:
				button_cls = MDFlatButton

			on_release = partial(self.on_month_select, i+1)
			btn = button_cls(
				text = month_abbr[i],
				size = (dp(35), dp(35)),
        		size_hint = (None, None),
				on_release = on_release,
			)
			calendar_grid.add_widget( btn )

	def update_labels(self):
		self.year_label.text = str(self.year)
		self.big_date_label.text = f"{calendar.month_abbr[self.month]}. {str(self.year)}"

	def on_month_select(self, month_number, ins):
		self.month = month_number
		# refactor this - simply change button colors using instance
		self.load_month_buttons()
		self.update_labels()

	def on_year_select(self, year, *largs):
		self.year = year
		# refactor this - check if selected year is now and change button colors
		self.load_month_buttons()
		self.update_labels()

	def get_month_year(self):
		return self.month, self.year


class MonthPicker(MDDialog):

	'''
	Similar to a date picker, this dialog menu allows to choose only month and year.
	Behaves exactly like MDDialog for opening and dismissing.

	Parameters
	----------
		on_date_select:		(callable) Function called when a date is chosen
							and the OK button is pressed. Must have the signature
							`on_date_select(month:int, year:int)`

		*args, **kwargs		Arguments passed to MDDialog
	'''

	def __init__(self, *args, on_date_select = lambda m,y:None, **kwargs):
		kwargs['type'] = "custom"
		kwargs['content_cls'] = MonthDialogContent()
		kwargs['buttons'] = [
			MDFlatButton(text="CANCEL", on_release=self.dismiss),
			MDRaisedButton(text="OK",   on_release=self.on_date_chosen),
		]
		super().__init__(*args, **kwargs)
		self.on_date_select = on_date_select

	def get_selection(self):
		return self.content_cls.get_month_year()

	def on_date_chosen(self, *largs):
		month, year = self.get_selection()
		self.on_date_select(month, year)
		self.dismiss()



class HomeScreen(MDScreen):

	datetime_label = ObjectProperty(None)

	def on_month_select(self, month, year):
		self.datetime_label.text = f"{calendar.month_name[month]} {year}"

	def on_month_dialog(self):
		self.month_dialog = MonthPicker(on_date_select = self.on_month_select)
		self.month_dialog.open()
	
	def on_pre_enter(self):
		
		now = dt.datetime.now()
		weekday = calendar.day_name[now.weekday()]

		self.now = now
		self.date = f"{weekday}, " + now.strftime("%d %B %Y")
		self.time = str(now.strftime("%H:%M:%S"))

		if self.datetime_label:
			self.datetime_label.text = self.date




	
def get_daily_data(dataset: pd.DataFrame)-> pd.DataFrame:
	return dataset.drop_duplicates(subset=['date'], keep='last')[::-1]

def get_data_of_month(dataset: pd.DataFrame, month: str) -> pd.DataFrame:
	month_num = str(list(calendar.month_name).index(month))
	if len(month_num) < 2: month_num = '0' + month_num
	return dataset['Date']




class MainApp(MDApp):

	@staticmethod
	def load_dataset() -> pd.DataFrame:
		'''Load all csv files in the data folder and combine dataframes'''
		datafiles = glob.glob("data/*.csv")
		dataframes = [pd.read_csv(file) for file in datafiles]
		dataset = pd.concat(dataframes)
		return dataset


	def cleanup_dataset(self):
		# simplify column names
		names = {
			'Transaction Date': 'date',
			'Balance': 'balance',
			'Debit Amount': 'expense',
			'Credit Amount': 'income'
		}
		self.dataset = self.dataset.rename(names, axis='columns')

		# generate datetime objects
		self.dataset['datetime'] = [
			dt.datetime.strptime(d,"%d/%m/%Y")
			for d in self.dataset['date'] ]

		# extract inidividual date components
		month_nums = [date.month for date in self.dataset['datetime']]
		month_names = [ calendar.month_name[n] for n in month_nums]
		self.dataset['month'] = month_names
		self.dataset['day']  = [date.day  for date in self.dataset['datetime']]
		self.dataset['year'] = [date.year for date in self.dataset['datetime']]

		# extract weekdays names
		weekday_nums = [date.weekday() for date in self.dataset['datetime']]
		weekday_names = [calendar.day_name[n] for n in weekday_nums]
		self.dataset['weekday'] = weekday_names

		# calculate transaction amounts (negative is expense, positive is income)
		debit  = self.dataset['expense']
		credit = self.dataset['income'] 
		self.dataset['amount'] = [-d if not np.isnan(d) else c for c,d in zip(credit,debit)]


	@staticmethod
	def sterling(amount: Union[float,str]):
		if isinstance(amount,str): return '£'+amount
		return f"£{amount:,.2f}"

	def build(self):
		self.dataset = MainApp.load_dataset()
		self.cleanup_dataset()

		self.each_day = self.dataset.drop_duplicates(subset=['date'], keep='last')[::-1]

		self.this_year = dt.datetime.now().year
		last_month_num = dt.datetime.now().month - 1
		if last_month_num == 0:
			last_month_num = 12
			self.this_year -= 1
		self.last_month = calendar.month_name[last_month_num]
		self.this_year = str(self.this_year)

		time_idx = self.dataset['month'] == self.last_month
		time_idx &= int(self.this_year) == self.dataset['year']

		self.balance = self.dataset['balance'][time_idx].iloc[0]
		self.expenses = self.dataset[time_idx]['expense'].sum()
		self.income = self.dataset[time_idx]['income'].sum()
		self.profit = self.income - self.expenses

		self.balance_text = MainApp.sterling(self.balance)
		self.expenses_text = MainApp.sterling(self.expenses)
		self.income_text =  MainApp.sterling(self.income)
		self.profit_text =  MainApp.sterling(self.profit)

		# self.theme_cls.primary_palette = "BlueGray"
		self.theme_str = "Light"
		self.theme_cls.theme_style = self.theme_str

		screen = Builder.load_file("layout.kv")

		return screen


if __name__ == '__main__':
	sm = ScreenManager()
	sm.add_widget(HomeScreen(name="Home"))
	sm.add_widget(GraphScreen(name="Graphs"))
	sm.add_widget(DataScreen(name="Data"))
	MainApp().run()