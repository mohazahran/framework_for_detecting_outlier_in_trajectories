'''
Created on Apr 11, 2017

@author: mohame11
'''

from DetectionTechnique import *
from MyEnums import *
import os.path
import math 
import random
import numpy as np

class BagOfActions (DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)  
        self.type = SEQ_PROB.BAG_OF_ACTIONS
        self.allActions = []
        #self.smoothingParam = 1.0
       
        
    def loadModel(self):
        self.calculatingItemsFreq(self.smoothingParam)
        for action in self.smoothedProbs:
            self.allActions.append(action)
        
    
    def getProbability(self, userId, newSeq):
        logProb = 0.0
        for action in newSeq:
            logProb += self.smoothedProbs[action]
        return logProb
            
        
    def prepareTestSet(self):
        testDic = {}
        print(">>> Preparing testset ...")
        testSetCount = 0
        r = open(self.SEQ_FILE_PATH, 'r')  
        user = -1  
        for line in r:
            line = line.strip() 
            tmp = line.split()  
            actionStartIndex = 0
            #user += 1
            if (self.DATA_HAS_USER_INFO == True):
                user = tmp[0]   
                actionStartIndex = 1
            else:
                user += 1
            if(self.VARIABLE_SIZED_DATA == True):
                if('###' not in tmp):
                    seq = tmp[actionStartIndex:]
                    goldMarkers = ['false']*len(seq)
                else:
                    indx = tmp.index('###')
                    seq = tmp[:indx]
                    goldMarkers = tmp[indx+1:]
            #print(seq,goldMarkers)
            else:
                seq = tmp[actionStartIndex:self.true_mem_size+2]
                goldMarkers = tmp[self.true_mem_size+2:]
                if(len(goldMarkers) != len(seq)):
                    goldMarkers = ['false']*len(seq)
       
            t = TestSample()  
            t.user = user
            t.actions = list(seq)
            t.goldMarkers = list(goldMarkers)   
            
            testSetCount += 1
            if(user in testDic):
                testDic[user].append(t)                                                    
            else:
                testDic[user]=[t]
        r.close()
        if(self.useWindow == USE_WINDOW.FALSE): # we need to use the original sequence instead of overlapping windows
            testSetCount = len(testDic)
            for u in testDic:
                tests = testDic[u]
                originalSeq, originalGoldMarkers = self.formOriginalSeq(tests)
                t = TestSample()  
                t.user = u
                t.actions = list(originalSeq)
                t.goldMarkers = list(originalGoldMarkers)   
                testDic[u] = [t]
        return testDic, testSetCount         
        
        

        
              
#self, testDic, quota, coreId, q, store, true_mem_size, hyper2id, obj2id, Theta_zh, Psi_sz, smoothedProbs


    def getAllPossibleActions(self):
        return self.allActions
    
    def getUserId(self, uid):
        return uid

    def calculatingItemsFreq(self, smoothingParam, useLog = True):
        self.smoothedProbs = {}    
        freqs = {}            
        r = open(self.trace_fpath)
        counts = 0
        for line in r:
            cats = line.strip().split('\t')[self.true_mem_size+1:]
            for c in cats:
                if(c in freqs):
                    freqs[c] += 1
                else:
                    freqs[c] = 1                
                counts += 1
        for k in freqs:
            prob = float(freqs[k]+ smoothingParam) / float(counts + (len(freqs) * smoothingParam))
            if(useLog):
                self.smoothedProbs[k] = math.log10(prob)
            else:
                self.smoothedProbs[k] = prob
        

    def simulatedData(self, numberOfSequences, seqLenRange, outfile):
        self.calculateSequenceProb(self.smoothingParam, useLog = False)
        w = open(outfile, 'w')
        for i in range(numberOfSequences):
            num = random.randint(seqLenRange[0], seqLenRange[1])
            for j in num:
                action = np.random.choice(self.smoothedProbs.keys(), len(self.smoothedProbs), replace=True, p=self.smoothedProbs.values())
                w.write(action + ' ')
            w.write('\n')
        w.close()
            
        
    
    
    
    
