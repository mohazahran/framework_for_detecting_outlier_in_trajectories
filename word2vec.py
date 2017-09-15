'''
Created on Sep 14, 2017

@author: mohame11
'''
from DetectionTechnique import *
from MyEnums import *
import gensim
import math

class Word2vec (DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)  
        self.type = SEQ_PROB.WORD2VEC
        self.allActions = []
        self.model = None
       
        
    def loadModel(self):
        self.model = gensim.models.Word2Vec.load(self.model_path)  # you can continue training with the loaded model!
        r = open(self.ALL_ACTIONS_PATH, 'r')
        for line in r:
            line = line.strip()
            if(len(line)>0):
                self.allActions.append(line)
        r.close()
        
    
    def getProbability(self, userId, newSeq):
        #model.score(["The fox jumped over a lazy dog".split()])
        line = ' '.join(newSeq)
        logprob = self.model.score([line.split()])
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
        return testDic, testSetCount         
        
        

        
              
#self, testDic, quota, coreId, q, store, true_mem_size, hyper2id, obj2id, Theta_zh, Psi_sz, smoothedProbs

    def getAllPossibleActions(self):
        return self.allActions
    
    def getUserId(self, uid):
        return uid

    
    def train(self, dataSetPath):
        #gensim.models.word2vec.LineSentence(source, max_sentence_length=10000, limit=None)¶
        sentences = gensim.models.word2vec.LineSentence(dataSetPath)
        
        '''
        Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/homes/mohame11/anaconda2/lib/python2.7/site-packages/gensim-2.3.0-py2.7-linux-x86_64.egg/gensim/models/word2vec.py", line 1041, in score
        run word2vec with hs=1 and negative=0 for this to work.")
    RuntimeError: We have currently only implemented score for the hierarchical softmax scheme, 
    so you need to have run word2vec with hs=1 and negative=0 for this to work.
    

        '''
        model = gensim.models.Word2Vec(sentences, size=200, window=9, min_count=2, workers=40, hs=1, negative=0)
        
        model.save(dataSetPath+'_Word2vec')
        
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
        
        
        



def experiments():
    w2v = Word2vec()
    w2v.train('')
    
    
    
#experiments()
