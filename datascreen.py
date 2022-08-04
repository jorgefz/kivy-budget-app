
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.scrollview import MDScrollView
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

class MD3Card(MDCard, RoundedRectangularElevationBehavior):
	'''Implements a material design v3 card.'''
	text = StringProperty()


class TransactionCard(MD3Card):

	def __init__(self, *args, **kwargs):
		self.icon = kwargs.pop("icon", "help-circle-outline")
		self.name = kwargs.pop("name", "Transaction")
		self.amount = kwargs.pop("amount", 0.0)
		super().__init__(*args, **kwargs)

	def load(self):
		"""
		MDIcon:
			halign:"left"
		MDLabel:
			padding_x: 15
			halign:"left"
			text:"Costa"
		MDLabel:
			halign:"right"
			text: app.sterling(2.00)
			font_size: self.width * 0.2
		"""
		self.icon_obj = MDIcon(
			halign="left",
			icon=self.icon
		)
		self.vendor_label = MDLabel(
			text = self.name,
			padding_x = 15,
			halign = "left",
			size_hint_x = dp(2),
			#line_color = [1.0, 0.0, 0.0],
			#line_width = dp(1)
		)
		self.amount_label = MDLabel(
			text = f"£{self.amount:,.2f}",
			halign="right",
			#line_color = [1.0, 0.0, 0.0],
			#line_width = dp(1)
		)

		self.add_widget(self.icon_obj)
		self.add_widget(self.vendor_label)
		self.add_widget(self.amount_label)



class DataScreen(MDScreen):

	dataset = ObjectProperty(None)
	'''Pandas dataframe that holds financial data'''

	transaction_list = ObjectProperty(None)
	'''Scrollable transaction list widget'''

	date_label = ObjectProperty(None)
	'''Label widget that displays chosen date'''

	day_spent_label = ObjectProperty(None)
	'''Label widget for the amount of money spent in a day'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.chosen_date = dt.datetime.now()

	def on_date_choice(self, instance, value, date_range):
		self.chosen_date = value
		self.load_transactions()

	def show_date_picker(self):
		date_picker = MDDatePicker(
			year  = self.chosen_date.year,
			month = self.chosen_date.month,
			day   = self.chosen_date.day
		)
		date_picker.bind(on_save = self.on_date_choice)
		date_picker.open()

	def load_transactions(self):
		# Calculate day transactions

		# inefficient, refactor
		idx = self.dataset['date'] == self.chosen_date.strftime("%d/%m/%Y")
		dates = self.dataset[idx]
		tr_num = idx.sum()

		# Update labels
		self.date_label.title = self.chosen_date.strftime("%A, %d %b %Y")
		day_amount = np.abs( dates['expense'].sum() )
		self.day_spent_label.text = f"£{day_amount:,.2f}"

		# print(self.date_label.ids.label_title.font_size)

		# Update transaction cards
		self.transaction_list.clear_widgets()
		card_kw = dict(
			padding = 16,
			size_hint = (None, None),
			size_hint_y = "50dp",
			size_hint_x = self.transaction_list.width,
			elevation = 5
		)

		if(tr_num == 0):
			self.transaction_list.rows = 1
			card = TransactionCard(
				name = f"No transactions", **card_kw
			)
			self.transaction_list.add_widget(card)
			card.load()
			return

		self.transaction_list.rows = tr_num
		for tr in dates.iterrows():
			_, data = tr
			card = TransactionCard(
				name   = data['Transaction Description'],
				amount = data['amount'],
				**card_kw
			)
			self.transaction_list.add_widget(card)
			card.load()

	def on_pre_enter(self):
		self.load_transactions()
		