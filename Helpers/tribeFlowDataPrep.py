'''
Created on Aug 25, 2016

@author: Mohamed Zahran
'''
from random import shuffle
#import MySQLdb

#DATA_PATH = 'D:/Career/Work/New_Linux/shareFolder/'
DATA_PATH = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/tribeflow_outlierDetection/Data/sql_saved_data/'
SQL = 'likes__withFriendship.csv'
TRIBE_PATH = DATA_PATH + 'likes_withFriendship_win4.trace'


def pareseDataFromSQLWithNoDuplicateConsecutiveActions_likes():
    r = open(DATA_PATH+SQL,'r')
    w = open(TRIBE_PATH, 'w')
    toWrite = []
    user = '-1'
    actions = []
    areFriends = []
    prevAction = ''
    #unqActions = set()
    cnt = 0    
    MIN_WIN = 4
    catIndx = 5
    line = r.readline()
    for line in r:
        line = line.lower().strip().replace(' ','_').replace('"','')
        parts = line.split(',')
        for p in parts:
            p = p.strip()        
        cnt += 1
        if(user == parts[1] or user == '-1'):
            if(prevAction == '' or prevAction != parts[catIndx]):
                actions.append(parts[catIndx])
                areFriends.append(parts[-1])
                prevAction = parts[catIndx]                
            user = parts[1]    
        else:    
            if(len(actions) >= MIN_WIN):        
                for i in range(len(actions) - MIN_WIN + 1):
                    #times = ''
                    #for j in range(MIN_WIN-1):
                    #    times += '0'+'\t'     
                    #times += user+'\t'
                    sq = actions[i:i+MIN_WIN]
                    fr = areFriends[i:i+MIN_WIN]
                    frSeq = ''
                    seq = ''
                    for s in sq:
                        seq += s +'\t'
                    for f in fr:
                        frSeq += f +'\t'            
                    toWrite.append(user+'\t'+seq+frSeq)
                #    if(len(unqActions) < MIN_WIN):
                #        print(times+seq)
                user = parts[1]
                actions = []     
                areFriends = []                   
                actions.append(parts[catIndx])
                areFriends.append(parts[-1])
                prevAction = parts[catIndx]
            else:
                user = parts[1]
                actions = []   
                areFriends = []                      
                actions.append(parts[catIndx])
                areFriends.append(parts[-1])
                prevAction = parts[catIndx]
                
    
                                                                                                                                                                                                                    
    #shuffle(toWrite)
    for l in toWrite:
        w.write(l+'\n')   
    w.close()       

def pareseDataFromSQLWithNoDuplicateConsecutiveActions():
    r = open(DATA_PATH+SQL,'r')
    w = open(TRIBE_PATH, 'w')
    toWrite = []
    user = '-1'
    actions = []
    prevAction = ''
    #unqActions = set()
    cnt = 0    
    MIN_WIN = 4
    for line in r:
        line = line.lower().strip().replace(' ','_').replace('"','')
        parts = line.split(',')
        for p in parts:
            p = p.strip()        
        cnt += 1
        if(user == parts[1] or user == '-1'):
            if(prevAction == '' or prevAction != parts[4]):
                actions.append(parts[4])
                prevAction = parts[4]                
            user = parts[1]    
        else:    
            if(len(actions) >= MIN_WIN):        
                for i in range(len(actions) - MIN_WIN + 1):
                    times = ''
                    for j in range(MIN_WIN-1):
                        times += '0'+'\t'     
                    times += user+'\t'
                    sq = actions[i:i+MIN_WIN]
                    seq = ''
                    for s in sq:
                        seq += s +'\t'           
                    toWrite.append(times+seq)
                #    if(len(unqActions) < MIN_WIN):
                #        print(times+seq)
                user = parts[1]
                actions = []                        
                actions.append(parts[4])
                prevAction = parts[4]
            else:
                user = parts[1]
                actions = []                        
                actions.append(parts[4])
                prevAction = parts[4]
                
    
                                                                                                                                                                                                                    
    #shuffle(toWrite)
    for l in toWrite:
        w.write(l+'\n')   
    w.close()       

def pareseDataFromSQLWithNoDuplicateActions():
    r = open(DATA_PATH+SQL,'r')
    w = open(TRIBE_PATH, 'w')
    toWrite = []
    user = '-1'
    actions = []
    unqActions = set()
    cnt = 0    
    MIN_WIN = 5
    for line in r:
        line = line.strip().replace(' ','_')
        parts = line.split('\t')        
        cnt += 1
        if(user == parts[1] or user == '-1'):
            if(parts[4] not in unqActions):
                actions.append(parts[4])
                unqActions.add(parts[4])
                user = parts[1]    
        else:            
            for i in range(len(actions) - MIN_WIN + 1):
                times = ''
                for j in range(MIN_WIN-1):
                    times += '0'+'\t'     
                times += user+'\t'
                sq = actions[i:i+MIN_WIN]
                seq = ''
                for s in sq:
                    seq += s +'\t'           
                toWrite.append(times+seq)
                if(len(unqActions) < MIN_WIN):
                    print(times+seq)
            user = parts[1]
            actions = []
            unqActions = set()
            actions.append(parts[4])
    
                                                                                                                                                                                                                    
    #shuffle(toWrite)
    for l in toWrite:
        w.write(l+'\n')   
    w.close()       
    
def pareseDataFromSQLWithDuplicateActions():
    r = open(DATA_PATH+SQL,'r')
    w = open(TRIBE_PATH, 'w')
    toWrite = []
    user = '-1'
    actions = []
    cnt = 0    
    MIN_WIN = 5
    for line in r:
        line = line.strip().replace(' ','_')
        parts = line.split('\t')        
        cnt += 1
        if(user == parts[1] or user == '-1'):
            actions.append(parts[4])
            user = parts[1]    
        else:            
            for i in range(len(actions) - MIN_WIN + 1):
                times = ''
                for j in range(MIN_WIN-1):
                    times += '0'+'\t'
                    #w.write('0'+'\t')
                #w.write(user+'\t')
                times += user+'\t'
                sq = actions[i:i+MIN_WIN]
                seq = ''
                for s in sq:
                    seq += s +'\t'
                    #w.write(s +'\t')
                #w.write('\n')
                toWrite.append(times+seq)
            user = parts[1]
            actions = []
            actions.append(parts[4])
    
                                                                                                                                                                                                                    
    #shuffle(toWrite)
    for l in toWrite:
        w.write(l+'\n')   
    w.close()       

def combineFiles():
    filesPaths = [DATA_PATH+'pins_win4.trace',DATA_PATH+'repins_win4.trace']
    w = open(DATA_PATH+'pins_repins_win4.trace','w')
    for f in filesPaths:
        print (f)
        r = open(f,'r')
        for line in r:
            if(len(line) < 3):
                print(line)
                continue
            line = line.strip('\n')            
            w.write(line+'\n')
        r.close()
    w.close()

def addFriendship():    
    LIKE_FILE = DATA_PATH +'sqlData_likes_full_info_fixed.csv'
    LIKE_WITH_FRIENDS = DATA_PATH + 'sqlData_likes_full_info_fixed_withFriendship.csv'
    FB_FRIENDS = DATA_PATH + 'fb-graph_fixed.csv'
    
    fb = set()
    r_fb = open(FB_FRIENDS, 'r')
    for line in r_fb:
        line = line.strip()
        if(line not in fb):
            fb.add(line)
    r_fb.close()
    
    
    r_likes = open(LIKE_FILE, 'r')
    line = r_likes.readline()
    
    w_likesFriends = open(LIKE_WITH_FRIENDS, 'w')
    w_likesFriends.write(line.strip()+',areFriends'+'\n')
    cnt = 0
    for line in r_likes:
        line = line.strip()
        tokens = line.split(',')
        u1 = tokens[1]
        u2 = tokens[2]
        u12 = u1+','+u2
        u21 = u2+','+u1
        if(u12 in fb or u21 in fb):
            w_likesFriends.write(line+',True'+'\n')
            cnt += 1            
        else:
            w_likesFriends.write(line+',False'+'\n')
            
    print(cnt)
    w_likesFriends.close()
    

def selectLikesWithTrueFriendship():
    LIKE_FILE = DATA_PATH +'PARSED_sqlData_likes_full_info_fixed_withFriendship'
    LIKE_WITH_FRIENDS = DATA_PATH + 'sqlData_likes_full_info_fixed_ONLY_TRUE_friendship.csv'
    
    w = open(LIKE_WITH_FRIENDS, 'w')
    r = open(LIKE_FILE,'r')
    lst = []
    prevUser = '-1'
    foundFriend = False
    for line in r:
        line = line.strip()
        parts = line.split('\t')  
        user = parts[0]        
            
        if(prevUser == '-1'):
            lst.append(line)
            prevUser = user
        
        elif(user == prevUser):
            lst.append(line)
            
        else:
            if(foundFriend):
                foundFriend = False
                for itm in lst:
                    w.write(itm+'\n')
            lst = []
            lst.append(line)
            prevUser = user
        
        if('true' in parts):
            foundFriend = True
    
    w.close()
                
                  
        
        
            
    
def filter_unknows():
    r = open(DATA_PATH+SQL,'r')
    w = open(TRIBE_PATH, 'w')
    for line in r:
        line = line.strip().replace('"','')
        tokens = line.strip().split(',')
        if(tokens[-2] == '-1' or tokens[-2] == '3'):
            continue
        w.write(line+'\n')
    w.close()
    

def main():
    #selectLikesWithTrueFriendship()
    pareseDataFromSQLWithNoDuplicateConsecutiveActions_likes()
    #addFriendship()
    #filter_unknows()
    #combineFiles()
    #pareseDataFromSQLWithNoDuplicateConsecutiveActions()
    #pareseDataFromSQLWithNoDuplicateActions()
    #pareseDataFromSQLWithDuplicateActions()
   

           
            
        
    



if __name__ == '__main__':
    main()
    print 'DONE!'   
    
    
