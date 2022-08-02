from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from kivymd.uix.toolbar import MDTopAppBar

from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp, sp

from kivy.core.window import Window
#Window.size = (1000, 600)

from graphscreen import GraphScreen
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

from graph import PlotWidget, DonutPlot

class HomeScreen(MDScreen):

	datetime_label = ObjectProperty(None)
	
	def on_pre_enter(self):
		
		now = dt.datetime.now()
		weekday = calendar.day_name[now.weekday()]
		self.date = f"{weekday}, " + now.strftime("%d %B %Y")
		self.time = str(now.strftime("%H:%M:%S"))
		if self.datetime_label:
			self.datetime_label.text = self.date


class DataTableScreen(MDScreen):

	dataset = ObjectProperty(None)
	'''Pandas dataframe that holds financial data'''

	columns = ListProperty([])
	'''Column names to display'''

	def generate_row_data(self) -> pd.DataFrame:
		data = [
			list(row[self.columns])
			for index,row in self.dataset.iterrows() ]
		return data

	def load_table(self):
		self.table_widget = MDDataTable(
			size_hint= (0.9, 0.8),
			pos_hint= {"center_x": 0.5, "center_y": 0.55},
			use_pagination = True,
			rows_num = 7,
			column_data = [
				("Date",    dp(21)),
				("Amount",  dp(18)),
				("Balance", dp(18)) ],
			row_data = self.generate_row_data(),
		)
		self.add_widget(self.table_widget)

	def on_enter(self):
		self.clear_widgets()
		self.load_table()

	
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

		# extract month names
		month_nums = [int(date[3:5]) for date in self.dataset['date']]
		month_names = [ calendar.month_name[n] for n in month_nums]
		self.dataset['month'] = month_names

		# extract weekdays
		weekday_nums = [dt.datetime.strptime(date,"%d/%m/%Y").weekday() for date in self.dataset['date']]
		weekday_names = [calendar.day_name[n] for n in weekday_nums]
		self.dataset['weekday'] = weekday_names
		self.dataset['day'] = [int(date[0:2]) for date in self.dataset['date']]
		self.dataset['year'] = [int(date[6:]) for date in self.dataset['date']]

		# calculate transaction amounts (negative is expense, positive is income)
		debit  = self.dataset['expense']
		credit = self.dataset['income']  
		self.dataset['amount'] = [-d if not np.isnan(d) else c for c,d in zip(credit,debit)]

	@staticmethod
	def sterling(amount: float):
		return f"£{amount:.2f}"

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
		
		self.balance = self.dataset['balance'][time_idx].iloc[0]
		self.expenses = self.dataset[time_idx]['expense'].sum()
		self.income = self.dataset[time_idx]['income'].sum()
		self.profit = self.income - self.expenses

		self.balance_text = MainApp.sterling(self.balance)
		self.expenses_text = MainApp.sterling(self.expenses)
		self.income_text =  MainApp.sterling(self.income)
		self.profit_text =  MainApp.sterling(self.profit)

		self.theme_cls.theme_style = "Dark"

		screen = Builder.load_file("layout.kv")

		return screen


if __name__ == '__main__':
	sm = ScreenManager()
	sm.add_widget(HomeScreen(name="Home"))
	sm.add_widget(GraphScreen(name="Graphs"))
	sm.add_widget(DataTableScreen(name="Data"))
	MainApp().run()