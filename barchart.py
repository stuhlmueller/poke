#!/usr/bin/python

"""
Implements a continuously updateable barchart for the traits UI.
"""

from enthought.chaco.api import *
from enthought.enable.component_editor import ComponentEditor
from enthought.pyface.timer.api import Timer
from enthought.traits.api import *
from enthought.traits.ui.api import *
import logging
import numpy as np
import settings

logging.basicConfig()


__all__ = "BarChart"


def readable_labels(labels):
    if type(labels[0]) in [np.float64, type(1.0)]:
        return [str(l)[:5] for l in labels]
    else:
        return [str(l) for l in labels]


class BarChart(HasTraits):

    index =  Instance(ArrayDataSource)
    values = Instance(ArrayDataSource)
    title =  Str
    plot =   Instance(BarPlot)

    
    def bounds_func(self, data_low, data_high, margin, tight_bounds):
        return data_low-0.5, data_high+0.5

    
    def configure(self, source, index_name, value_name, index_title='Index',
                  value_title='Count', value_range_kw={},
                  readable_labels=readable_labels):

        self.index = ArrayDataSource(data=getattr(source, index_name))
        self.values = ArrayDataSource(data=getattr(source, value_name))

        self.source = source
        self.index_name = index_name
        self.value_name = value_name
        self.readable_labels = readable_labels

        self.source.on_trait_change(self.source_updated, 'updated')

        index_range = DataRange1D(self.index, bounds_func=self.bounds_func)
        value_range = DataRange1D(self.values, **value_range_kw)

        self.plot = BarPlot(
                index = self.index,
                value = self.values,
                index_range = index_range,
                value_range = value_range,
                index_mapper = LinearMapper(range=index_range),
                value_mapper = LinearMapper(range=value_range),
                bar_width = 0.9,
                fill_color = 0x34352D,
                line_color = 0x34352D,
                antialias = False,
                padding = 80)

        self.plot.bgcolor = 'white'
        self.plot.fill_padding = True
        self.plot.border_visible = False

        self.index_label = LabelAxis(
                self.plot,
                title = index_title,
                positions = [],
                labels = [],
                orientation = 'bottom',
                title_font = "swiss 20",                
                tick_label_font = "swiss 20")

        self.value_label = PlotAxis(
                self.plot,
                orientation = 'left',
                title = value_title,
                title_font = "swiss 20",
                tick_label_font = "swiss 20")

        self.plot.underlays.append(self.value_label)
        self.plot.underlays.append(self.index_label)

    
    def source_updated(self):
        
        index = getattr(self.source, self.index_name)
        value = getattr(self.source, self.value_name)

        if len(index) == len(value):
            i = np.argsort(index)

            self.index.set_data(np.arange(len(index)))
            self.index_label.positions = np.arange(len(index))
            self.values.set_data(np.asarray(value)[i])

            newlabels = self.readable_labels(np.asarray(index)[i])
            
            if newlabels != self.index_label.labels:
                self.index_label.labels = newlabels
                self.index_label.invalidate_and_redraw()
        else:
            logging.warn('skipping BarChart update because index != value')
