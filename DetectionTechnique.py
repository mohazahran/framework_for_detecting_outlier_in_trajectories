'''
Created on Jan 22, 2017

@author: mohame11
'''
from scipy.stats import chisquare
from collections import OrderedDict
from multiprocessing import Process, Queue

import pandas as pd
#import plac
import numpy as np
import math
import os.path
import cProfile
import _eval_outlier
from MyEnums import *
from TestSample import *
from bokeh.colors import gold

import sys
from astropy import log
sys.path.append('/Users/mohame11/anaconda/lib/python2.7/site-packages/')
import kenlm
#import rnnlm
import subprocess

#testDic, quota, coreId, q, store, true_mem_size, hyper2id, obj2id, Theta_zh, Psi_sz, smoothedProbs
class DetectionTechnique():
    def __init__(self):
        self.true_mem_size = None
        self.model_path = None
        self.useWindow = None
        self.type = None
        self.model = None
        
    def formOriginalSeq(self, tests):
        origSeq = list(tests[0].actions)  
        origGoldMarkers = list(tests[0].goldMarkers)
        if(len(tests) <= 1):
            return origSeq, origGoldMarkers
        for i in range(1,len(tests)):
            a = tests[i].actions[-1]
            g = tests[i].goldMarkers[-1]
            origSeq.append(a)
            origGoldMarkers.append(g)            
        return origSeq, origGoldMarkers
    
    
    def getProbability(self, userId, newSeq):
        pass
    
    def getAllPossibleActions(self):
        pass
    
    def getUserId(self, uid):
        pass
