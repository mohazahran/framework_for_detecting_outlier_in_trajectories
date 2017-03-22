'''
Created on Mar 21, 2017

@author: mohame11
'''
import random
from TestSample import *
from MyEnums import *
from outlierEvaluation import *
import math

ANALYSIS_FILES_PATH = '/Users/mohame11/Desktop/pvalues_rnnlm3'
FILE_NAME = 'outlier_analysis_pvalues_'
NUM_ITERATIONS = 10

alphaList = [1e-20, 1e-15, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0]
pvalueList = [PVALUE.WITHOUT_RANKING, PVALUE.WITH_RANKING]

metric = METRIC.REC_PREC_FSCORE
tech = TECHNIQUE.MAJORITY_VOTING
hyp = HYP.EMPIRICAL
tadj = False


def main():
    
    lines = []
    
    pattern = re.compile(FILE_NAME+'\d+')
    allfiles = listdir(ANALYSIS_FILES_PATH)
    for file in allfiles:    
        if isfile(join(ANALYSIS_FILES_PATH, file)):            
            if(pattern.match(file) and '~' not in file):
                r = open(join(ANALYSIS_FILES_PATH, file), 'r')                                         
                for line in r:
                    lines.append(line)
                r.close()
    
    threshDic = {p:[] for p in pvalueList}
    batchSize = len(lines)//NUM_ITERATIONS
    for i in range(NUM_ITERATIONS):
        print i,'/',NUM_ITERATIONS
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
        
        for pv in pvalueList:
            bestAlpha = 0
            bestScore = 0
            for alpha in alphaList:            
                #print(metric, pv,alpha,tech,hyp,tadj)           
                ev = OutlierEvaluation(pasredData, tech, hyp, metric, pv, alpha, tadj)
                ev.evaluate()
                fscore = ev.metricObj.stats[-1]
                if(fscore > bestScore):
                    bestScore = fscore
                    bestAlpha = alpha
                    
            threshDic[pv].append((bestAlpha, bestScore))
    
    for pv in pvalueList:
        print(pv)
        
        alphas = [x[0] for x in threshDic[pv]]
        scores = [x[1] for x in threshDic[pv]]
        
        avgAlpha = float(sum(alphas))/float(len(alphas))
        avgScore = float(sum(scores))/float(len(scores))
        
        stddAlphas = math.sqrt( sum([(x-avgAlpha)**2 for x in alphas]) / float(len(alphas)) )
        stddScores = math.sqrt( sum([(x-avgScore)**2 for x in scores]) / float(len(scores)) )
        
        print 'Alpha=', avgAlpha, '+/-', stddAlphas
        print 'Fscore=', avgScore, '+/-', stddScores
    
                
                
               
                

    
main()    
print('DONE!')