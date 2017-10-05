'''
Created on Oct 3, 2017

@author: mohame11
'''
from DetectionTechnique import *
from MyEnums import *
import numpy as np
from hmmlearn import hmm
from sklearn.externals import joblib

class HMM(DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)  
        self.type = SEQ_PROB.HMM
        self.allActions = []
        self.model = None
    
    

    def formOriginalSeq(self, tests):
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
                originalSeq = self.formOriginalSeq(tests)
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
        self.model = hmm.MultinomialHMM(n_components=2, n_iter=1)
        
        try:
            print('Training HMM ...')
            self.model.fit(training)
        except:
            print('Error in training HMM')
        
        print('Dumping HMM model as pkl ...')
        joblib.dump(self.model, trainPath+'_MODEL.pkl')
        
    
    def loadModel(self, modelPath):
        self.model = joblib.load(modelPath) 
        
        
        
        
        
        
        
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
    model = hmm.MultinomialHMM(n_components=3, n_iter=100)
    import random
    #X = [[chr(random.choice(range(97, 121))) for i in range(random.choice(range(1,10)))] for i in range(10)]  
    X1 = [[random.choice(range(10)) for i in range(random.choice(range(1,10)))] for i in range(10)]
    X2 = [[0,1,2,3],[4,5]]
    X3 = [[1,2,3],[0,4,5]]
    #X4=[[100,101],[103,102,104]]
    model.fit(X1)
    model.score(X1[0])
    
    #print(X)
            
if __name__ == "__main__":
    #expirements()
    h = HMM()
    #h.doFormating()
    trainPath = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/pins_repins_win10.trace_HMM'
    h.trainHmm(trainPath)
    print('DONE!')
    
    
