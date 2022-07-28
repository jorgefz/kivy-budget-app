from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp

import pandas as pd
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg


# Globals
dataset = pd.read_csv("data/halifax_july_2022.csv")
selected_cols = ["Transaction Date", "Debit Amount", "Balance"]
row_data = [ list(row[selected_cols]) for index,row in dataset.iterrows() ]


class HomeScreen(MDScreen):
	pass

class GraphScreen(MDScreen):
	
	def update_graphs(self):
		plt.clf() # clear plot
		self.ids.expense_graph.clear_widgets()

		unique_dates = dataset.drop_duplicates(subset=['Transaction Date'], keep='last')

		plt.plot(unique_dates['Transaction Date'], unique_dates['Balance'])

		self.ids.expense_graph.add_widget(FigureCanvasKivyAgg(figure=plt.gcf()))

	def on_enter(self):
		self.update_graphs()

class DataTableScreen(MDScreen):

	def load_table(self):

		self.table_widget = MDDataTable(
			size_hint= (0.7, 0.8),
			pos_hint= {"center_x": 0.5, "center_y": 0.5},
			use_pagination = True,
			rows_num = 7,
			column_data = [
				("Date", dp(30)),
				("Amount", dp(30)),
				("Balance", dp(30)) ],
			row_data = row_data
		)
		self.add_widget(self.table_widget)

	def on_enter(self):
		self.load_table()


class MainApp(MDApp):

	def build(self):

		from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem

		self.balance = dataset['Balance'][0]
		self.balance_text = u"£" + f"{self.balance:.2f}"
		self.theme_cls.theme_style = "Dark"

		screen = Builder.load_file("layout.kv")

		return screen


if __name__ == '__main__':
	sm = ScreenManager()
	sm.add_widget(HomeScreen(name="Home"))
	sm.add_widget(GraphScreen(name="Graphs"))
	sm.add_widget(DataTableScreen(name="Data"))
	MainApp().run()