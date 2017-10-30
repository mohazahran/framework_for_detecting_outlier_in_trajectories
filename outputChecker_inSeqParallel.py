'''
Created on Oct 5, 2017

@author: mohame11
'''
import TestSample
from multiprocessing import Process, Queue
from MyEnums import *
import time
#from Tribeflowpp import *
from Tribeflow import *
import pandas as pd
import outlierDetection
import sys
sys.path.append('myCython')
import pyximport; pyximport.install()
import cythonOptimize

class OutputChecker():
    def __init__(self, seq_file_path, results_path, nonExistingUsers, modelType):
        self.RESULTS_PATH = results_path
        self.SEQ_FILE_PATH = seq_file_path
        self.modelType = modelType
        self.nonExistingUsers = nonExistingUsers
        self.model = None
        self.CORES = 20
    
    def getMissingTestSamples(self):
        if(self.modelType == SEQ_PROB.TRIBEFLOW):
            print('Tribeflow ...')
            self.model = TribeFlow()
            modelPath = '/u/scratch1/mohame11/pins_repins_fixedcat/pins_repins_win10_noop_NoLeaveOut.h5'
            store = pd.HDFStore(modelPath)
            self.model.true_mem_size = 9
            self.model.Theta_zh = store['Theta_zh'].values
            self.model.Psi_sz = store['Psi_sz'].values 
            self.model.hyper2id = dict(store['hyper2id'].values)
            self.model.obj2id = dict(store['source2id'].values)    
            self.model.trace_fpath = '/u/scratch1/mohame11/pins_repins_fixedcat/pins_repins_win10.trace'
            self.model.UNBIAS_CATS_WITH_FREQ = True
            self.model.STAT_FILE = '/u/scratch1/mohame11/pins_repins_fixedcat/Stats_win10'
            self.model.RESULTS_PATH = '/u/scratch1/mohame11/pins_repins_fixedcat/allLikes/pvalues_tr_leftovers_copa'
            
            self.model.DATA_HAS_USER_INFO = True
            self.model.VARIABLE_SIZED_DATA = False
            self.model.SEQ_FILE_PATH = self.SEQ_FILE_PATH
            if(self.model.UNBIAS_CATS_WITH_FREQ):
                print('>>> calculating statistics for unbiasing categories ...')
                self.model.calculatingItemsFreq(1.0)

        elif(self.modelType == SEQ_PROB.TRIBEFLOWPP):
            self.model = TribeFlowpp()
            self.model.true_mem_size = 9
            self.hyper2id = {}
            self.model.userMappingsPath = '/homes/mohame11/scratch/pins_repins_fixedcat/pins_repins_win10.trace_tribeflowpp_userMappings'
            r = open(self.model.userMappingsPath, 'r')
            for line in r:
                parts = line.split()
                self.model.hyper2id[parts[0]] = int(parts[1])
            r.close()
            
            
        self.model.SEQ_FILE_PATH =  self.SEQ_FILE_PATH
        self.model.useWindow = USE_WINDOW.FALSE
        self.model.groupActionsByUser = False
        
        
        nonExistingUsers = set()
        rr = open(self.nonExistingUsers, 'r')
        for line in rr:
            nonExistingUsers.add(line.strip())
        rr.close()
        
        ############################################
        print('Reading the output data ...')
        outputData = TestSample.parseAnalysisFiles('outlier_analysis_pvalues_', self.RESULTS_PATH)

        print('Reading test data ...')
        testData,_ = self.model.prepareTestSet() 
        #print(type(testData))
        
        
        for us in nonExistingUsers:
            testData.pop(us, None)
        
        outputUsers = sorted(outputData.keys())
        testUsers = sorted(testData.keys())
        
        print('outputUsers', len(outputUsers), 'testUsers', len(testUsers))
        leftovers = {}
        
        if(len(testUsers) == len(outputUsers)):
            print('equal !')
       
        elif(len(testUsers) > len(outputUsers)):
            print('The diff between the two sets:', len(testUsers) - len(outputUsers))
            for u in testData:
                if(u not in outputData):
                    leftovers[u] = testData[u]
            print('number of leftovers=',len(leftovers))
        else:
            print 'MORE OUTPUT than the DATA !!!!!!'
            
            
        #########################################################3
        
        #od = outlierDetection.OutlierDetection()
        #od.outlierDetection(leftovers, len(leftovers), '999', None, self.model)
        
        testSetCount = len(leftovers)
        
        elapsed_time = time.time() - start_time
        print 'Elapsed Time=', elapsed_time
        
        
  
  
  
  
def main():
    seq_file_path = '/u/scratch1/mohame11/pins_repins_fixedcat/allLikes/likes.trace'
    results_path = '/u/scratch1/mohame11/pins_repins_fixedcat/allLikes/pvalues_noWindow_log'
    nonExistingUsers = '/u/scratch1/mohame11/pins_repins_fixedcat/allLikes/likes.trace_nonExistingUsers'
    modelType = SEQ_PROB.TRIBEFLOW
    op = OutputChecker(seq_file_path, results_path, nonExistingUsers, modelType)
    op.getMissingTestSamples()
    
if __name__ == "__main__": 
    main()
    print('DONE!')

    
