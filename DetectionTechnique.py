'''
Created on Jan 22, 2017

@author: mohame11
'''


import sys
sys.path.append('/Users/mohame11/anaconda/lib/python2.7/site-packages/')
import subprocess
from TestSample import *
#testDic, quota, coreId, q, store, true_mem_size, hyper2id, obj2id, Theta_zh, Psi_sz, smoothedProbs
class DetectionTechnique():
    def __init__(self):
        self.true_mem_size = None
        self.model_path = None
        self.useWindow = None
        self.type = None
        self.model = None
        
    def formOriginalSeq(self, tests):
        if(self.groupActionsByUser == True):
            actions = []
            golds = []
            for t in tests:
                for a in t.actions:
                    actions.append(a)
                for g in t.goldMarkers:
                    golds.append(g)
            return actions, golds
         
        else:
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
