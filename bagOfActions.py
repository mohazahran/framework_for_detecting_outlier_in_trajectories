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
            cats = line.strip().split()[self.true_mem_size+1:]
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
        ww = open(self.trace_fpath+'_actionsProbs', 'w')
        for a in self.smoothedProbs:
            ww.write(str(a)+','+str(self.smoothedProbs[a])+'\n')
        ww.close()
           

    def simulateData(self, numberOfSequences, seqLenRange, outfile):
        print '>> Calculating probabilities ...'
        self.calculatingItemsFreq(self.smoothingParam, useLog = False)
        print '>> Number of actions: ', len(self.smoothedProbs)
        actions = []
        probs = []
        for a in self.smoothedProbs:
            actions.append(a)
            probs.append(self.smoothedProbs[a])
        
        w = open(outfile, 'w')
        for i in range(numberOfSequences):
            num = random.randint(seqLenRange[0], seqLenRange[1])
            simActions = np.random.choice(actions, num, replace=True, p=probs)
            w.write(' '.join(simActions) + '\n')
        w.close()
    
    
    def detectOutliers(self, testDic): #probMassCutOff = 0.05 to correspond to 5% tail
        #print '#actions', len(self.smoothedProbs)   
        #sorting ascendingly
        keySortedProbs = sorted(self.smoothedProbs, key=lambda k: (-self.smoothedProbs[k], k), reverse=True)
        
        for probMassCutOff in self.probMassCutOff:
            if(self.metricType == METRIC.FISHER):
                metric = Fisher()
            elif(self.metricType == METRIC.REC_PREC_FSCORE):
                metric = rpf()
	    elif(self.metricType == METRIC.CHI_SQUARE):
	        metric = Chisq()
            elif(self.metricType == METRIC.BAYESIAN):
                metric = Bayesian()
            self.probMassCutOff = probMassCutOff
            outlierActions = set()
            #accum = 0.0
            for key in keySortedProbs:
                #if(accum >= self.probMassCutOff):
                #    break
                #accum += self.smoothedProbs[key]
                #outlierActions.add(key)
                if(self.smoothedProbs[key] < self.probMassCutOff):
		    outlierActions.add(key)
            
            #outlierCountAllowed = 3
            #where = 0
            #print 'accumalted_pdf=', accum
            #print 'outlier actions count = ', len(outlierActions)
            for user in testDic:
                for testSample in testDic[user]:
                    seq = testSample.actions
                    goldMarkers = list(testSample.goldMarkers)
                    decisionVector = []
                    for action in seq:
                        if(action in outlierActions):
                            #print '>>>>>> asd'
                            decisionVector.append(DECISION.OUTLIER)
                        else:
                            decisionVector.append(DECISION.NORMAL)
                    #print (len(decisionVector), len(goldMarkers))

                    metric.update(decisionVector, goldMarkers)
                    #c = goldMarkers.count(GOLDMARKER.TRUE)
                    #outlierCountAllowed -= c
                    #if(outlierCountAllowed <= 0):   
                        #while GOLDMARKER.TRUE in goldMarkers:
                            #idx = goldMarkers.index(GOLDMARKER.TRUE)
                            #print 'idx=', idx
                            #del goldMarkers[idx]
                            #del decisionVector[idx]
                    #print len(decisionVector), len(goldMarkers)
                    #metric.update(decisionVector, goldMarkers)
            
            metric.calculateStats() 
            print 'alpha='+str(self.probMassCutOff),
            print ','+str(TECHNIQUE.MAJORITY_VOTING),       
            print ','+str(HYP.EMPIRICAL),                                
            print ',TScountAdj='+str(False),':',
            print metric.getSummary()
            
        return metric.getSummary()
            
    
    def getBoundingAlphas(self):
        r = open(self.RESULTS_PATH, 'r')
        self.upperAlpha = None
        self.lowerAlpha = None
        for line in r:
            parts = line.split(':')
            params = parts[0].split(',')
            results = parts[-1].replace(')','').replace('(','').split(', ')
            config = ','.join(params[1:])
            alpha = float(params[0].split('=')[-1])
            print alpha
            
            tp=float(results[0].split('=')[-1])
            fp=float(results[1].split('=')[-1])
            fn=float(results[2].split('=')[-1])
            tn=float(results[3].split('=')[-1])
            res = (tp+tn)/(tp+tn+fp+fn)
            #print res
          
                
            if(abs(res - self.requiredLevel) <= self.epsilon):
                return alpha,res
            
            if(res  < self.requiredLevel):
                self.lowerAlpha = [alpha,res]
                
            if(res  > self.requiredLevel):
                self.upperAlpha = [alpha,res]
            
            if(self.lowerAlpha != None and self.upperAlpha != None):
                return        
        

def performOutLierDetection():
    bag = BagOfActions()
    bag.true_mem_size = 9
    #bag.trace_fpath = '/u/scratch1/mohame11/pins_repins_fixedcat/pins_repins_win10.trace'
    bag.trace_fpath = '/u/scratch1/mohame11/lastFm/lastfm_win10_trace'
    #bag.trace_fpath = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/pins_repins_win4.trace'
    bag.smoothingParam = 1.0
    #bag.SEQ_FILE_PATH = '/Users/mohame11/Documents/newResults_lastfm/simData_perUser_2_forInjection_injected_0.1'
    bag.SEQ_FILE_PATH = '/u/scratch1/mohame11/lastFm/simulatedData/bag9_simDataForInj_u982_perUser20_injected_0.1'
    #bag.SEQ_FILE_PATH = '/u/scratch1/mohame11/pins_repins_fixedcat/allLikes/likes.trace'
    #bag.SEQ_FILE_PATH = '/scratch/snyder/m/mohame11/lastFm/simulatedData/simulatedData_bagOfActions'
    #bag.SEQ_FILE_PATH =  '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/simulatedData/simulatedData_bagOfActions'
    #bag.SEQ_FILE_PATH = '/home/mohame11/pins_repins_fixedcat/allLikes/likes.trace'
    #bag.SEQ_FILE_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/allLikes/likes_withFriendship_win4.trace'
    bag.DATA_HAS_USER_INFO = False
    bag.VARIABLE_SIZED_DATA = True
    #bag.RESULTS_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/allLikes/bagOfActions_noPvalue_win10/'
    bag.useWindow = USE_WINDOW.FALSE
    bag.groupActionsByUser = True
    bag.probMassCutOff = []
    #bag.probMassCutOff = [1e-20, 1e-15, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 2.0]
    bag.probMassCutOff = [1e-100, 1e-90, 1e-80, 1e-70, 1e-60, 1e-50, 1e-40, 1e-30, 1e-20, 1e-18, 1e-16, 1e-14, 1e-12, 1e-10, 5e-10, 1e-9, 5e-9, 1e-8, 5e-8, 1e-7, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1 ,0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 2.0]
    #bag.probMassCutOff.append(0.048671875)
    
    #bag.metricType = METRIC.BAYESIAN
    #bag.metricType = METRIC.FISHER
    bag.metricType = METRIC.REC_PREC_FSCORE
    testDic,testSetCount = bag.prepareTestSet()
    #NON_EXISTING_USERS_PATH = '/u/scratch1//mohame11/pins_repins_fixedcat/allLikes/likes.trace_nonExistingUsers'
    #NON_EXISTING_USERS_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/allLikes/likes_withFriendship_win4.trace_nonExistingUsers'
    #NON_EXISTING_USERS_PATH = '/scratch/snyder/m/mohame11/lastFm/simulatedData/simData_perUser_2_forInjection_injected_0.1_nonExistingUsers'
    '''
    nonExistingUsers = set()
    rr = open(NON_EXISTING_USERS_PATH, 'r')
    for line in rr:
        nonExistingUsers.add(line.strip())
    rr.close()
    badUserCnt = 0
    for us in nonExistingUsers:
        tmp = testDic.pop(us, None)
        if (tmp != None):
                badUserCnt += 1
    print 'badUserCnt=',badUserCnt
    '''
    #print '#users', len(testDic)
    for user in testDic:
        #print user,'#sequences',len(testDic[user])
        for testSample in testDic[user]:
            goldMarkers = testSample.goldMarkers
            #print '#golds', len(goldMarkers), '#actions', len(testSample.actions)
            for i in range(len(goldMarkers)):
                if (goldMarkers[i] == 'false'):
                    goldMarkers[i] = GOLDMARKER.FALSE
                else:
                    goldMarkers[i] = GOLDMARKER.TRUE
                    
    print '>> Calculating probabilities ...'
    bag.calculatingItemsFreq(bag.smoothingParam, useLog = False)
    print '>> Number of actions: ', len(bag.smoothedProbs)
    bag.detectOutliers(testDic)


def performDataSimulation():
    bag = BagOfActions()
    #bag.trace_fpath = '/u/scratch1/mohame11/pins_repins_fixedcat/pins_repins_win10.trace'
    bag.trace_fpath = '/u/scratch1/mohame11/lastFm/lastfm_win10_trace'
    #bag.trace_fpath = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/pins_repins_win4.trace'
    bag.smoothingParam = 1.0
    bag.true_mem_size = 9
    #bag.simulateData(10000, [10,10], '/scratch/snyder/m/mohame11/lastFm/simulatedData/simulatedData_bagOfActions2')
    #bag.simulateData(10000, [9,19], '/u/scratch1/mohame11/pins_repins_fixedcat/simulatedData/bag9_simData') #simulateData(numberOfSequences, seqLenRange, outfile):
    bag.simulateData(982, [20,20], '/u/scratch1/mohame11/lastFm/simulatedData/bag9_simDataForInj_u982_perUser20') #simulateData(numberOfSequences, seqLenRange, outfile):
  
    '''
    print '>> Calculating probabilities ...'
    bag.calculatingItemsFreq(bag.smoothingParam, useLog = False)
    print '>> Number of actions: ', len(bag.smoothedProbs)
    w = open(bag.trace_fpath+'_ALL_ACTIONS', 'w')
    for a in bag.smoothedProbs:
        w.write(a+'\n')
    w.close()
    '''
    



def performThresholdSelection():
    bag = BagOfActions()
    bag.true_mem_size = 3
    bag.trace_fpath = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/pins_repins_win4.trace'
    bag.smoothingParam = 1.0
    bag.SEQ_FILE_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/simulatedData/simulatedData_bagOfActions'
    #bag.SEQ_FILE_PATH = '/scratch/snyder/m/mohame11/lastFm/simulatedData/simulatedData_bagOfActions'
    bag.DATA_HAS_USER_INFO = False
    bag.VARIABLE_SIZED_DATA = True
    bag.RESULTS_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/simulatedData/standAlone_bagOfActions_simulatedData'
    bag.useWindow = False
    bag.metricType = METRIC.REC_PREC_FSCORE
    bag.requiredLevel = 0.95
    bag.epsilon = 1e-4

    print '>> Calculating probabilities ...'
    bag.calculatingItemsFreq(bag.smoothingParam, useLog = False)
    print '>> Number of actions: ', len(bag.smoothedProbs)

    
    testDic,testSetCount = bag.prepareTestSet()
    for user in testDic:
        for testSample in testDic[user]:
            goldMarkers = testSample.goldMarkers
            for i in range(len(goldMarkers)):
                if (goldMarkers[i] == 'false'):
                    goldMarkers[i] = GOLDMARKER.FALSE
                else:
                    goldMarkers[i] = GOLDMARKER.TRUE
                    
    
    ret = bag.getBoundingAlphas()
    print 'upperAlpha=', bag.upperAlpha, ' lowerAlpha=', bag.lowerAlpha
    if(ret != None):
        print 'Alpha=',ret[0],' metric=',ret[1]
        return
    
    
    
    diff = bag.epsilon + 1
    print 'starting'
    while(diff > bag.epsilon):
        currAlpha = (bag.lowerAlpha[0] + bag.upperAlpha[0])/2
        #debugPath = self.INPUT_PATH+'DEBUG_'+str(pv)+'_'+str(alpha)
        bag.probMassCutOff = [currAlpha]
        summary = bag.detectOutliers(testDic)
        results = summary.replace(')','').replace('(','').split(', ')
        tp=float(results[0].split('=')[-1])
        fp=float(results[1].split('=')[-1])
        fn=float(results[2].split('=')[-1])
        tn=float(results[3].split('=')[-1])
        res = (tp+tn)/(tp+tn+fp+fn)
        if(abs(res-bag.requiredLevel) <= bag.epsilon):
            return currAlpha, res
        
        if(bag.requiredLevel > res):
            bag.lowerAlpha = [currAlpha, res]
        elif(bag.requiredLevel < res):
            bag.upperAlpha = [currAlpha, res]
        
        print 'currentAlpha=', currAlpha, ' metric=', res
    
      


def main():
    performDataSimulation()
    #performOutLierDetection()
    #performThresholdSelection()
        
        
            
        
    
    
    
if __name__ == "__main__":
    #print('In bag of actions')
    main() 
