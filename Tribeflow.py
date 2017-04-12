'''
Created on Feb 16, 2017

@author: mohame11
'''
from DetectionTechnique import *
import sys
import math
import numpy as np
import os.path
sys.path.append('Cython/')
import cythonOptimize
import MyEnums

class TribeFlow (DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)
        self.type = SEQ_PROB.TRIBEFLOW
        self.hyper2id = None
        self.obj2id = None
        self.Theta_zh = None
        self.Psi_sz = None
        self.smoothedProbs = None
        self.trace_fpath = None
        self.STAT_FILE = None
        self.UNBIAS_CATS_WITH_FREQ = None
        self.store = None
    
    def evaluate(self, userId, history, targetObjId, Theta_zh, Psi_sz, env):        
        mem_factor = 1.0    
        candidateProb = 0.0                    
        for j in xrange(len(history)):#for all B
            #i.e. multiply all psi[objid1,z]*psi[objid2,z]*..psi[objidB,z]
            mem_factor *= Psi_sz[history[j], env] # Psi[objId, env z]            
        #mem_factor *= 1.0 / (1 - Psi_sz[history[len(history)-1], env])# 1-Psi_sz[mem[B-1],z] == 1-psi_sz[objIdB,z]       
        candidateProb += mem_factor * Psi_sz[targetObjId, env] * Theta_zh[env, userId]                                              
        return candidateProb
         
    def calculateSequenceProb(self, theSequence, true_mem_size, userId, obj2id, Theta_zh, Psi_sz):                     
        seqProb = 0.0
        window = min(true_mem_size, len(theSequence))
        for z in xrange(Psi_sz.shape[1]): #for envs
            seqProbZ = 1.0        
            for targetObjIdx in range(0,len(theSequence)): #targetObjIdx=0 cannot be predicted we have to skip it
                if(targetObjIdx == 0):                
                    d = theSequence[targetObjIdx]
                    #all_in = h in hyper2id and d in obj2id
                    #if(all_in):
                    targetObjId = obj2id[d]
                    prior = Psi_sz[targetObjId, z]
                    seqProbZ *= prior
                else:                                                                            
                    d = theSequence[targetObjIdx]                 
                    sources = theSequence[max(0,targetObjIdx-window): targetObjIdx] # look back 'window' actions.                             
                    #all_in = h in hyper2id and d in obj2id
                    #for s in sources:
                    #    all_in = all_in and s in obj2id                
                    #if all_in:
                    targetObjId = obj2id[d]
                    #userId = hyper2id[h]
                    history = [obj2id[s] for s in sources]                                
                    candProb = self.evaluate(userId, history, targetObjId, Theta_zh, Psi_sz, z) #(int[:, ::1] HOs, double[:, ::1] Theta_zh, double[:, ::1] Psi_sz, int[::1] count_z, int env):
                    #candProb = 0.001                    
                    seqProbZ *= candProb
                    #seqProb += math.log(predTargetProb)
            seqProb += seqProbZ
            #print(seqProb, math.log(seqProb))
        return seqProb   
    
    def createTestingSeqFile(self, store):
        from_ = store['from_'][0][0]
        to = store['to'][0][0]
        trace_fpath = store['trace_fpath']
        Dts = store['Dts']
        winSize = Dts.shape[1]
        tpath = '/home/zahran/Desktop/tribeFlow/zahranData/pinterest/test_traceFile_win5'
        w = open(tpath,'w')
        r = open(trace_fpath[0][0],'r')
        
        cnt = 0
        for line in r:
            if(cnt > to):
                p = line.strip().split('\t')
                usr = p[winSize]
                sq = p[winSize+1:]
                w.write(str(usr)+'\t')
                for s in sq:
                    w.write(s+'\t')
                w.write('\n')
            cnt += 1
        w.close()
        r.close()
        return tpath         
        
    def calculatingItemsFreq(self, smoothingParam):
        self.smoothedProbs = {}    
        if os.path.isfile(self.STAT_FILE):
            r = open(self.STAT_FILE, 'r')
            for line in r:
                parts = line.strip().split('\t')               
                #print(parts, parts[1]) 
                #self.smoothedProbs[parts[0]] = math.log10(float(parts[1]))                    
                self.smoothedProbs[parts[0]] = float(parts[1]) 
            
        
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
            self.smoothedProbs[k] = math.log10(prob)
        
        w = open(self.STAT_FILE, 'w')
        for key in self.smoothedProbs:
            w.write(key+'\t'+str(self.smoothedProbs[key])+'\n')
        w.close()
        #return self.smoothedProb                            

    def getProbability(self, userId, newSeq):
        newSeqIds = [self.obj2id[s] for s in newSeq]       
        newSeqIds_np = np.array(newSeqIds, dtype = 'i4').copy()
        logSeqProbZ = np.zeros(self.Psi_sz.shape[1], dtype='d').copy()
        #print(logSeqProbZ)
        logSeqScore = cythonOptimize.calculateSequenceProb(newSeqIds_np, len(newSeqIds_np), logSeqProbZ, self.true_mem_size, userId, self.Theta_zh, self.Psi_sz) 
        #seqScore = cythonOptimize.calculateSequenceProb(newSeqIds_np, len(newSeqIds_np), self.true_mem_size, userId, self.Theta_zh, self.Psi_sz)                                            
        #seqScore = calculateSequenceProb(newSeq, true_mem_size, userId, obj2id, Theta_zh, Psi_sz)
        #asd = open('logprob','w')
        #for x in seqScore:
        #    asd.write(str(x)+',')
        #asd.close()
        #print(seqScore)
        #logSeqScore = math.log10(seqScore)
        if(self.UNBIAS_CATS_WITH_FREQ):
            #unbiasingProb = 1.0
            logUnbiasingProb = 0 
            for ac in newSeq:
                if(ac in self.smoothedProbs):
                    #unbiasingProb *= self.smoothedProbs[ac]
                    logUnbiasingProb += self.smoothedProbs[ac]                                          
            #seqScore = float(seqScore)/float(unbiasingProb)  
            logSeqScore = logSeqScore - logUnbiasingProb
        #return seqScore
        return logSeqScore      
    
    def prepareTestSet(self):
        seqsCountWithNonExistingUsers = 0
        nonExistingUsers = set()
        testDic = {}
        print(">>> Preparing testset ...")
        testSetCount = 0
        r = open(self.SEQ_FILE_PATH, 'r')    
        for line in r:
            line = line.strip() 
            tmp = line.split()  
            actionStartIndex = 1
            user = tmp[0]   
            if(user not in self.hyper2id):
                #print("User: "+str(user)+" is not found in training set !")
                seqsCountWithNonExistingUsers += 1
                nonExistingUsers.add(user)
                continue
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
        print 'seqsCountWithNonExistingUsers=',seqsCountWithNonExistingUsers
        print 'number of nonExistingUsers=',len(nonExistingUsers)
        return testDic, testSetCount    
    
    def getAllPossibleActions(self):
        return self.obj2id.keys()  
        
    def getUserId(self, uid):
        return self.hyper2id[uid]   
        
