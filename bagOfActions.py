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
from Metric import *

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
        print '>> Calculating probabilities ...'
        self.calculatingItemsFreq(self.smoothingParam, useLog = False)
        print '>> Number of actions: ', len(self.smoothedProbs)
        w = open(outfile, 'w')
        for i in range(numberOfSequences):
            num = random.randint(seqLenRange[0], seqLenRange[1])
            for j in range(num):
                action = np.random.choice(self.smoothedProbs.keys(), 1, replace=True, p=self.smoothedProbs.values())
                #print action[0], '##'
                w.write(action[0] + ' ')
            w.write('\n')
        w.close()
    
    
    def detectOutliers(self, testDic, metric): #probMassCutOff = 0.05 to correspond to 5% tail
        print '>> Calculating probabilities ...'
        self.calculatingItemsFreq(self.smoothingParam, useLog = False)
        print '>> Number of actions: ', len(self.smoothedProbs)
        #sorting ascendingly
        keySortedProbs = sorted(self.smoothedProbs, key=lambda k: (-self.smoothedProbs[k], k), reverse=True)
        outlierActions = set()
        accum = 0.0
        for key in keySortedProbs:
            accum += self.smoothedProbs
            outlierActions.add(key)
            if(accum > self.probMassCutOff):
                break
            
        
        for user in testDic:
            for testSample in testDic[user]:
                seq = testSample.actions
                goldMarkers = testSample.goldMarkers
                decisionVector = []
                for action in seq:
                    if(action in outlierActions):
                        decisionVector.append(DECISION.OUTLIER)
                    else:
                        decisionVector.append(DECISION.NORMAL)
                
                metric.update(decisionVector, goldMarkers)
        
        print metric.getSummary()
                        
            
        
    

def main():
    bag = BagOfActions()
    bag.trace_fpath = '/home/mohame11/pins_repins_fixedcat/pins_repins_win10.trace'
    bag.smoothingParam = 1.0
    bag.true_mem_size = 9
    bag.simulatedData(100000, [3,25], '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/simulatedData/simulatedData_bagOfActions')
    
    
    #####
    bag = BagOfActions()
    

    bag.true_mem_size = 9
    bag.trace_fpath = '/home/mohame11/pins_repins_fixedcat/pins_repins_win10.trace'
    bag.smoothingParam = 1.0
    bag.SEQ_FILE_PATH = '/home/mohame11/pins_repins_fixedcat/allLikes/likes.trace'
    bag.DATA_HAS_USER_INFO = True
    bag.VARIABLE_SIZED_DATA = False
    bag.RESULTS_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/allLikes/bagOfActions_noPvalue_win10/'
    bag.useWindow = False
    bag.probMassCutOff = 0.05
    
    testDic,testSetCount = bag.prepareTestSet()
    
    fisher = Fisher()
    
    bag.detectOutliers(testDic, fisher)
        
        
            
        
    
    
    
if __name__ == "__main__":
    main() 
