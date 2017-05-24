'''
Created on Oct 3, 2016

@author: zahran
'''
import pandas as pd
from MyEnums import *
import random

class InjectOutliers:
    def __init__(self):
        #common
        self.INPUT_FILE = '/scratch/snyder/m/mohame11/lastFm/simulatedData/simData_perUser_2_forInjection'
        self.OUTPUT_FILE = ''
        self.METHOD = SEQ_PROB.TRIBEFLOW
        self.isTraceFile = False #The input data file is a tracefile: has the same format as tribeflow's training data
        #maxInjections = 1
        self.injectionRatio = 0.1
        self.samplesCount = 1962
        
        #tribeflow
        self.MODEL_PATH = '/scratch/snyder/m/mohame11/lastFm/lastfm_win10_noob.h5'
        
        #ngram
        self.ALL_ACTION_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/pins_repins_win4.trace_forLM_RNN_train_ALL_ACTIONS'
    
    def inject(self):
        if(self.METHOD == SEQ_PROB.TRIBEFLOW):
            store = pd.HDFStore(self.MODEL_PATH)     
            obj2id = dict(store['source2id'].values)
            allPossibleActions = obj2id.keys()
            Dts = store['Dts']
            winSize = Dts.shape[1]    
        else:
            alla = open(self.ALL_ACTION_PATH,'r')
            allPossibleActions = []
            for line in alla:
                allPossibleActions.append(line.strip())
            alla.close()
              
    
        r = open(self.INPUT_FILE, 'r')  
        inputSequences = r.readlines()
        inputSequences = random.sample(inputSequences, self.samplesCount)
        r.close()
        
        if(self.OUTPUT_FILE == ''):
            self.OUTPUT_FILE = self.INPUT_FILE+'_injected_'+str(self.injectionRatio)
        w = open(self.OUTPUT_FILE, 'w')
        
        allCategories = set(allPossibleActions)
        for line in inputSequences:
            allPossibleActions = set(allCategories)
            line = line.strip()
            parts = line.split()
            user = None
            if(self.METHOD == SEQ_PROB.TRIBEFLOW):
                if self.isTraceFile == True:
                    times = parts[:winSize]
                    user = parts[winSize]
                    cats = parts[winSize+1:]
                else:
                    user = parts[0]
                    cats = parts[1:winSize+2]
            else:
                cats = parts	
            for c in cats:
                allPossibleActions.discard(c)
                
            markers = ['false']*(len(cats))
            
            maxInjections = int(len(cats) * self.injectionRatio)

            injectedIdx = random.sample(list(range(len(cats))), maxInjections)
            
            for idx in injectedIdx:
                originalCat = cats[idx]                                        
                if(idx == 0):                    
                    while True:
                        randCat = random.sample(allPossibleActions, 1)[0]                        
                        ok = (randCat != originalCat) and (randCat != cats[idx+1])
                        if(ok):
                            break                            
                elif (idx == len(cats)-1):
                    while True:
                        randCat = random.sample(allPossibleActions, 1)[0]                        
                        ok = (randCat != originalCat) and (randCat != cats[-2])
                        if(ok):
                            break
                else:
                    while True:
                        randCat = random.sample(allPossibleActions, 1)[0]                        
                        ok = (randCat != originalCat) and (randCat != cats[idx+1]) and (randCat != cats[idx-1])
                        if(ok):
                            break
                        
                cats[idx]= randCat
                markers[idx] = 'true'

            if(user != None):
                w.write(user+'\t')
            for c in cats:
                w.write(c+'\t')
                
                
            if(not self.METHOD == SEQ_PROB.TRIBEFLOW):
                w.write('###\t')
            for m in markers:
                w.write(m+'\t')
            w.write('\n')
            
        w.close()
        if(self.METHOD == SEQ_PROB.TRIBEFLOW):
            store.close()
        
                                        
                



def work():
    inj = InjectOutliers()
    inj.inject()
    
if __name__ == "__main__":
    work()
    print('DONE !')

