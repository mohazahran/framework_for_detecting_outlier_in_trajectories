'''
Created on Feb 16, 2017

@author: mohame11
'''
from DetectionTechnique import *
import MyEnums

class RNNLM (DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)  
        self.type = SEQ_PROB.RNNLM
        self.allActions = []
        self.model = None
       
        
    def loadModel(self):
        '''
        self.model = rnnlm.CRnnLM()
        lmda = 0.75
        regularization = 0.0000001
        dynamic = 0
        rand_seed = 1
        self.model.setLambda(lmda)
        self.model.setRegularization(regularization)
        self.model.setDynamic(dynamic)
        self.model.setRnnLMFile(self.model_path)
        self.model.setRandSeed(rand_seed)
        '''
        r = open(self.ALL_ACTIONS_PATH, 'r')
        for line in r:
           line = line.strip()
           if(len(line)>0):
                self.allActions.append(line)
        r.close()

        
    def getProbability(self, userId, newSeq, coreId):
        #test_file = self.RESULTS_PATH+'tmp'+str(coreId)
        test_file = '/Users/mohame11/Desktop/'+'tmp'+str(coreId)
        w = open(test_file,'w')
        strSeq = ' '.join(newSeq)
        w.write(strSeq)
        w.close()
        
        #self.model.setTestFile(test_file)
        #prob = self.model.testNet() 
        py2output = subprocess.check_output(['python', self.RNNLM_PYTHON_PATH+'main.py', '-rnnlm', self.model_path, '-test', test_file])
        logProb = py2output.split('log probability:')[-1].split('PPL')[0].strip()
        return logProb
        #prob = 10**float(logProb)
        #return prob
        
        
        
        
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
            user += 1
            if (self.DATA_HAS_USER_INFO == True):
                user = tmp[0]   
                actionStartIndex = 1
            
            if(self.VARIABLE_SIZED_DATA == True):
                seq = tmp[actionStartIndex:]
                goldMarkers = ['false']*len(seq)
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