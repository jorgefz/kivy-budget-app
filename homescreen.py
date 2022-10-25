
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivy.clock import Clock as KivyClock

from monthpicker import *
from functools import partial
import numpy as np

class HomeScreenScrollList(MDGridLayout):
	'''Holds scrollable content box on the home screen'''	
	
	homescreen = ObjectProperty(None)
	
	balance_plot = ObjectProperty(None)


class HomeScreen(MDScreen):

	topbar = ObjectProperty(None)

	scroll_content = ObjectProperty(None)

	dataset = ObjectProperty(None)

	def plot_month_balance(self):
		plot = self.scroll_content.balance_plot		
		month_name = calendar.month_name[self.month]
		idx = (self.each_day['month'] == month_name)
		idx &= (self.each_day['year'] == self.year)

		if self.month == 1:
			idx_old = (self.each_day['month'] == calendar.month_name[12])
			idx_old &= (self.each_day['year'] == (self.year-1))
		else:
			idx_old = (self.each_day['month'] == calendar.month_name[self.month-1])
			idx_old &= (self.each_day['year'] == self.year)

		x = self.each_day[idx]['day']
		y = self.each_day[idx]['balance']
		
		xold = self.each_day[idx_old]['day']
		yold = self.each_day[idx_old]['balance']

		plot.clear()
		
		plot.ax.plot(xold, yold, c = 'k', alpha=0.3, lw=2)
		# plot.ax.fill_between(xold, yold, color = 'k', alpha=0.3)
		plot.ax.plot(x, y, c = '#4285F4', lw=3)
		# plot.ax.fill_between(x, y, color = '#4285F4', alpha=0.8)
		
		plot.ax.axis('off')
		plot.ax.set_xticks([])
		plot.ax.set_yticks([])
		plot.ax.set_xlim(1, 31)
		ymin = min(y.min() if len(y)>0 else 0, yold.min()) * 0.9
		ymax = max(y.max() if len(y)>0 else 1, yold.max()) * 1.1
		plot.ax.set_ylim(ymin, ymax)
		ylines = np.linspace(ymin, ymax, num = 4)
		for yl in ylines:
			plot.ax.axhline(yl, ls=':', c='k', alpha=0.3)
			if yl > 1000: text = f"{yl/1000:.1f}k"
			else:         text = f"{yl:.1f}"
			plot.ax.annotate(text=text, xy=[1, yl], alpha=0.5, fontsize=9)
		plot.show()


	def on_month_select(self, month, year, *largs):
		if self.topbar is None:
			return
		self.month = month
		self.year = year
		month_name = calendar.month_name[month]
		self.topbar.title = f"{month_name} {year}"	
		self.plot_month_balance()

		idx = (self.dataset['month'] == month_name)
		idx &= (self.dataset['year'] == self.year)

		print(self.dataset[idx]['income'])
		balances_row = self.dataset[idx]['balance']
		balance = 0 if balances_row.shape[0] == 0 else balances_row.iloc[-1]
		income  = self.dataset[idx]['income'].sum()
		expense = self.dataset[idx]['expense'].sum()
		cash_flow = income - expense
		
		self.scroll_content.ids.balance_label.text   = f"£{balance:.2f}"
		self.scroll_content.ids.cash_flow_label.text = f"£{cash_flow:.2f}"
		self.scroll_content.ids.income_label.text    = f"£{income:.2f}"
		self.scroll_content.ids.expenses_label.text  = f"£{expense:.2f}"
		

	def on_month_dialog(self):
		self.month_dialog = MonthPicker(
			on_date_select = self.on_month_select,
			month = self.month,
			year = self.year
		)
		self.month_dialog.open()
	
	def on_pre_enter(self):
		
		now = dt.datetime.now()
		weekday = calendar.day_name[now.weekday()]

		self.date = now.strftime("%A, %d %B %Y")
		self.time = now.strftime("%H:%M:%S")

		self.now = now
		self.month = now.month
		self.year = now.year
	
		KivyClock.schedule_once( partial(self.on_month_select, now.month, now.year), 0)

