'''
Created on Sep 12, 2017

@author: mohame11
'''
import sys
sys.path.append('/homes/mohame11/framework_for_detecting_outlier_in_trajectories/')
from TestSample import *

PATH = '/homes/mohame11/scratch/pins_repins_fixedcat/pins_repins_win10.trace'
FILE_TYPE = 'trace'
ACTION_COUNT = 10

testDic = {}


def formOriginalSeq(tests):
    origSeq = list(tests[0].actions)  
    if(len(tests) <= 1):
        return origSeq
    for i in range(1,len(tests)):
        a = tests[i].actions[-1]
        origSeq.append(a)    
    return origSeq

def doFormating():
    if(FILE_TYPE == 'trace'):
        r = open(PATH, 'r')   
        w = open(PATH+'_word2vec', 'w') 
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
            originalSeq = formOriginalSeq(tests)
            t = TestSample()  
            t.user = u
            t.actions = list(originalSeq)  
            testDic[u] = [t]
            
           
            st = ''
            for action in originalSeq:
                st += str(action)+'\t'
            w.write(st+'\n')
            
            
    w.close()        
            
if __name__ == "__main__":
    doFormating()
    print('DONE!')
    
    

