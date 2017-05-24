#-*- coding: utf8
'''
Created on Oct 2, 2016

@author: zahran
'''
from MyEnums import *
from Metric import *
from HypTesting import *
from TestSample import *


#ANALYSIS_FILES_PATH = '/home/mohame11/pins_repins_fixedcat/allLikes/pvalues/'
#ANALYSIS_FILES_PATH = '/home/mohame11/pins_repins_fixedcat/injections/pvalues/'
#FILE_NAME = 'outlier_analysis_pvalues_'
#FILE_NAME = 'PARSED_pins_repins_win10_pinterest_INJECTED_SCORES_ANOMALY_ANALYSIS_'
    

class OutlierEvaluation:
    def __init__(self, allData, techType, hyp, metricType, pvalueTyp, alpha, testSetCountAdjust, debugPath = ''):
        self.allData = allData
        self.techType = techType
        self.hypType = hyp
        self.metricType = metricType
        self.pvalueTyp = pvalueTyp
        self.alpha = alpha
        self.testSetCountAdjust = testSetCountAdjust
        self.debugPath = debugPath
        
        if(len(self.debugPath) != 0):
            self.debugger = open(self.debugPath, 'w')
            
        
        allTestsCount = 0
        for u in self.allData:
            allTestsCount += len(self.allData[u])
            
        self.allTestsCount = allTestsCount #this is the count of "B+1" actions sequences we have.
                        
        if(hyp == HYP.BONFERRONI):
            self.hypObj = Bonferroni(self.alpha, self.testSetCountAdjust, self.allTestsCount)
        elif(hyp == HYP.HOLMS):
            self.hypObj = Holms(self.alpha, self.testSetCountAdjust, self.allTestsCount)
        elif(hyp == HYP.EMPIRICAL):
            self.hypObj = Empirical(self.alpha, self.testSetCountAdjust, self.allTestsCount)
        
        if(self.metricType == METRIC.CHI_SQUARE):
            self.metricObj = Chisq()
        elif(self.metricType == METRIC.REC_PREC_FSCORE):
            self.metricObj = rpf()
        elif(self.metricType == METRIC.FISHER):
            self.metricObj = Fisher()
        elif(self.metricType == METRIC.BAYESIAN):
            self.metricObj = Bayesian()
            
               
        
        
                                
    def formOriginalSeq(self, tests):
        origSeq = list(tests[0].actions)  
        origGoldMarkers = list(tests[0].goldMarkers)
        for i in range(1,len(tests)):
            a = tests[i].actions[-1]
            g = tests[i].goldMarkers[-1]
            origSeq.append(a)
            origGoldMarkers.append(g)            
        return origSeq, origGoldMarkers
    
    
    def dumpDebuggingInfo(self, u, seq ,pValues, decisionVec, goldMarkers):
	if(len(self.debugPath) == 0):
	    return
        self.debugger.write('\nUser: '+str(u)+'\n')
        for i in range(len(seq)):
            self.debugger.write(seq[i] + ' || ')
            self.debugger.write(str(pValues[i]) + ' || ')
            self.debugger.write(str(decisionVec[i]) + ' || ')
            self.debugger.write(str(goldMarkers[i]) + ' || ')
            self.debugger.write('\n')
            
        
    
    def aggregateDecisions(self, actionDecisions):
        if(self.techType == TECHNIQUE.ALL_OR_NOTHING):
            for d in actionDecisions:
                if(d == DECISION.NORMAL):
                    return DECISION.NORMAL
            return DECISION.OUTLIER
            
        elif(self.techType == TECHNIQUE.ONE_IS_ENOUGH):
            for d in actionDecisions:
                if(d == DECISION.OUTLIER):
                    return DECISION.OUTLIER
            return DECISION.NORMAL
            
        elif(self.techType == TECHNIQUE.MAJORITY_VOTING):
            counts = {}
            mySet = set(actionDecisions)
            if(len(mySet) == 1):
                return actionDecisions[0]
            counts[DECISION.NORMAL] = actionDecisions.count(DECISION.NORMAL)
            counts[DECISION.OUTLIER] = actionDecisions.count(DECISION.OUTLIER)
            
            if(counts[DECISION.NORMAL] >= counts[DECISION.OUTLIER]):
                return DECISION.NORMAL
            return DECISION.OUTLIER
                        
            
    def evaluate_continousAlpha(self, metricList, files):
        allPvalues = {}
        allGoldMarkers = {}
        cnt = 0
        for u in self.allData:
            tests = self.allData[u]
            for ti, t in enumerate(tests):
                if(self.pvalueTyp == PVALUE.WITH_RANKING):
                    pValues = t.PvaluesWithRanks
                elif(self.pvalueTyp == PVALUE.WITHOUT_RANKING):
                    pValues = t.PvaluesWithoutRanks
                golds = t.goldMarkers
                for p in pValues:
                    #theKey = '_'.join([str(u),str(ti),str(p)])
                    theKey = cnt
                    allPvalues[theKey] = pValues[p]
                    allGoldMarkers[theKey] = golds[p]
                    cnt += 1
        
        keySortedAllPvalues = sorted(allPvalues, key=lambda k: (-allPvalues[k], k), reverse=True)  #sort ascendingly
        trueOutlierCount = allGoldMarkers.values().count(GOLDMARKER.TRUE)
        myCounter = -1
        for rank in keySortedAllPvalues:
            pv =  allPvalues[rank]
            gold = allGoldMarkers[rank]
            myCounter += 1
            #at this pvalue, we set our alpha=pv. which means we flag this action to be OUTLIER
            for m in metricList:
                if(gold == GOLDMARKER.TRUE):
                    m.OT += 1
                if(gold == GOLDMARKER.FALSE):
                    m.OF += 1  
                m.NT = trueOutlierCount-m.OT
                m.NF = (len(allGoldMarkers)-trueOutlierCount)-m.OF
                           
                m.calculateStats()
                logger = files[m.type]
                logger.write('alpha='+str(pv))
                logger.write(', '+str(TECHNIQUE.MAJORITY_VOTING))       
                logger.write(', '+str(HYP.EMPIRICAL))                                
                logger.write(', TScountAdj='+str(False))
                logger.write(': '+m.getSummary()+'\n')
                if(myCounter % 1000 == 0):
                    logger.flush()
                    print myCounter, ' examples finished'
        for f in files:
            f.close()
              
                
            
        
    def evaluate(self):         
        if(self.testSetCountAdjust == False):   
            for u in self.allData:
                tests = self.allData[u]
                #print(u,len(tests),len(tests[0].actions))
                if(len(tests)>1):
                    originalSeq, originalGoldMarkers = self.formOriginalSeq(tests)
                    winSize = len(tests[0].PvaluesWithRanks)
                    decisionsForOriginalSeq = []
                    
                    for origIdx in range(len(originalSeq)):
                        firstSeqIdxAppear = origIdx // winSize  #the index of first seq this current action appeared in                   
                        firstIdxInFirstSeq = origIdx % winSize  #the index of current action in that seq
                        
                        idxInSeq = firstIdxInFirstSeq   
                        actionDecisions = []
                        
                        for seqIdx in range(firstSeqIdxAppear, len(tests)):                                                
                            if(idxInSeq < 0):
                                break
                            t = tests[seqIdx]
                            goldMarkers = t.goldMarkers                
                            if(self.pvalueTyp == PVALUE.WITH_RANKING):
                                pValues = t.PvaluesWithRanks
                            elif(self.pvalueTyp == PVALUE.WITHOUT_RANKING):
                                pValues = t.PvaluesWithoutRanks
                                
                            keySortedPvalues = sorted(pValues, key=lambda k: (-pValues[k], k), reverse=True)                                            
                            decisionVec = self.hypObj.classify(keySortedPvalues, pValues)                    
                            actionDecisions.append(decisionVec[idxInSeq])
                            
                            idxInSeq -= 1
                            
                        # now we have a list of decisions for the action at index=origIdx
                        # depending on the classification technique we pick only one decision out of the actionDecisions
                        finalDecision = self.aggregateDecisions(actionDecisions)
                        decisionsForOriginalSeq.append(finalDecision)
                                   
                    self.metricObj.update(decisionsForOriginalSeq, originalGoldMarkers)
                    self.dumpDebuggingInfo(u, originalSeq, pValues, decisionsForOriginalSeq, originalGoldMarkers)
                    
                elif(len(tests) == 1): # the number of sequences is 1, no need to get original sequences.
                    t = tests[0]
                    goldMarkers = t.goldMarkers    
                    seq = t.actions            
                    if(self.pvalueTyp == PVALUE.WITH_RANKING):
                        pValues = t.PvaluesWithRanks
                    elif(self.pvalueTyp == PVALUE.WITHOUT_RANKING):
                        pValues = t.PvaluesWithoutRanks
                        
                    keySortedPvalues = sorted(pValues, key=lambda k: (-pValues[k], k), reverse=True)
                    #print(len(keySortedPvalues), len(pValues))                                            
                    decisionVec = self.hypObj.classify(keySortedPvalues, pValues)  
                    
                    self.metricObj.update(decisionVec, goldMarkers)
                    self.dumpDebuggingInfo(u, seq , pValues, decisionVec, goldMarkers)
                    
                #self.metricObj.calculateStats()   
        #----------------------------------------------------------------------------------------------------------------------  
        #when self.testSetCountAdjust == True   
        else:
            allPvalues = {}
            for u in self.allData:
                tests = self.allData[u]
                for ti, t in enumerate(tests):
                    if(self.pvalueTyp == PVALUE.WITH_RANKING):
                        pValues = t.PvaluesWithRanks
                    elif(self.pvalueTyp == PVALUE.WITHOUT_RANKING):
                        pValues = t.PvaluesWithoutRanks
                    for p in pValues:
                        theKey = '_'.join([str(u),str(ti),str(p)])
                        allPvalues[theKey] = pValues[p]
            
            keySortedAllPvalues = sorted(allPvalues, key=lambda k: (-allPvalues[k], k), reverse=True)  #sort ascendingly
            
            for u in self.allData:
                tests = self.allData[u]
                originalSeq, originalGoldMarkers = self.formOriginalSeq(tests)
                winSize = len(tests[0].PvaluesWithRanks)
                decisionsForOriginalSeq = []
                
                for origIdx in range(len(originalSeq)):
                    firstSeqIdxAppear = origIdx // winSize  #the index of first seq this current action appeared in                   
                    firstIdxInFirstSeq = origIdx % winSize  #the index of current action in that seq
                    
                    idxInSeq = firstIdxInFirstSeq   
                    actionDecisions = []
                    
                    for seqIdx in range(firstSeqIdxAppear, len(tests)):                                                
                        if(idxInSeq < 0):
                            break
                        t = tests[seqIdx]
                        goldMarkers = t.goldMarkers                
                        if(self.pvalueTyp == PVALUE.WITH_RANKING):
                            pValues = t.PvaluesWithRanks
                        elif(self.pvalueTyp == PVALUE.WITHOUT_RANKING):
                            pValues = t.PvaluesWithoutRanks
                        
                        theKey = '_'.join([str(u), str(seqIdx), str(idxInSeq)])
                        rank = keySortedAllPvalues.index(theKey)
                        #keySortedPvalues = sorted(pValues, key=lambda k: (-pValues[k], k), reverse=True)                                            
                        #decisionVec = self.hypObj.classify(keySortedPvalues, pValues)                   
                        dec = self.hypObj.classifyOne(rank, keySortedAllPvalues, allPvalues)
                        actionDecisions.append(dec)
                        
                        idxInSeq -= 1
                        
                    # now we have a list of decisions for the action at index=origIdx
                    # depending on the classification technique we pick only one decision out of the actionDecisions
                    finalDecision = self.aggregateDecisions(actionDecisions)
                    decisionsForOriginalSeq.append(finalDecision)
                               
                self.metricObj.update(decisionsForOriginalSeq, originalGoldMarkers)
                self.dumpDebuggingInfo(u, originalSeq, pValues, decisionsForOriginalSeq, originalGoldMarkers)
                
        self.metricObj.calculateStats()            
        if(len(self.debugPath) != 0):
            self.debugger.write('\n'+self.metricObj.getSummary())
            self.debugger.close()
                    
                            
        
        
    
    
    

def work():
       
    #ALPHA_NORANKING = np.arange(0.000005,0.1,0.005) # start=0, step=0.1, end=1 (exlusive)
    #ALPHA_RANKING = np.arange(0.000005,0.1,0.005)    
    
    
    ANALYSIS_FILES_PATH = '/home/mohame11/pins_repins_fixedcat/allLikes/pvalues_noWindow_log/'
    #ANALYSIS_FILES_PATH = '/home/mohame11/pins_repins_fixedcat/allLikes/pvalues_9gram/'
    FILE_NAME = 'outlier_analysis_pvalues_'
    
    print('>>> Reading Data ...')
    allData = TestSample.parseAnalysisFiles(FILE_NAME, ANALYSIS_FILES_PATH)
    
    NON_EXISTING_USERS_PATH = '/home/mohame11/pins_repins_fixedcat/allLikes/likes.trace_nonExistingUsers'
    nonExistingUsers = set()
    rr = open(NON_EXISTING_USERS_PATH, 'r')
    for line in rr:
        nonExistingUsers.add(line.strip())
    rr.close()
    for us in nonExistingUsers:
        allData.pop(us, None)
    print('>>> Evaluating ...')
    
    #actionAtBoundary = BOUNDARY.INCLUDE #NEED to BE ADDED
    
    #metricList = [METRIC.REC_PREC_FSCORE]
    metricList = [METRIC.BAYESIAN, METRIC.FISHER]
    #techList = [TECHNIQUE.ALL_OR_NOTHING,TECHNIQUE.MAJORITY_VOTING,TECHNIQUE.ONE_IS_ENOUGH]
    techList = [TECHNIQUE.MAJORITY_VOTING]
    #alphaList = [1e-20, 1e-15, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 2.0]
    alphaList = [1e-100, 1e-90, 1e-80, 1e-70, 1e-60, 1e-50, 1e-40, 1e-30, 1e-20, 1e-18, 1e-16, 1e-14, 1e-12, 1e-10, 5e-10, 1e-9, 5e-9, 1e-8, 5e-8, 1e-7, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1 ,0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 2.0]
    #alphaList= [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0]
    hypList = [HYP.EMPIRICAL]
    #hypList = [HYP.BONFERRONI, HYP.HOLMS]
    #pvalueList = [PVALUE.WITH_RANKING]
    #pvalueList = [PVALUE.WITHOUT_RANKING]
    pvalueList = [PVALUE.WITHOUT_RANKING, PVALUE.WITH_RANKING]
    testSetCountAdjustList = [False]
    
    #debugMode = True
    if(len(alphaList) == 0):
        metrics = []
        for pv in pvalueList:
            files = {}
            for metric in metricList:
                logger = open(ANALYSIS_FILES_PATH+str(metric)+'_'+str(pv),'w')
                files[metric] = logger
                if(metric == METRIC.CHI_SQUARE):
                    metricObj = Chisq()
                elif(metric == METRIC.REC_PREC_FSCORE):
                    metricObj = rpf()
                elif(metric == METRIC.FISHER):
                    metricObj = Fisher()
                elif(metric == METRIC.BAYESIAN):
                    metricObj = Bayesian()
                metrics.append(metricObj)
            print(metric, pv)
            ev = OutlierEvaluation(allData, TECHNIQUE.MAJORITY_VOTING, HYP.EMPIRICAL, None, pv, None, None)
            ev.evaluate_continousAlpha(metrics, files)
        
    else:
        for metric in metricList:
            for pv in pvalueList:
                logger = open(ANALYSIS_FILES_PATH+str(metric)+'_'+str(pv),'w')
                for alpha in alphaList:            
                    for tech in techList:                
                        for hyp in hypList:                                       
                            for tadj in testSetCountAdjustList:
                                
                                print(metric, pv,alpha,tech,hyp,tadj)
                                
                                #ev = OutlierEvaluation(allData, tech, hyp, metric, pv, alpha, tadj, ANALYSIS_FILES_PATH+'DEBUG_MODE_'+str(metric)+'_'+str(pv)+'_'+str(alpha))
                                ev = OutlierEvaluation(allData, tech, hyp, metric, pv, alpha, tadj)
                                ev.evaluate()   
                                
                                logger.write('alpha='+str(alpha))
                                logger.write(', '+str(tech))       
                                logger.write(', '+str(hyp))                                
                                logger.write(', TScountAdj='+str(tadj))
                                logger.write(': '+ev.metricObj.getSummary()+'\n')
                                logger.flush()
            logger.close()
        
        
  
    
if __name__ == "__main__":
    work()
    print('DONE!')
