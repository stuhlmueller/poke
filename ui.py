#!/usr/bin/python

"""
Visualizes continuously changing histogram data.
"""

from barchart import BarChart
from enthought.chaco.api import *
from enthought.enable.component_editor import ComponentEditor
from enthought.pyface.timer.api import Timer
from enthought.traits.api import *
from enthought.traits.ui.api import *
from hashable import make_hashable
import IPython
import db
import logging
import numpy as np
import settings
import sys

logger = logging.getLogger('poke-ui')
logger.addHandler(logging.FileHandler(settings.LOGFILE_UI))
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)
    
def normalize(vals):
    return vals/np.sum(vals)

def discrete_hist(vals):
    h = {}
    for v in vals:
        h.setdefault(v, 0.0)
        h[v] += 1
    entries = sorted(h.items())
    x = [str(e[0]) for e in entries]
    y = normalize([e[1] for e in entries])
    return x, y

def continuous_hist(vals):
    y, bounds = np.histogram(vals, density=True)
    x = [(a+b)/2.0 for (a, b) in zip(bounds, bounds[1:])]
    return x, y

def is_continuous(vals):
    assert vals
    if ((type(vals[0]) == type(1.0)) and not int(vals[0]) == vals[0]):
        return True
    else:
        return False

def hist(vals):
    if not vals:
        return [], []
    if is_continuous(vals):
        return continuous_hist(vals)        
    else:
        return discrete_hist(make_hashable(vals))

    
class SQLiteGenerator(object):
    
    def __init__(self):
        self.hist_x = []
        self.hist_y = []        
        self.hists = []
        self.data = {}

    def update(self):
        conn = db.connect(settings.DATABASE)
        raw_data = db.getdata(conn)
        if raw_data == None:
            logger.info("data is None, skipping ui update...")
            return
        raw_data = list(raw_data)
        conn.close()
        if not raw_data:
            logger.info("no data, skipping ui update...")
            return        
        data = sorted(raw_data, reverse=True)[:settings.WINDOWSIZE]
        i, pairs = data[0]
        logger.info(str((i, pairs)))
        
        self.vars = [var for [var, val] in pairs]
        
        self.data = {}
        for (i, pairs) in data:
            for [var, val] in pairs:
                if var in self.vars:
                    self.data.setdefault(var, [])
                    self.data[var].append(val)
        
        self.hists = {}
        for var in self.vars:
            self.hists[var] = hist(self.data[var])
    
    def gethist(self):
        try:
            self.update()
        except Exception, e:
            logger.info("update failed: %s" % e)
        if self.hists:
            return self.hists[self.vars[-1]]
        else:
            return [], []


class SimulationGenerator(object):

    def __init__(self):
        self.hist_x = [str(n)[:3] for n in np.random.random(5)*10]
        self.hist_y = np.random.random(5)*10
        self.data = [0.0]
        self.windowsize = 500
    
    def update(self):
        self.data += [np.random.normal(self.data[-1])*.1]
        self.data = self.data[-self.windowsize:]
        ys, bounds = np.histogram(self.data, density=True)
        self.hist_y = normalize(ys)
        self.hist_x = ["%s..%s" % (str(a)[:5], str(b)[:5]) for (a, b) in zip(bounds, bounds[1:])]
    
    def gethist(self):
        self.update()
        return self.hist_x, self.hist_y


class HistSource(HasTraits):
    
    x = Array
    y = Array
    updated = Button
    generator = Any

    @on_trait_change('x, y')
    def update(self):
        self.updated = True
    
    def data_reload(self):
        self.x, self.y = self.generator.gethist()


class BarChartHandler(Controller):

    timer = Instance(Timer)
    source = Any
    
    def __init__(self, *args, **kwargs):
        Controller.__init__(self, *args, **kwargs)
        self.timer = Timer(50, self.tick)

    def tick(self):
        source = self.info.object.source
        source.data_reload()


def start_ui():
    db.reset(settings.DATABASE)
    handler = BarChartHandler()
    source = HistSource(generator=SQLiteGenerator())
    model = BarChart()    
    model.configure(source, 'x', 'y',
                    value_range_kw = { "low" : 0.0, "high" : 1.0 },
                    index_title = 'Value',
                    value_title = 'Probability')
    view = View(Item('plot',
                     editor = ComponentEditor(size=(400,400)),
                     show_label = False),
                title = "Church",
                resizable = True,
                height = 400,
                width = 360)
    model.configure_traits(handler=handler, view=view)


if __name__ == '__main__':
    start_ui()
