'''
Created on Sep 12, 2017

@author: mohame11
'''
import sys
sys.path.append('/homes/mohame11/framework_for_detecting_outlier_in_trajectories/')
from TestSample import *

PATH = '/u/scratch1/mohame11/lastFm_filtered/lastfm_win10_trace_top5000'
FILE_TYPE = 'trace'
ACTION_COUNT = 10

testDic = {}
actions = {}
users = {}


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
    currentUserCount = 0
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
            if(u not in users):
               users[u] = currentUserCount
               currentUserCount += 1

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
                st = str(ac)+'\t'+str(users[u])+'\t'+str(actions[action])
                ac += 1
                w.write(st+'\n')
            
            
    w.close()

    w = open(PATH+'_tribeflowpp_actionMappings', 'w')
    for a in actions:
        w.write(str(a)+'\t'+str(actions[a])+'\n') 
    w.close()       

    w = open(PATH+'_tribeflowpp_userMappings', 'w')
    for u in users:
        w.write(str(u)+'\t'+str(users[u])+'\n')
    w.close()
    
            
            
if __name__ == "__main__":
    doFormating()
    print('DONE!')
    
    

