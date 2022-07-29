
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.properties import (
	NumericProperty,
	OptionProperty,
	ObjectProperty,
	StringProperty,
	BooleanProperty,
	VariableListProperty,
	ReferenceListProperty
)

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib as mpl
mpl.use("module://kivy.garden.matplotlib.backend_kivy")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Graph(MDBoxLayout):
	'''Graph class. Allows displaying Matplotlib plots.'''
	
	dataset = ObjectProperty(None)
	'''Pandas dataframe that holds financial data'''

	def update(self):
		pass


class ScatterGraph(Graph):
	'''Renders a scatter plot'''

	xfield = StringProperty("")
	'''Dataframe field reference for the x-axis data'''
	yfield = StringProperty("")
	'''Dataframe field reference for the y-axis data'''
	floating_labels = BooleanProperty(False)
	'''Displays data point info when mouse hovers over it'''

	def _update_floating_label(self, labelbox, index, line):
		x,y = line.get_data()
		data_index = index["ind"][0]
		labelbox.xy = (x[data_index], y[data_index])
		date    = self.dataset[self.xfield].iloc[data_index]
		balance = self.dataset[self.yfield].iloc[data_index]
		labelbox.set_text(f"{date}\n£{balance}")

	def _setup_floating_labels(self, lines):
		""" Enables hovering annotations over pointed data point """
		fig = plt.gcf()
		axs = plt.gca() # problematic on subplots?
		labelbox = axs.annotate(
			text='',
			xy=(0,0),
			xytext=(15,15),
			textcoords='offset points',
			bbox={'boxstyle':'round', 'fc':'white', 'alpha':1.0},
			arrowprops={'arrowstyle':'-|>', 'color':'white'}
		)
		labelbox.set_visible(False)

		def hover_callback(event):
			''' Callback for mouse hovering over a plot '''
			nonlocal labelbox, lines
			visible = labelbox.get_visible()
			if event.inaxes == plt.gca():
				contained, index = lines.contains(event)
				if contained:
					self._update_floating_label(
						labelbox, index, lines
					)
					labelbox.set_visible(True)
					fig.canvas.draw_idle()
				else:
					if visible:
						labelbox.set_visible(False)
						fig.canvas.draw_idle()

		fig.canvas.mpl_connect('motion_notify_event', hover_callback)

	def style_plot(self, lines):
		fig = plt.gcf()
		axs = fig.axes

		# transparent background outside graph area
		fig.patch.set_alpha(0.0)

		for ax in axs:
			 # transparent graph area
			ax.set_facecolor("#FFFFFF00")
			
			ax.tick_params(axis='x', colors='white', labelsize=12)
			ax.tick_params(axis='y', colors='white', labelsize=12)
			
			# make graph edges visible in dark mode
			for key in ax.spines:
				ax.spines[key].set_color("white")

			# Format axis ticks
			yfmt = lambda y, pos: f"£{y:.0f}"
			ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(yfmt))

			ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
			ax.format_xdata = mdates.DateFormatter('%d')

		# hovering data point label
		if self.floating_labels is True:
			self._setup_floating_labels(lines)

	def update(self):
		plt.clf() # clear plot
		self.clear_widgets()

		if(self.dataset is None):
			self.add_widget(MDLabel(
				text = "No data to display",
				halign = "center",
				font_style = "H5"
			))
			return

		x = self.dataset[self.xfield]
		y = self.dataset[self.yfield]

		lines, = plt.plot(x, y, marker = "s", ms = 10, mfc = 'b', mec = 'b')
		self.style_plot(lines)
		
		self.add_widget(FigureCanvasKivyAgg(figure=plt.gcf()))


class GraphScreen(MDScreen):

	def update_graphs(self):
		for widget in self.children:
			if issubclass(type(widget), Graph):
				widget.update()

	def on_enter(self):
		self.update_graphs()
		
		
				