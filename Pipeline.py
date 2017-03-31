'''
Created on Mar 25, 2017

@author: mohame11
'''
from outlierDetection import *
from injectOutliers import *
from thresholdSelection import *



def selectThresholdPipeline():
    #######################
    #config the injections
    ####################### 
    inj = InjectOutliers()
    #common
    inj.INPUT_FILE = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/simulatedData/pins_repins_bbtt3_simulatedData_fixed_3'
    inj.OUTPUT_FILE = ''
    inj.METHOD = SEQ_PROB.RNNLM
    inj.isTraceFile = False #The input data file is a tracefile: has the same format as tribeflow's training data
    #maxInjections = 1
    inj.injectionRatio = 0.1
    inj.samplesCount = 10000
    #tribeflow
    inj.MODEL_PATH = '/home/mohame11/pins_repins_fixedcat/pins_repins_win10_noop_NoLeaveOut.h5'
    
    #ngram
    inj.ALL_ACTION_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/pins_repins_win4.trace_forLM_RNN_train_ALL_ACTIONS'
   
    print '>> Injecting outliers ...' 
    inj.inject() 
    ############################
    #config outlier detection
    ############################
    
    detect = OutlierDetection()
    #COMMON
    detect.CORES = 40
    detect.PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/'
    detect.RESULTS_PATH = detect.PATH+'/simulatedData/pipeline_rnnlm3'
    detect.SEQ_FILE_PATH = inj.OUTPUT_FILE
    detect.MODEL_PATH = detect.PATH+'pins_repins_bbtt3.RNNLMmodel'
    detect.seq_prob = SEQ_PROB.RNNLM
    detect.useWindow = USE_WINDOW.FALSE
    
    #TRIBEFLOW
    detect.TRACE_PATH = detect.PATH+'pins_repins_win10.trace'
    detect.STAT_FILE = detect.PATH+'Stats_win10'
    detect.UNBIAS_CATS_WITH_FREQ = True
    detect.smoothingParam = 1.0   #smoothing parameter for unbiasing item counts.
    
    #NGRM/RNNLM
    detect.HISTORY_SIZE = 3
    detect.DATA_HAS_USER_INFO = False #has no effect on tribeflow
    detect.VARIABLE_SIZED_DATA = True #has no effect on tribeflow
    detect.ALL_ACTIONS_PATH = inj.ALL_ACTION_PATH
    
    print '>>> Detecting outliers ...'
    detect.distributeOutlierDetection()
    
    
    ############################
    #config threshold selection
    ############################
    select = ThresholdSelection()
    select.INPUT_PATH = detect.RESULTS_PATH+'/'
    select.FILE_NAME = 'outlier_analysis_pvalues_'
    select.NUM_ITERATIONS = 100
    select.BATCH_SIZE = 100 # -1 means use all data
    
    select.alphaList = [1e-20, 1e-15, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0]
    select.pvalueList = [PVALUE.WITHOUT_RANKING, PVALUE.WITH_RANKING]
    
    select.metric = METRIC.REC_PREC_FSCORE
    select.tech = TECHNIQUE.MAJORITY_VOTING
    select.hyp = HYP.EMPIRICAL
    select.tadj = False
    
    print '>>> Selecting threshold ...'
    print inj.INPUT_FILE
    print 'injectionRatio=', inj.injectionRatio
    print 'injectedSamplesCount=', inj.samplesCount
    select.selectThreshold()   
    





















if __name__ == "__main__":
    selectThresholdPipeline()    
    print('DONE!')
