
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout

from kivy.properties import *

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import matplotlib as mpl
mpl.use("module://kivy.garden.matplotlib.backend_kivy")


class PlotWidget(MDBoxLayout):
	'''
	Interface for showing matplotlib plots on Kivy apps
	
	class MyApp(MDApp):
		def build(self):
			plot = PlotWidget(
				size=(200,200),
				size_hint=(None,None),
				pos_hint = {'center_y': 0.5, 'center_x': 0.5},
			)
			self.add_widget(plot)
			plot.plot([1,2,3], [1,2,3], color='b')
			plot.ax.set_xlabel("X", fontsize=14)
			plot.set_theme('dark')

	MyApp.run()
	'''
	
	def __init__(self, *args, **kwargs):
		'''Arguments solely for the MDBoxLayout parent class'''
		
		# remove kwarg if existing so that kivy doesn't complain
		subplot_kw = kwargs.pop("subplot_kw", dict())
		super().__init__(*args, **kwargs)

		self.fig, self.ax = plt.subplots(1,1, subplot_kw = subplot_kw)
		self.plot_widget = FigureCanvasKivyAgg(figure = self.fig)
		self.show()

		# Fit plot to box layout
		self.fig.tight_layout(pad=5)

		 # This hides the white square that would appear on the bottom left
		self.fig.patch.set_alpha(0.0)

		
	def plot(self, *args, **kwargs):
		''' Produces figure canvas widget, allows replotting '''
		self.ax.plot(*args, **kwargs)

	def show(self):
		'''Allows plot to be displayed as a widget'''
		self.clear_widgets()
		self.plot_widget = FigureCanvasKivyAgg(figure = self.fig)
		self.add_widget(self.plot_widget)

	def clear(self):
		'''Removes the plotted data'''
		# don't use fig.clear(), it will delete the axes as well
		self.ax.clear()

	def set_theme(self, theme: str):
		'''Quick theming - 'dark' or 'light' '''
		 # transparent graph area
		if theme == 'dark':
			color = "white"
			axcolor = "#FFFFFF00"
		elif theme == 'light':
			color = "black"
			axcolor = "white"
		else: return

		self.ax.set_facecolor(axcolor) # Graph area
		self.ax.tick_params(axis='x', colors=color, labelsize=12)
		self.ax.tick_params(axis='y', colors=color, labelsize=12)
		self.ax.get_xaxis().label.set_color(color)
		self.ax.get_yaxis().label.set_color(color)
		# Graph edges
		for key in self.ax.spines:
			self.ax.spines[key].set_color(color)


from typing import List, Tuple, Union

class DonutPlot(PlotWidget):
	
	def __init__(self, *args, **kwargs):
		if not 'subplot_kw' in kwargs: kwargs['subplot_kw'] = dict()
		kwargs['subplot_kw']['projection'] = 'polar'
		super().__init__(*args, **kwargs)

	def plot(self, value: float, limits: Tuple[float,float] = [0,100],
		color: str = "blue", text: str = "",
		textcolor: str = "black", fontsize: float = 10):
		
		# value normalized to interval 0 to 100
		norm = 100.0 * (value - limits[0]) / (limits[1] - limits[0])

		startangle = 90
		x = (norm * np.pi *2)/100
		y = 0.2

		left = (startangle * np.pi *2)/ 360
		self.ax.barh(y, x, left=left, height=1, color=color)
		self.ax.set_ylim(-4,4)
		self.ax.text(0, -3.7, text, ha='center', va='center',
			fontsize = fontsize, color = textcolor)
		self.ax.set_xticks([])
		self.ax.set_yticks([])
		self.ax.spines.clear()
		# Round ends, find a way to adjust size to match the circle width
		# ax.scatter(x+left, y, s=40, color=self.color, zorder=2)
		# ax.scatter(left, y,   s=40, color=self.color, zorder=2)


		
class GraphDataLabel():
	''' Renders hovering annotations over a data point in a plot'''

	@staticmethod
	def hover_callback(event, labelbox, lines, xdata, ydata):
		''' Callback for mouse hovering over a plot '''
		fig = plt.gcf()
		visible = labelbox.get_visible()

		if event.inaxes != plt.gca():
			return
		
		contained, index = lines.contains(event)
		if contained:
			ind = index['ind'][0]
			xp = xdata.iloc[ind]
			yp = ydata.iloc[ind]
			x,y = lines.get_data()
			labelbox.xy = (x[ind], y[ind])
			labelbox.set_text(f"{xp}\n{yp}")
			labelbox.set_visible(True)
			fig.canvas.draw_idle()
		elif visible:
			labelbox.set_visible(False)
			fig.canvas.draw_idle()


	@staticmethod
	def show(xdata, ydata, lines):
		''' Enables hovering annotations over pointed data point '''
		fig = plt.gcf()
		axs = plt.gca()
		labelbox = axs.annotate(
			text='',
			xy=(0,0),
			xytext=(15,15),
			textcoords='offset points',
			bbox={'boxstyle':'round', 'fc':'white', 'alpha':1.0},
			arrowprops={'arrowstyle':'-|>', 'color':'white'}
		)
		labelbox.set_visible(False)

		callback = lambda event: GraphDataLabel.hover_callback(
			event, labelbox, lines, xdata, ydata)
		fig.canvas.mpl_connect('motion_notify_event', callback)



class Graph(MDBoxLayout):
	'''Skeleton Graph class. Allows displaying Matplotlib plots.'''
	
	dataset = ObjectProperty(None)
	'''Pandas dataframe that holds financial data'''

	def clear(self):
		'''Clears previous plots and all child widgets'''
		plt.clf() # clear plot
		self.clear_widgets()

	def show(self):
		'''Draws the plot'''
		self.add_widget(FigureCanvasKivyAgg(figure=plt.gcf()))

	def update(self, dataset = None):
		if dataset is not None: self.dataset = dataset
		self.clear()
		self.show()


class ScatterGraph(Graph):
	'''Renders a scatter plot'''

	xfield = StringProperty("")
	'''Dataframe field reference for the x-axis data'''
	yfield = StringProperty("")
	'''Dataframe field reference for the y-axis data'''
	floating_labels = BooleanProperty(False)
	'''Displays data point info when mouse hovers over it'''

	# plot_options = DictProperty({})
	''' Keyword arguments for pyplot.plot '''

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


	def update(self, xfield=None, yfield=None):
		self.clear()

		if(self.dataset is None):
			self.add_widget(MDLabel(
				text = "No data to display",
				halign = "center",
				font_style = "H5"
			))
			return

		if xfield is None: xfield = self.xfield
		if yfield is None: yfield = self.yfield
		
		x = self.dataset[self.xfield]
		y = self.dataset[self.yfield]

		lines, = plt.plot(x, y, marker = "s", ms = 10, mfc = 'b', mec = 'b')
		self.style_plot(lines)

		if self.floating_labels is True:
			GraphDataLabel.show(x, y, lines)
		
		self.show()


