'''
Created on Feb 4, 2017

@author: mohame11
'''



TRAINING_FILE = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/UNIX_user_data/data/training_Ngram'
ACTIONS_LIST = TRAINING_FILE+'_ALL_ACTIONS'

r = open(TRAINING_FILE, 'r')
actions = set()
for line in r:
    parts = line.strip().split()
    for p in parts:
        actions.add(p)
        
        
w = open(ACTIONS_LIST, 'w')
for a in actions:
    w.write(a+'\n')
w.close()
print('DONE!')
    
    