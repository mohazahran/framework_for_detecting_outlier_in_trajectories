'''
Created on Oct 3, 2016

@author: zahran
'''
import pandas as pd
import random

#common
SRC_FILE = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/simulatedData/pins_repins_bbtt3_simulatedData_fixed_3'
INJECTED_TRAIN = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/simulatedData_injected/pins_repins_bbtt3_simulatedData_fixed_3_injected'
isTribeflow = False
injectedInstancesCount = 0 # 0 for all the training data
doRandomization = False
maxInjections = 1
isTraceFile = False #tracefile has the same format as tribeflow's training data

#tribeflow
MODEL_PATH = '/scratch/snyder/m/mohame11/unix_user_data/tribeflow_win4/training_tribeflow_burst_4_noop.h5'

#ngram
ALL_ACTION_PATH = '/scratch/snyder/m/mohame11/pins_repins_win4_fixedcat/pins_repins_win4.trace_forLM_RNN_train_ALL_ACTIONS'

def main():
    if(isTribeflow):
    	store = pd.HDFStore(MODEL_PATH)     
    	obj2id = dict(store['source2id'].values)
    	allCats = obj2id.keys()
    	Dts = store['Dts']
    	winSize = Dts.shape[1]    
    else:
	alla = open(ALL_ACTION_PATH,'r')
	allCats = []
	for line in alla:
		allCats.append(line.strip())
	alla.close()
        print(len(allCats))

    w = open(INJECTED_TRAIN, 'w')        
    r = open(SRC_FILE, 'r')
    N = 0
    if(injectedInstancesCount == 0):        
        for l in r:
            N += 1
    else:           
        N = injectedInstancesCount
    r.close()
    r = open(SRC_FILE, 'r')
    #Reservoir Sampling Algorithm
    sample = []
    for i,line in enumerate(r):
        if i < N:
            sample.append(line)
        else:
            break
       
#     for i,line in enumerate(r):
#         if i < N:
#             sample.append(line)
#         elif i >= N and random.random() < N/float(i+1):
#             replace = random.randint(0,len(sample)-1)
#             sample[replace] = line
        #else:
        #    break
    print('injectedInstancesCount=',injectedInstancesCount)
    allCategories = set(allCats)
    for line in sample:
        allCats = set(allCategories)
        line = line.strip()
        parts = line.split()
        if(isTribeflow):
        	if isTraceFile == True:
            		times = parts[:winSize]
            		user = parts[winSize]
            		cats = parts[winSize+1:]
        	else:
            		user = parts[0]
            		cats = parts[1:winSize+2]
	else:
		cats = parts	
        for c in cats:
            allCats.discard(c)
        markers = ['false']*(len(cats))
	#print(len(cats), maxInjections)
        injectedIdx = random.sample(list(range(len(cats))), maxInjections)
        for idx in injectedIdx:
            originalCat = cats[idx]                                        
            if(idx == 0):                    
                while True:
                    randCat = random.sample(allCats, 1)[0]                        
                    ok = (randCat != originalCat) and (randCat != cats[idx+1])
                    if(ok):
                        break                            
            elif (idx == len(cats)-1):
                while True:
                    randCat = random.sample(allCats, 1)[0]                        
                    ok = (randCat != originalCat) and (randCat != cats[-2])
                    if(ok):
                        break
            else:
                while True:
                    randCat = random.sample(allCats, 1)[0]                        
                    ok = (randCat != originalCat) and (randCat != cats[idx+1]) and (randCat != cats[idx-1])
                    if(ok):
                        break
                    
            cats[idx]= randCat
            markers[idx] = 'true'
        if(isTribeflow):
        	w.write(user+'\t')
	
        for c in cats:
            w.write(c+'\t')
	if(not isTribeflow):
		w.write('###\t')
        for m in markers:
            w.write(m+'\t')
        w.write('\n')
    w.close()
    if(isTribeflow):
	    store.close()
    
                                    
            




main()
print('DONE !')
