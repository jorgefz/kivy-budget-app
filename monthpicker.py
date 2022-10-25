

import datetime as dt
import calendar
from functools import partial

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card.card import MDSeparator
from kivymd.uix.button import (
	MDFlatButton,
	MDRaisedButton,
	MDRoundFlatButton,
	MDFillRoundFlatButton,
	MDRectangleFlatButton
)

from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty


class MonthDialogContent(MDBoxLayout):

	big_date_label = ObjectProperty(None)
	year_label = ObjectProperty(None)
	
	def __init__(self, *args, month=None, year=None, **kwargs):
		super().__init__(*args, **kwargs)

		self.today = dt.datetime.today()
		self.month = self.today.month if month is None else month
		self.year  = self.today.year  if year is None else year

		self.load_month_buttons()
		self.update_labels()

	def load_month_buttons(self):
		calendar_grid = self.ids.monthdiag_calendar
		item_count = calendar_grid.rows * calendar_grid.cols
		month_abbr = [calendar.month_abbr[i] for i in range(1,item_count+1)]

		calendar_grid.clear_widgets()

		self.month_buttons = [None] * item_count

		for i in range(item_count):
			month = i+1

			if (month == self.month):
				button_cls = MDFillRoundFlatButton
			elif (month == self.today.month and self.year == self.today.year):
				button_cls = MDRoundFlatButton # MDRectangleFlatButton
			else:
				button_cls = MDFlatButton

			on_release = partial(self.on_month_select, i+1)
			self.month_buttons[i] = button_cls(
				text = month_abbr[i],
				size = (dp(35), dp(35)),
        		size_hint = (None, None),
				on_release = on_release,
			)

		for btn in self.month_buttons:
			calendar_grid.add_widget(btn)
	

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
							`on_date_select(month: int, year: int)`
		month:				(float) Default month on initialisation (as a number)
		year:				(float) Default year on initialisation

		*args, **kwargs		Arguments passed to MDDialog
	'''

	def __init__(self, *args, 
		month = None,
		year = None,
		on_date_select = lambda m,y:None,
		**kwargs ):

		kwargs['type'] = "custom"
		kwargs['content_cls'] = MonthDialogContent(month=month, year=year)
		kwargs['buttons'] = [
			MDFlatButton(text="CANCEL", on_release=self.dismiss),
			MDRaisedButton(text="OK",   on_release=self.date_chosen),
		]
		super().__init__(*args, **kwargs)
		self.on_date_select = on_date_select

	def get_selection(self):
		'''Returns the month and year currently selected within the picker'''
		return self.content_cls.get_month_year()

	def date_chosen(self, *largs):
		month, year = self.get_selection()
		self.on_date_select(month, year)
		self.dismiss()
