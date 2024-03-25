## __init__

"""Functions for running Exponential Random Graph Model (ERGM) analysis on networks.

Code implementation utilises the RPy2 package to emulate R's ERGM library. 

Notes
-----
    * RPy2: https://rpy2.github.io/doc/latest/html/index.html
    * R ERGM: https://cran.r-project.org/web/packages/ergm/ergm.pdf 
"""


import rpy2 as r
globals()['r'] = r

from rpy2 import robjects
globals()['robjects'] = robjects

import rpy2.robjects.packages as rpackages
globals()['rpackages'] = rpackages

from rpy2.robjects import lib
globals()['libr'] = lib

from rpy2.robjects.packages import importr
globals()['importr'] = importr

from rpy2.robjects import IntVector
globals()['IntVector'] = IntVector

from rpy2.robjects import Formula
globals()['Formula'] = Formula

from rpy2.robjects import numpy2ri
globals()['numpy2ri'] = numpy2ri

from rpy2.robjects import pandas2ri
globals()['pandas2ri'] = pandas2ri

numpy2ri.activate()

# globals()['r_emulator'] = r_emulator

globals()['base'] = importr('base')
globals()['utils'] = importr('utils')

utils.chooseCRANmirror(ind=1)
utils.install_packages('ergm')
utils.install_packages('igraph')

globals()['ergm'] = importr('ergm', on_conflict="warn")
globals()['networkr'] = importr('network', on_conflict="warn")

from .ergm_functions import casenet_fit_ergm, case_fit_ergm, create_ergm, fit_ergm, edge_probabilities, casenet_edge_probabilities, case_edge_probabilities, ergm_edge_probabilities