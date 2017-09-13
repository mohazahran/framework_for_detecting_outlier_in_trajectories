'''
Created on Sep 12, 2017

@author: mohame11
'''
from TestSample import *

PATH = '/Users/mohame11/Downloads/traceTmp'
FILE_TYPE = 'trace'
ACTION_COUNT = 10

testDic = {}
actions = {}


def formOriginalSeq(tests):
    origSeq = list(tests[0].actions)  
    if(len(tests) <= 1):
        return origSeq
    for i in range(1,len(tests)):
        a = tests[i].actions[-1]
        origSeq.append(a)    
    return origSeq

def doFormating():
    currentActionCount = 0
    if(FILE_TYPE == 'trace'):
        r = open(PATH, 'r')   
        w = open(PATH+'_tribeflowpp', 'w') 
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
            
            ac = 1
            for action in originalSeq:
                if(action not in actions):
                    actions[action] = currentActionCount
                    currentActionCount += 1
                st = str(ac)+'\t'+str(u)+'\t'+str(actions[action])
                ac += 1
                w.write(st+'\n')
            
            
    w.close()        
            
            
            
if __name__ == "__main__":
    doFormating()
    
    

