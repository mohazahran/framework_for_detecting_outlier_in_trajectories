'''
Created on Mar 21, 2017

@author: mohame11
'''
import random
from TestSample import *
from MyEnums import *
from outlierEvaluation import *
import math


class ThresholdSelection:
    def __init__(self):
        self.INPUT_PATH = '/Users/mohame11/Desktop/pvalues_rnnlm3'
        self.FILE_NAME = 'outlier_analysis_pvalues_'
        self.NUM_ITERATIONS = 100
        self.BATCH_SIZE = -1 # -1 means use all data
        
        self.alphaList = [1e-20, 1e-15, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0]
        self.pvalueList = [PVALUE.WITHOUT_RANKING, PVALUE.WITH_RANKING]
        
        self.metric = METRIC.REC_PREC_FSCORE
        self.tech = TECHNIQUE.MAJORITY_VOTING
        self.hyp = HYP.EMPIRICAL
        self.tadj = False


    def selectThreshold(self):
        
        lines = []
        
        pattern = re.compile(self.FILE_NAME+'\d+')
        allfiles = listdir(self.INPUT_PATH)
        for file in allfiles:    
            if isfile(join(self.INPUT_PATH, file)):            
                if(pattern.match(file) and '~' not in file):
                    r = open(join(self.INPUT_PATH, file), 'r')                                         
                    for line in r:
                        lines.append(line)
                    r.close()
        
        #threshDic = {p:[] for p in pvalueList}
        threshDic = {}
        for p in self.pvalueList:
            threshDic[p] = []
            
        batchSize = self.BATCH_SIZE
        if(batchSize == -1):
            batchSize = len(lines)//self.NUM_ITERATIONS
        for i in range(self.NUM_ITERATIONS):
            #print i,'/',self.NUM_ITERATIONS
            samplesIds = set(random.sample(xrange(len(lines)), batchSize))
            samples = []
            leftOvers = []
            for j in range(len(lines)):
                if (j in samplesIds):
                    samples.append(lines[j])
                else:
                    leftOvers.append(lines[j])
            lines = leftOvers
            
            pasredData = TestSample.parseAnalysisByData(samples)
            
            for pv in self.pvalueList:
                bestAlpha = 0
                bestScore = 0
                for alpha in self.alphaList:            
                    #print(metric, pv,alpha,tech,hyp,tadj)           
                    ev = OutlierEvaluation(pasredData, self.tech, self.hyp, self.metric, pv, alpha, self.tadj)
                    ev.evaluate()
                    fscore = ev.metricObj.stats[-1]
                    if(fscore > bestScore):
                        bestScore = fscore
                        bestAlpha = alpha
                        
                threshDic[pv].append((bestAlpha, bestScore))
        
        for pv in self.pvalueList:
            print(pv)
            
            alphas = [x[0] for x in threshDic[pv]]
            scores = [x[1] for x in threshDic[pv]]
            
            avgAlpha = float(sum(alphas))/float(len(alphas))
            avgScore = float(sum(scores))/float(len(scores))
            
            stddAlphas = math.sqrt( sum([(x-avgAlpha)**2 for x in alphas]) / float(len(alphas)) )
            stddScores = math.sqrt( sum([(x-avgScore)**2 for x in scores]) / float(len(scores)) )
            
            print 'Alpha=', avgAlpha, '+/-', stddAlphas
            print 'Fscore=', avgScore, '+/-', stddScores
        
                    
                
def work():
    t = ThresholdSelection()
    t.selectThreshold()        
                
if __name__ == "__main__":
    work()
    print('DONE!')
