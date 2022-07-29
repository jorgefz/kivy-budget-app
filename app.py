from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp

from kivy.core.window import Window
Window.size = (900, 600)

from graph import GraphScreen
import glob
import pandas as pd

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


class HomeScreen(MDScreen):
	pass


class DataTableScreen(MDScreen):

	dataset = ObjectProperty(None)
	'''Pandas dataframe that holds financial data'''

	columns = ListProperty([])
	'''Column names to display'''

	def _generate_row_data(self) -> pd.DataFrame:
		data = [
			list(row[self.columns])
			for index,row in self.dataset.iterrows() ]
		return data

	def _load_table(self):
		self.table_widget = MDDataTable(
			size_hint= (0.7, 0.8),
			pos_hint= {"center_x": 0.5, "center_y": 0.5},
			use_pagination = True,
			rows_num = 7,
			column_data = [
				("Date", dp(30)),
				("Amount", dp(30)),
				("Balance", dp(30)) ],
			row_data = self._generate_row_data()
		)
		self.add_widget(self.table_widget)

	def on_enter(self):
		self._load_table()



class MainApp(MDApp):

	@staticmethod
	def load_dataset() -> pd.DataFrame:
		'''Load all csv files in the data folder and combine dataframes'''
		datafiles = glob.glob("data/*.csv")
		dataframes = [pd.read_csv(file) for file in datafiles]
		return dataframes[0]

	def process_dataset(self):
		pass

	def build(self):
		self.dataset = MainApp.load_dataset()
		self.balance = self.dataset['Balance'].iloc[0]
		self.balance_text = f"£{self.balance:.2f}"
		self.expenses = self.dataset['Debit Amount'].sum()
		self.expenses_text = f"£{self.expenses:.2f}"
		self.income = self.dataset['Balance'].iloc[-1] - self.balance - self.expenses
		self.income_text = f"£{self.income:.2f}"

		self.theme_cls.theme_style = "Dark"

		screen = Builder.load_file("layout.kv")

		return screen


if __name__ == '__main__':
	sm = ScreenManager()
	sm.add_widget(HomeScreen(name="Home"))
	sm.add_widget(GraphScreen(name="Graphs"))
	sm.add_widget(DataTableScreen(name="Data"))
	MainApp().run()