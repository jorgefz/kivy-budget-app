
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout

from kivy.properties import *

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from typing import List, Tuple, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import matplotlib as mpl
mpl.use("module://kivy.garden.matplotlib.backend_kivy")


class PlotDataLabels():
	''' Renders hovering annotations over a data point in a plot'''

	@staticmethod
	def hover_callback(event, fig, ax, labelbox, lines, xdata, ydata, fmt):
		''' Callback for mouse hovering over a plot '''
		visible = labelbox.get_visible()

		if event.inaxes != ax:
			return

		# pandas objects are indexed with extra variable iloc[]
		x_is_pd = isinstance(xdata, (pd.DataFrame,pd.Series))
		y_is_pd = isinstance(ydata, (pd.DataFrame,pd.Series))

		contained, index = lines.contains(event)
		if contained:
			ind = index['ind'][0]
			x,y = lines.get_data()
			xp = xdata.iloc[ind] if x_is_pd else xdata[ind]
			yp = ydata.iloc[ind] if y_is_pd else ydata[ind]
			labelbox.xy = (x[ind], y[ind])
			labelbox.set_text(fmt(xp,yp))
			labelbox.set_visible(True)
			fig.canvas.draw_idle()
		elif visible:
			labelbox.set_visible(False)
			fig.canvas.draw_idle()


	@staticmethod
	def show(fig, axs, lines, xdata, ydata, **kwargs):
		''' Enables hovering annotations over pointed data point '''
		# custom keyword - does not belong to axis.annotate
		fmt = kwargs.pop('fmt')
		# Overwrite text and xy
		kwargs['text'] = '',	
		kwargs['xy']   = (0,0),
		# Defaults for the others
		kwargs.setdefault('textcoords', 'offset points')
		kwargs.setdefault('xytext',     (15,15))
		kwargs.setdefault('bbox',       {'boxstyle':'round', 'fc':'white', 'alpha':0.5})
		kwargs.setdefault('arrowprops', {'arrowstyle':'-|>', 'color':'white'})
		kwargs.setdefault('fontsize', 12)

		labelbox = axs.annotate(**kwargs)
		labelbox.set_visible(False)

		callback = lambda event: PlotDataLabels.hover_callback(
			event, fig, axs, labelbox, lines, xdata, ydata, fmt)
		fig.canvas.mpl_connect('motion_notify_event', callback)



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
		'''
		Produces figure canvas widget, allows replotting.
		Pass the same arguments as to plt.plot()
		See 'https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html'

		Extra arguments:
			hover_labels:	dict, optional
							Displays an annotation with info on one data point
							when the mouse hovers over a data point in the plot.
							If left undefined, the annotations will not be show.
							If provided with an empty dict, the annotations will
							be shown using default parameters.
							*See below for a list of accepted parameters
							for hover_labels.

		*Parameters for hover_labels:
			fmt:			callable, optional
							Function that receives the x,y values of a data point
							and returns a formatted string.
							By default, it is set to `lambda x,y: f"{x}\n{y}"`.
			Additional arguments sent to Axis.annotate,
			except 'text' and 'xy', which will be overwritten.
		'''

		hover_labels = kwargs.pop("hover_labels", None)
		line_info = self.ax.plot(*args, **kwargs)

		if not isinstance(hover_labels, dict):
			return line_info

		line = line_info[0]
		hover_labels.setdefault("fmt", lambda x,y: f"{x}\n{y}")
		x = line._xorig
		y = line._yorig
		PlotDataLabels.show(self.fig, self.ax, line, x, y, **hover_labels)
		

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

	def format_axis(self, formatter: callable, axis: str):
		if axis.lower() == 'x':
			self.ax.xaxis.set_major_formatter(formatter)
		elif axis.lower() == 'y':
			self.ax.yaxis.set_major_formatter(formatter)
		else:
			raise ValueError("axis must be 'x' or 'y'")


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


