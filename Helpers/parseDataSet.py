'''
Created on Jul 25, 2016

@author: Mohamed Zahran
'''

DATA_PATH = 'D:/Career/Work/Purdue/PhD_courses/Summer2016_sem3/Data/'
PINS_PATH = DATA_PATH + 'pins.csv'
LIKESS_PATH = DATA_PATH + 'likes.csv'
REPINS_PATH = DATA_PATH + 'repins.csv'
USERS_PATH = DATA_PATH + 'pnt-users.csv'
FB_PATH = DATA_PATH + 'fb-graph.csv'

def readPins():
    r = open(PINS_PATH,'r')
    s = set()
    for line in r:
        parts = line.strip().split('|')
        user = parts[0]
        pin = parts[1]        
        web = parts[2]
        if(web in s):
            print line
        else:
            s.add(web)

def main():  
    
    fixDelimeter()

def fixDelimeter():
    r = open(FB_PATH,'r')
    w = open(FB_PATH+'_fixed','w')
    for line in r:
        newLine = line.replace('|',',')
        w.write(newLine)
    r.close()
    w.close()
                 
if __name__ == '__main__':
    main()
    print 'DONE!'          