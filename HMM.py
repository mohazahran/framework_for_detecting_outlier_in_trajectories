'''
Created on Oct 3, 2017

@author: mohame11
'''
from DetectionTechnique import *
from MyEnums import *
import numpy as np
from hmmlearn import hmm
from sklearn.externals import joblib
from Metric import *

class HMM(DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)  
        self.type = SEQ_PROB.HMM
        self.allActions = []
        self.model = None
    
    
    
    def formOriginalSeq2(self, tests):
        origSeq = list(tests[0].actions)  
        if(len(tests) <= 1):
            return origSeq
        for i in range(1,len(tests)):
            a = tests[i].actions[-1]
            origSeq.append(a)    
        return origSeq
    
    def doFormating(self):
        PATH = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/pins_repins_win10.trace'
        FILE_TYPE = 'trace'
        ACTION_COUNT = 10
        ACTION_MAPPINGS_PATH = PATH+'_HMM_ACTION_MAPPINGS'
        
        actionDic = {}
        actionCntr = 0
        wr = open(ACTION_MAPPINGS_PATH, 'w')
        
        testDic = {}
        if(FILE_TYPE == 'trace'):
            r = open(PATH, 'r')   
            w = open(PATH+'_HMM', 'w') 
            for line in r:
                line = line.strip() 
                tmp = line.split()  
                
                user = tmp[ACTION_COUNT-1]
                seq = tmp[ACTION_COUNT:]
                
                t = TestSample()  
                t.user = user
                t.actions = list(seq)   
                
                if(user in testDic):
                    testDic[user].append(t)                                                    
                else:
                    testDic[user]=[t]
           
            
            for u in testDic:
                tests = testDic[u]
                originalSeq = self.formOriginalSeq2(tests)
                t = TestSample()  
                t.user = u
                t.actions = list(originalSeq)  
                testDic[u] = [t]
                
               
                st = ''
                for action in originalSeq:
                    if(action in actionDic):
                        st += str(actionDic[action])+'\t'
                    else:
                        actionDic[action] = actionCntr
                        actionCntr += 1
                        st += str(actionDic[action])+'\t'
                w.write(st+'\n')
                
                
        w.close()      
        for a in actionDic:
            wr.write(a+'\t'+str(actionDic[a])+'\n')
        wr.close()
    
    def trainHmm(self, trainPath):
        r = open(trainPath, 'r')
        training= []
        for line in r:
            t = [int(x) for x in (line.strip().split())]
            training.append(t)
        r.close()
        self.model = hmm.MultinomialHMM(n_components=10, n_iter=100)
        
        import warnings
        warnings.filterwarnings('ignore')
        try:
            print('Training HMM ...')
            self.model.fit(training)
        except:
            print('Error in training HMM')
        
        print('Dumping HMM model as pkl ...')
        joblib.dump(self.model, trainPath+'_MODEL.pkl')
        
    
    def loadModel(self):
        self.model = joblib.load(self.MODEL_PATH) 
        self.obj2id = {}
        r = open(self.actionMappingsPath, 'r')
        for line in r:
            parts = line.split()
            self.obj2id[parts[0]] = int(parts[1])
        r.close()
        
    
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
            
            #remove users not in training data
            if (self.DATA_HAS_USER_INFO == True):
                nonExistingUsers = set()
                rr = open(self.nonExistingUserFile, 'r')
                for line in rr:
                    nonExistingUsers.add(line.strip())
                rr.close()
                for us in nonExistingUsers:
                    testDic.pop(us, None)
        return testDic, len(testDic)
        
    def outlierDections(self, path, alphaList, metricList):
        testDic, _ = self.prepareTestSet()
        for user in testDic:
            for testSample in testDic[user]:
                goldMarkers = testSample.goldMarkers
                for i in range(len(goldMarkers)):
                    if (goldMarkers[i] == 'false'):
                        goldMarkers[i] = GOLDMARKER.FALSE
                    else:
                        goldMarkers[i] = GOLDMARKER.TRUE
        
        for m in metricList:
            if(m == METRIC.BAYESIAN):
                metric = Bayesian()
                w = open(path+'METRIC_BAYESIAN', 'w')
            elif(m == METRIC.FISHER):
                metric = Fisher()
                w = open(path+'METRIC_FISHER', 'w')
            for alpha in alphaList:
                cnt = 0
                for user in testDic:
                    cnt += 1
                    print(cnt,'/',len(testDic))
                    for testSample in testDic[user]:
                        decisionVector = []
                        actionIds = [self.obj2id[a] for a in testSample.actions]
                        prediction = self.model.predict(actionIds)
                        for i in range(len(actionIds)):
                            hiddenStat = prediction[i]
                            stateEmission = self.model._get_emissionprob()[hiddenStat]
                            emission = stateEmission[actionIds[i]]
                            if(emission <= alpha):
                                decisionVector.append(DECISION.OUTLIER)
                            else:
                                decisionVector.append(DECISION.NORMAL)
                        
                        metric.update(decisionVector, testSample.goldMarkers)
                
                
                metric.calculateStats() 
                w.write('alpha='+str(self.alpha))
                w.write(','+str(TECHNIQUE.MAJORITY_VOTING))       
                w.write(','+str(HYP.EMPIRICAL),)                                
                w.write(',TScountAdj='+str(False),':')
                w.write(metric.getSummary()+'\n')
            w.close()  
            
        
        
        
def expirements():
    '''
    def __init__(self, n_components=1, startprob=None, transmat=None,
                 startprob_prior=None, transmat_prior=None,
                 algorithm="viterbi", random_state=None,
                 n_iter=10, thresh=1e-2, params=string.ascii_letters,
                 init_params=string.ascii_letters):
        
        n_components : int
        Number of states in the model.
        
        n_symbols : int
        Number of possible symbols emitted by the model (in the observations).
    '''
    #model = hmm.MultinomialHMM(n_components=10, n_symbols= 315, n_iter=100)
    model = hmm.MultinomialHMM(n_components=10, n_iter=100)
    import random
    #X = [[chr(random.choice(range(97, 121))) for i in range(random.choice(range(1,10)))] for i in range(10)]  
    X1 = [[random.choice(range(10)) for i in range(random.choice(range(1,10)))] for i in range(10)]
    X2 = [[0,1,2,3],[4,5]]
    X3 = [[1,2,3],[0,4,5]]
    #X4=[[100,101],[103,102,104]]
    model.fit(X3)
    inp = X3[0]
    score = model.score(inp)
    prediction = model.predict(inp)
    thresh = 0.001
    for i in range(len(inp)):
        hiddenStat = prediction[i]
        stateEmission = model._get_emissionprob()[hiddenStat]
        emission = stateEmission[inp[i]]
        if(emission < thresh):
            print('outlier')
    
         
            
if __name__ == "__main__":
    #expirements()
    #h = HMM()
    #h.doFormating()
    #trainPath = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/pins_repins_win10.trace_HMM'
    #h.trainHmm(trainPath)
    
    myModel = HMM()
    path = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/HMM/'
    #myModel.SEQ_FILE_PATH = path+'sampleLikes'
    myModel.SEQ_FILE_PATH = path+'likes.trace'
    myModel.MODEL_PATH = path + 'pins_repins_win10.trace_HMM_MODEL.pkl'
    myModel.nonExistingUserFile = path + 'likes.trace_nonExistingUsers'
    myModel.actionMappingsPath = path + 'pins_repins_win10.trace_HMM_ACTION_MAPPINGS'
    myModel.useWindow = USE_WINDOW.FALSE
    myModel.groupActionsByUser = False
    myModel.DATA_HAS_USER_INFO = True
    myModel.VARIABLE_SIZED_DATA = False
    myModel.true_mem_size = 9
    alphaList = [1e-100, 1e-90, 1e-80, 1e-70, 1e-60, 1e-50, 1e-40, 1e-30, 1e-20, 1e-18, 1e-16, 1e-14, 1e-12, 1e-10, 5e-10, 1e-9, 5e-9, 1e-8, 5e-8, 1e-7, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1 ,0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 2.0]
    metricList = [METRIC.BAYESIAN, METRIC.FISHER]
    
    myModel.loadModel()
    myModel.outlierDections(path, alphaList, metricList)
    
    
    
    print('DONE!')
    
    
