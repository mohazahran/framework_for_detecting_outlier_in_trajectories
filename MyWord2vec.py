'''
Created on Sep 14, 2017

@author: mohame11
'''
from DetectionTechnique import *
from MyEnums import *
import gensim
import math
import random
import numpy as np

class MyWord2vec (DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)  
        self.type = SEQ_PROB.WORD2VEC
        self.allActions = []
        self.model = None
       
        
    def loadModel(self):
        self.model = gensim.models.Word2Vec.load(self.model_path)  # you can continue training with the loaded model!
        print 'Fast word2vec =', gensim.models.word2vec.FAST_VERSION
	print 'Fast word2vec_inner=', gensim.models.word2vec_inner.FAST_VERSION
        self.model.workers = 1
        
        r = open(self.ALL_ACTIONS_PATH, 'r')
        for line in r:
            line = line.strip()
            if(len(line)>0):
                self.allActions.append(line)
        r.close()
        
    
    def getProbability(self, userId, newSeq):
        #model.score(["The fox jumped over a lazy dog".split()])
        #line = ' '.join(newSeq)
        #logprob = self.model.score([line.split()])
        logprob = self.model.score(sentences = [newSeq], total_sentences = 1)
        return logprob[0]
        
        
        
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
        
        

        
              
#self, testDic, quota, coreId, q, store, true_mem_size, hyper2id, obj2id, Theta_zh, Psi_sz, smoothedProbs

    def getAllPossibleActions(self):
        return self.allActions
    
    def getUserId(self, uid):
        return uid

    def dumpAllActions(self):
        if(self.model == None):
            self.model = gensim.models.Word2Vec.load(self.model_path)
        
        w = open(self.model_path+'_ALL_ACTIONS','w')
        for a in self.model.wv.vocab:
            w.write(a+'\n')
        w.close()
    
    def train(self, dataSetPath):
        print 'Training word2vec ...'
        #gensim.models.word2vec.LineSentence(source, max_sentence_length=10000, limit=None)
        sentences = gensim.models.word2vec.LineSentence(dataSetPath)
        
        '''
        Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/homes/mohame11/anaconda2/lib/python2.7/site-packages/gensim-2.3.0-py2.7-linux-x86_64.egg/gensim/models/word2vec.py", line 1041, in score
        run word2vec with hs=1 and negative=0 for this to work.")
    RuntimeError: We have currently only implemented score for the hierarchical softmax scheme, 
    so you need to have run word2vec with hs=1 and negative=0 for this to work.
    
        '''
        model = gensim.models.Word2Vec(sentences, size=200, window=9, min_count=2, workers=40, hs=1, negative=0, sg=1)
        
        model.save(dataSetPath+'_SKIPG')
        
        if(self.model == None):
            self.model = model
        
        '''
        Word2vec constructor
        def __init__(self, sentences=None, size=100, alpha=0.025, window=5, min_count=5,
                 max_vocab_size=None, sample=1e-3, seed=1, workers=3, min_alpha=0.0001,
                 sg=0, hs=0, negative=5, cbow_mean=1, hashfxn=hash, iter=5, null_word=0,
                 trim_rule=None, sorted_vocab=1, batch_words=MAX_WORDS_IN_BATCH, compute_loss=False):
        '''
        
        '''
        import gensim
        from gensim.models.keyedvectors import KeyedVectors
        word_vectors = KeyedVectors.load_word2vec_format('/homes/mohame11/scratch/pins_repins_fixedcat/pins_repins_win10_word2vec_vectors_skipgram', binary=True)
        model = gensim.models.Word2Vec(hs=1,negative=0)
        model.wv = word_vectors
        model.score(['shopping'])
        '''
        
    def predictNext(self, seq):
        '''
        only works with negative !=0
        '''
        negBuff = self.model.negative
        self.model.negative = 5
        nextAction = self.model.predict_output_word(seq.split(),topn=1)
        self.model.negative = negBuff
        return nextAction
        

    def simulatedSeq(self, size):
        allActions = self.getAllPossibleActions()
        #allActions = ['shopping', 'news', 'education']
        startAction = random.choice(allActions)
        seq = [startAction]
        for i in range(size-1):
            maxProb  = -1*float('inf')
            mostLikelyAction = ''
            allActionsCopy = list(allActions)
            allActionsCopy.remove(seq[-1])
            for a in allActionsCopy:
                tmpSeq = list(seq)
                tmpSeq.append(a)
                logprob = self.model.score(sentences = [tmpSeq], total_sentences = 1)
                if(logprob > maxProb):
                    maxProb = logprob
                    mostLikelyAction = a
            seq.append(mostLikelyAction)
            
        return seq
    
    def simulateData(self, mu, sigma, sampleCount, filepath):
        w = open(filepath, 'w')
        sizes = np.random.normal(mu, sigma, sampleCount)
        for i in range(len(sizes)):
            print i,'/',len(sizes)
            if(sizes[i]<=9):
                continue
            seq = self.simulatedSeq(int(sizes[i]))
            #if(len(seq) <=9):
            #    print(seq)
            w.write(' '.join(seq)+'\n')
            w.flush()
        w.close()    
                   
        


def experiments():
    w2v = MyWord2vec()
    w2v.model_path = '/u/scratch1/mohame11/lastfm_WWW/lastfm_win10_trace_top5000_word2vec_SKIPG'
    #w2v.ALL_ACTIONS_PATH = '/u/scratch1/mohame11/pins_repins_fixedcat/pins_repins_win10.trace_word2vec_SKIPG_ALL_ACTIONS'
    #w2v.model_path = '/u/scratch1/mohame11/lastFm/lastfm_win10_trace_word2vec_SKIPG'
    w2v.ALL_ACTIONS_PATH = '/u/scratch1/mohame11/lastfm_WWW/lastfm_win10_trace_top5000_word2vec_SKIPG_ALL_ACTIONS'
    w2v.loadModel()
    #model = gensim.models.Word2Vec.load(w2v.model_path)  # you can continue training with the loaded model!
    #print('Fast word2vec =', gensim.models.word2vec.FAST_VERSION)
    #print('Fast word2vec_inner=', gensim.models.word2vec_inner.FAST_VERSION)
    w2v.simulateData(30, 10, 10000, w2v.model_path+'_simulatedData')
    #model.workers = 1
    #lst = model.wv.similar_by_vector(model.wv['education'])
    #for x in lst:
    #    print x
    #w2v.dumpAllActions()
    #w2v.train(w2v.model_path)
   
    
if __name__ == "__main__":    
    experiments()
    print('DONE!')
