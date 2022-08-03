from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from kivymd.uix.toolbar import MDTopAppBar

from kivymd.uix.datatables import MDDataTable
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

class HomeScreen(MDScreen):

	datetime_label = ObjectProperty(None)
	
	def on_pre_enter(self):
		
		now = dt.datetime.now()
		weekday = calendar.day_name[now.weekday()]
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