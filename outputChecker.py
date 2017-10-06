'''
Created on Oct 5, 2017

@author: mohame11
'''
import TestSample
from MyEnums import *

class OutputChecker():
    def __init__(self, seq_file_path, results_path, nonExistingUsers, modelType):
        self.RESULTS_PATH = results_path
        self.SEQ_FILE_PATH = seq_file_path
        self.modelType = modelType
        self.nonExistingUsers = nonExistingUsers
        self.model = None
    
    def getMissingTestSamples(self):
        if(self.modelType == SEQ_PROB.TRIBEFLOW):
            self.model = Tribeflow()
            
        self.model.SEQ_FILE_PATH =  self.SEQ_FILE_PATH
        self.model.useWindow == USE_WINDOW.FALSE
        
        nonExistingUsers = {}
        nonExistingUsers = set()
        rr = open(self.nonExistingUsers, 'r')
        for line in rr:
            nonExistingUsers.add(line.strip())
        rr.close()
        
        outputData = TestSample.parseAnalysisFiles('outlier_analysis_pvalues_', self.RESULTS_PATH)
        testData = self.model.prepareTestSet() 
        
        
        for us in nonExistingUsers:
            testData.pop(us, None)
        
        outputUsers = sorted(outputData.keys())
        testUsers = sorted(testData.keys())
        
        print('outputUsers', len(outputUsers), 'testUsers', len(testUsers))
        
        
  
  
  
  
def main():
    seq_file_path = '/homes/mohame11/scratch/pins_repins_fixedcat/allLikes/likes.trace'
    results_path = '/homes/mohame11/scratch/pins_repins_fixedcat/allLikes/pvalues_noWindow_log_copy/'
    nonExistingUsers = '/homes/mohame11/scratch/pins_repins_fixedcat/allLikes/likes.trace_nonExistingUsers'
    modelType = SEQ_PROB.TRIBEFLOW
    op = OutputChecker(seq_file_path, results_path, nonExistingUsers, modelType)
    op.getMissingTestSamples()
    
if __name__ == "__main__": 
    main()

    