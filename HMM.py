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
import random

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
    
    def doFormating(self, PATH):
        #PATH = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/pins_repins_win10.trace'
        #PATH = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/lastFm/lastfm_win10_trace'
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
        
    def getAllPossibleActions(self):
        return self.obj2id.keys()
    
    def getUserId(self, uid):
        return uid
    
    def getProbability(self, userId, newSeq):
        import warnings
        warnings.filterwarnings('ignore')
        actionIds = [self.obj2id[a] for a in newSeq]
        score = self.model.score(actionIds)
        return score
    
    def trainHmm(self, trainPath, hiddenStates):
        r = open(trainPath, 'r')
        training= []
        for line in r:
            t = [int(x) for x in (line.strip().split())]
            training.append(t)
        r.close()
        self.model = hmm.MultinomialHMM(n_components=hiddenStates, n_iter=100)
        
        import warnings
        warnings.filterwarnings('ignore')
        #try:
        print('Training HMM ...')
        self.model.fit(training)
        #except:
        #    print('Error in training HMM')
        
        print('Dumping HMM model as pkl ...')
        joblib.dump(self.model, trainPath+'_MODEL_'+str(hiddenStates)+'hiddenStates'+'.pkl')
        
    
    def loadModel(self):
        print('loading model with joblib.load')
        self.model = joblib.load(self.model_path) 
        print('done loading')
        self.obj2id = {}
        self.id2Obj = {}
        r = open(self.actionMappingsPath, 'r')
        for line in r:
            parts = line.split()
            self.obj2id[parts[0]] = int(parts[1])
            self.id2Obj[int(parts[1])] = parts[0]
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
                    seq = tmp[actionStartIndex:indx]
                    goldMarkers = tmp[indx+1:]
            #print(seq,goldMarkers)
            else:
                seq = tmp[actionStartIndex:self.true_mem_size+2]
                goldMarkers = tmp[self.true_mem_size+2:]

       
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
                w = open(path+'METRIC_BAYESIAN', 'w')
            elif(m == METRIC.FISHER):
                w = open(path+'METRIC_FISHER', 'w')
            elif(m == METRIC.REC_PREC_FSCORE):
                w = open(path+'METRIC_REC_PREC_FSCORE', 'w')
            
            
            predictionsBuffer = {}
            
            for alpha in alphaList:
                if(m == METRIC.BAYESIAN):
                    metric = Bayesian()
                elif(m == METRIC.FISHER):
                    metric = Fisher()
                elif(m == METRIC.REC_PREC_FSCORE):
                    metric = rpf()
                
                cnt = 0
                print (alpha)
                for user in testDic:
                    cnt += 1
                    if(cnt % 10 == 0):
                        print(cnt,'/',len(testDic))
                    for testSample in testDic[user]:
                        decisionVector = []
                        actionIds = [self.obj2id[a] for a in testSample.actions]
                        #print(testSample.actions)
                        key = str(user)+':'+str(actionIds)
                        if(key in predictionsBuffer):
                            prediction = predictionsBuffer[key]
                        else:
                            prediction = self.model.predict(actionIds)
                            predictionsBuffer[key] = prediction
                            
                        for i in range(len(actionIds)):
                            hiddenStat = prediction[i]
                            stateEmission = self.model._get_emissionprob()[hiddenStat]
                            emission = stateEmission[actionIds[i]]
                            if(emission <= alpha):
                                decisionVector.append(DECISION.OUTLIER)
                            else:
                                decisionVector.append(DECISION.NORMAL)
                        
                        metric.update(decisionVector, testSample.goldMarkers)
                
                print(metric.getSummary())
                metric.calculateStats() 
                w.write('alpha='+str(alpha))
                w.write(','+str(TECHNIQUE.MAJORITY_VOTING))       
                w.write(','+str(HYP.EMPIRICAL),)                                
                w.write(',TScountAdj='+str(False)+':')
                w.write(metric.getSummary()+'\n')
                w.flush()
            w.close()  
            
    
    def simulatedSeq(self, size):
        currState = random.choice(list(range(self.model.n_components)))
        seq = []
        for i in range(size):
            stateEmission = self.model._get_emissionprob()[currState]
            actionId = np.random.choice(list(range(self.model.n_symbols)), 1, replace =True, p=stateEmission)[0]
            action = self.id2Obj[actionId]
            seq.append(action)
            
            trans = self.model._get_transmat()[currState]
            currState = np.random.choice(list(range(self.model.n_components)), 1, replace =True, p=trans)[0]
        return seq
            
            
        
    def simulateData(self, mu, sigma, sampleCount, filepath):
        w = open(filepath, 'w')
        sizes = np.random.normal(mu, sigma, sampleCount)
        cnt = 0
        for i in sizes:
            if(i<=8):
                continue
            seq = self.simulatedSeq(int(i))
            if(len(seq) <= 1):
                print(seq)
            w.write(' '.join(seq)+'\n')
            if(cnt % 10 == 0):
                w.flush()
                print(cnt)
            cnt += 1
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
    
         

def trainTheHMM():
    h = HMM()
    print('Formating ...')
    #h.doFormating()
    #trainPath = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/pins_repins_win10.trace_HMM'
    #trainPath = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/lastFm/lastfm_win10_trace_HMM'
    trainPath = '/u/scratch1/mohame11/lastfm_WWW/lastfm_win10_trace_top5000'

    h.doFormating(trainPath)
    print('Training HMM ...')
    
    hiddenStates = 30
    h.trainHmm(trainPath+'_HMM', hiddenStates)
    
def doTheOutlierDetection():
    myModel = HMM()
    #path = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/HMM/'
    path = '/u/scratch1/mohame11/lastfm_WWW/'
    #myModel.SEQ_FILE_PATH = path+'sampleLikes'
    #myModel.SEQ_FILE_PATH = path+'likes.trace'
    myModel.SEQ_FILE_PATH = path+'hmm30_www_simData'
    #myModel.MODEL_PATH = path + 'pins_repins_win10.trace_HMM_MODEL.pkl'
    myModel.model_path = path + 'lastfm_win10_trace_top5000_HMM_MODEL_30hiddenStates.pkl'
    #myModel.nonExistingUserFile = path + 'likes.trace_nonExistingUsers'
    myModel.nonExistingUserFile = path+'lastfm_win10_trace_top5000_allClusters_HMM_simData_withUsers_injected_0.1_nonExistingUsers'
    #myModel.actionMappingsPath = path + 'pins_repins_win10.trace_HMM_ACTION_MAPPINGS'
    myModel.actionMappingsPath = path + 'lastfm_win10_trace_top5000_HMM_ACTION_MAPPINGS'
    myModel.useWindow = USE_WINDOW.FALSE
    myModel.groupActionsByUser = True
    myModel.DATA_HAS_USER_INFO = False
    myModel.VARIABLE_SIZED_DATA = True
    myModel.true_mem_size = 9
    alphaList = [1e-100, 1e-90, 1e-80, 1e-70, 1e-60, 1e-50, 1e-40, 1e-30, 1e-20, 1e-18, 1e-16, 1e-14, 1e-12, 1e-10, 5e-10, 1e-9, 5e-9, 1e-8, 5e-8, 1e-7, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1 ,0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 0.995, 0.9975, 1.0, 2.0]
    #metricList = [METRIC.BAYESIAN, METRIC.FISHER]
    metricList = [METRIC.REC_PREC_FSCORE]
    
    myModel.loadModel()
    myModel.outlierDections(path, alphaList, metricList)
    
def doDataGeneration():
    #path = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/HMM/'
    path = '/u/scratch1/mohame11/lastfm_WWW/'
    h = HMM()
    #h.model_path = path + 'pins_repins_win10.trace_HMM_MODEL.pkl'
    #h.model_path = path + 'lastfm_win10_trace_top5000_HMM_MODEL.pkl'
    h.model_path = path + 'lastfm_win10_trace_top5000_HMM_MODEL_30hiddenStates.pkl'
    #h.actionMappingsPath = path + 'pins_repins_win10.trace_HMM_ACTION_MAPPINGS'
    h.actionMappingsPath = path + 'lastfm_win10_trace_top5000_HMM_ACTION_MAPPINGS'
    
    h.loadModel()
    
    #h.simulateData(19, 9, 5000,path+'simData')
    #h.simulateData(9912, 1000, 5000, path+'HMM_simData') #Avg. Trace Length: 9912
    h.simulateData(20, 0, 7000, path+'hmm30_www_simData') #Avg. Trace Length: 9912
    
    
if __name__ == "__main__":
    #expirements()
    #doDataGeneration()
    doTheOutlierDetection()
    #trainTheHMM()
    
    
    
    
    
    
    
    print('DONE!')
    
    
