'''
Created on Oct 28, 2017

@author: mohame11
'''
from TestSample import *

class LastFm(object):
    
    def __init__(self, PATH_TO_TRACE='', true_mem_size=9):
        self.PATH_TO_TRACE = PATH_TO_TRACE
        self.true_mem_size = true_mem_size
        
    def cal_and_write_probs(self, d):
        w = open(self.PATH_TO_TRACE+'_Artist_probs', 'w')
        smoothingParam = 1.0
        smoothedProbs = {}
        freqs = {}    
        counts = 0        
        for u in d:
            t = d[u]
            actions = t[0].actions
            for a in actions:
                if(a in freqs):
                    freqs[a] += 1
                else:
                    freqs[a] = 1                
                counts += 1
        for k in freqs:
            prob = float(freqs[k]+ smoothingParam) / float(counts + (len(freqs) * smoothingParam))
            smoothedProbs[k] = prob
        
        
        
        for k in smoothedProbs:
            w.write(str(k) + '\t' + str(smoothedProbs[k]) + '\n')
        w.close()
        return self.PATH_TO_TRACE+'_Artist_probs'
    
    def read_probs(self, FILE = ''):
        r = open(FILE, 'r')
        probs = {}
        for line in r:
            parts = line.strip().split()
            probs[parts[0]] = float(parts[1])
        r.close()
        return probs
        
    def formOriginalSeq2(self, tests):
        origSeq = list(tests[0].actions)  
        if(len(tests) <= 1):
            return origSeq
        for i in range(1,len(tests)):
            a = tests[i].actions[-1]
            origSeq.append(a)    
        return origSeq
    def readTrace(self):
        ACTION_COUNT = self.true_mem_size+1
        testDic = {}
        r = open(self.PATH_TO_TRACE, 'r')   
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
        
        return testDic
            
           
            
    
    def restrict_to_top_k_trace(self, k=5000, probs=None):
        artistsDesc = sorted(probs, key=lambda k: (-probs[k], k), reverse=False)
        topk = set(artistsDesc[:k])
        
        userDic = self.readTrace()
        
        w = open(self.PATH_TO_TRACE+'_top'+str(k), 'w')
        for u in userDic:
            test = userDic[u]
            actions = test[0].actions
            filteredActions = [a for a in actions if a in topk]
            if(len(filteredActions) < self.true_mem_size+1):
                continue
        
            
            limit = len(filteredActions) - (self.true_mem_size+1) + 1
            times = '0\t'*self.true_mem_size
            for i in range(limit):
                w.write(times)
                w.write(u+'\t')
                seq = filteredActions[i : i+self.true_mem_size+1]
                toWrite = '\t'.join(seq)
                w.write(toWrite+'\n')
            w.flush()
        w.close()
        
    
    def sample(self, k):
        r = open(self.PATH_TO_TRACE, 'r')
        w = open(self.PATH_TO_TRACE+'_sample'+str(k), 'w')
        c = 0
        for line in r:
            w.write(line)
            c += 1
            if(c > k):
                break
        w.close()
            
            
        
        
if __name__ == "__main__":
    lf = LastFm('/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/lastFm/lastfm_win10_trace_sample5000', 9)
    #lf.sample(5000)
    #d = lf.readTrace()
    #f = lf.cal_and_write_probs(d)
    probs = lf.read_probs(FILE = lf.PATH_TO_TRACE+'_Artist_probs')
    lf.restrict_to_top_k_trace(k=100, probs=probs)
    print('DONE!')
            
                
                
        
        
        
            


        
        