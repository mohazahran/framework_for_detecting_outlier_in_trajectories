'''
Created on Mar 30, 2017

@author: mohame11
'''
import random
from TestSample import *
from MyEnums import *
from outlierEvaluation import *
import math

class thresholdSelectionByMetric:
    
    def __init__(self):
        self.INPUT_PATH = '/u/scratch1/mohame11/pins_repins_fixedcat/simulatedData/pvalues_rnnlm9'
        self.resultsFilePath = self.INPUT_PATH + '/METRIC.REC_PREC_FSCORE_PVALUE.WITH_RANKING'
        self.FILE_NAME = 'outlier_analysis_pvalues_'
        self.requiredLevel = 0.9
        self.epsilon = 1e-4
        self.metric = METRIC.REC_PREC_FSCORE
        self.PVALUE = PVALUE.WITH_RANKING
        self.tech = TECHNIQUE.MAJORITY_VOTING
        self.hyp = HYP.EMPIRICAL
        self.tadj = False
        
    
    def getBoundingAlphas(self):
        r = open(self.resultsFilePath, 'r')
        self.upperAlpha = None
        self.lowerAlpha = None
        for line in r:
            parts = line.split(':')
            params = parts[0].split(', ')
            results = parts[-1].replace(')','').replace('(','').split(', ')
            config = ', '.join(params[1:])
            alpha = float(params[0].split('=')[-1])
            
            tp=float(results[0].split('=')[-1])
            fp=float(results[1].split('=')[-1])
            fn=float(results[2].split('=')[-1])
            tn=float(results[3].split('=')[-1])
            #res = (tp+tn)/(tp+tn+fp+fn)
            res = fp/(tn+fp)
            #print res
          
                
            if(abs(res - self.requiredLevel) <= self.epsilon):
                return alpha,res
            
            if(res  < self.requiredLevel):
                self.lowerAlpha = [alpha,res]
                
            if(res  > self.requiredLevel):
                self.upperAlpha = [alpha,res]
            
            if(self.lowerAlpha != None and self.upperAlpha != None):
                return
            
                
            
        

    def thresholdSearch(self):
        lines = []
        pattern = re.compile(self.FILE_NAME+'\d+')
        allfiles = listdir(self.INPUT_PATH)
        for file in allfiles:    
	    #print file
            if isfile(join(self.INPUT_PATH, file)):            
                if(pattern.match(file) and '~' not in file):
                    r = open(join(self.INPUT_PATH, file), 'r')                                         
                    for line in r:
                        lines.append(line)
                    r.close()
        
        pasredData = TestSample.parseAnalysisByData(lines)
            
        
        diff = self.epsilon + 1
        print 'starting'
        while(diff > self.epsilon):
            currAlpha = (self.lowerAlpha[0] + self.upperAlpha[0])/2
            #debugPath = self.INPUT_PATH+'DEBUG_'+str(pv)+'_'+str(alpha)
            ev = OutlierEvaluation(pasredData, self.tech, self.hyp, self.metric, self.PVALUE, currAlpha, self.tadj, '')
            ev.evaluate()
            summary = ev.metricObj.getSummary()
            results = summary.replace(')','').replace('(','').split(', ')
            tp=float(results[0].split('=')[-1])
            fp=float(results[1].split('=')[-1])
            fn=float(results[2].split('=')[-1])
            tn=float(results[3].split('=')[-1])
            #res = (tp+tn)/(tp+tn+fp+fn)
            res = fp/(tn+fp)
            if(abs(res-self.requiredLevel) <= self.epsilon):
                return currAlpha, res
            
            if(self.requiredLevel > res):
                self.lowerAlpha = [currAlpha, res]
            elif(self.requiredLevel < res):
                self.upperAlpha = [currAlpha, res]
            
            print 'currentAlpha=', currAlpha, ' metric=', res, 'tp=', tp, 'fp=', fp, 'fn=', fn, 'tn=', tn 
               






def work():
    tr = thresholdSelectionByMetric()
    ret = tr.getBoundingAlphas()
    #print 'ret=', ret
    print 'upperAlpha=', tr.upperAlpha, ' lowerAlpha=', tr.lowerAlpha
    if(ret != None):
        print 'Alpha=',ret[0],' metric=',ret[1]
        return
    
    alpha, res = tr.thresholdSearch()
    
    

if __name__ == "__main__":
    work()    
    print('DONE!')
