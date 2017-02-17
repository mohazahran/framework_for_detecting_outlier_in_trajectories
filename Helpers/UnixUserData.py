'''
Created on Feb 8, 2017

@author: mohame11
'''
from os import listdir



DATA_PATH = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/UNIX_user_data/data/'



def parse():
    data = {}
    files = listdir(DATA_PATH)
    for f in files:
        if('USER' not in f):
            continue
        print (f)
        data[f] = []
        r = open(DATA_PATH+f, 'r')
        seq = []
        for line in r:
            line = line.strip()
            if(line == '**SOF**'):
                seq = []
            elif(line == '**EOF**'):
                if(len(seq)>1):
                    data[f].append(list(seq))
            else:
                lineParts = line.split()
                if(len(lineParts)>0):
                    for p in lineParts:
                        seq.append(p)
                #else:
                #    print(line)
    return data
            

def generate_ngram_trace(data):
    w = open(DATA_PATH+'training_Ngram', 'w')
    for u in data:
        seqs = data[u]
        for s in seqs:
            w.write(' '.join(s)+'\n')
    w.close()


def generate_tribeflow_trace(data, burst = 10):
    w = open(DATA_PATH+'training_tribeflow_burst_'+str(burst), 'w')
    for u in data:
        seqs = data[u]
        for s in seqs:
            if(len(s) >= burst):
                burstCount = len(s)-burst+1
                for i in range(burstCount):
                    b = s[i:i+burst]
                    toPrint = '0\t'*(burst-1) + u +'\t' + '\t'.join(b)
                    w.write(toPrint+'\n')
    w.close()
    

'''
def checkup():
    r = open(DATA_PATH+'training_tribeflow_burst_10','r')
    for line in r:
        spl = line.strip().split('\t')
        print (spl)
        assert len(spl) >= 4
        assert (len(spl) - 2) % 2 == 0
        mem_size = (len(spl) - 2) // 2
'''

def main():
    data = parse()
    #generate_ngram_trace(data)
    generate_tribeflow_trace(data, burst = 10)
    #checkup()



main()
print('DONE !')