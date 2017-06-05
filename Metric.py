'''
Created on Nov 23, 2016

@author: zahran
'''
from MyEnums import *
from scipy.stats import chisquare, fisher_exact
from scipy.stats.contingency import expected_freq, chi2_contingency
import numpy as np

class Metric:
    def __init__(self):
        self.type = None
        pass
    def update(self, decisions, goldMarkers):
        pass
    
    

class Chisq(Metric):    
    def __init__(self):  
        self.type = METRIC.CHI_SQUARE          
        self.OT = 0 #OT: Decision=outlier and friendship=True.
        self.OF = 0 
        self.NT = 0
        self.NF = 0 #NF: Decision=Normal  and friendship=False      
        self.expectedOT = 0
        self.expectedOF = 0
        self.expectedNT = 0
        self.expectedNF = 0
        self.stats = None
    
    def getSummary(self):
        myStr = 'OT='+str(self.OT)+', OF='+str(self.OF)+', NT='+str(self.NT)+', NF='+str(self.NF)+', stats='+str(self.stats)
        return myStr
        
    def update(self, decisions, goldMarkers):
        for i in range(len(decisions)):        
            if(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.TRUE):
                self.OT += 1        
            elif(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.FALSE):
                self.OF += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.TRUE):
                self.NT += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.FALSE):
                self.NF += 1
        
        ''' 
        row0 = self.OT + self.OF # no. of outliers
        row1 = self.NT + self.NF
        col0 = self.OT + self.NT
        col1 = self.OF + self.NF
        grandTotal = row0+row1
                
        self.expectedOT = float(row0*col0)/float(grandTotal)
        self.expectedOF = float(row0*col1)/float(grandTotal)
        self.expectedNT = float(row1*col0)/float(grandTotal)
        self.expectedNF = float(row1*col1)/float(grandTotal)
        
        self.stats = chisquare([self.OT, self.OF, self.NT, self.NF], f_exp=[self.expectedOT, self.expectedOF, self.expectedNT, self.expectedNF], ddof=2)
        #ci = chi2_contingency([self.OT, self.OF, self.NT, self.NF])
        
        #print(self.stats, oddsratio, pvalue)
        #print('myExpected:'+str([self.expectedOT, self.expectedOF, self.expectedNT, self.expectedNF]))
        #ep = expected_freq([self.OT, self.OF, self.NT, self.NF])
        #cm = np.array_equal(ep, np.array([self.expectedOT, self.expectedOF, self.expectedNT, self.expectedNF]))
        #print(cm)
        #if(not cm):       
        #    print('\nERROR in exp cnt\n')
        #print('\n')
        '''
                
    def calculateStats(self):
        row0 = self.OT + self.OF # no. of outliers
        row1 = self.NT + self.NF
        col0 = self.OT + self.NT
        col1 = self.OF + self.NF
        grandTotal = row0+row1
                
        self.expectedOT = float(row0*col0)/float(grandTotal)
        self.expectedOF = float(row0*col1)/float(grandTotal)
        self.expectedNT = float(row1*col0)/float(grandTotal)
        self.expectedNF = float(row1*col1)/float(grandTotal)
        
        self.stats = chisquare([self.OT, self.OF, self.NT, self.NF], f_exp=[self.expectedOT, self.expectedOF, self.expectedNT, self.expectedNF], ddof=2)
        
        
        

class Fisher(Metric):    
    def __init__(self):  
        self.type = METRIC.FISHER          
        self.OT = 0 #OT: Decision=outlier and friendship=True.
        self.OF = 0 
        self.NT = 0
        self.NF = 0 #NF: Decision=Normal  and friendship=False             
        self.stats = None
    
    def getSummary(self):
        myStr = 'OT='+str(self.OT)+', OF='+str(self.OF)+', NT='+str(self.NT)+', NF='+str(self.NF)+', stats='+str(self.stats)
        return myStr
        
    def update(self, decisions, goldMarkers):
        for i in range(len(decisions)):        
            if(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.TRUE):
                self.OT += 1        
            elif(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.FALSE):
                self.OF += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.TRUE):
                self.NT += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.FALSE):
                self.NF += 1
            
        
        #self.stats = [fisher_exact([[self.OT, self.OF], [self.NT, self.NF]])]
    
    def calculateStats(self):
        self.stats = [fisher_exact([[self.OT, self.OF], [self.NT, self.NF]])]
        
        
        
class rpf(Metric): #recall_precision_fscore
    def __init__(self): 
        self.type = METRIC.REC_PREC_FSCORE
        self.OT = 0 #OT: Decision=outlier and friendship=True. (tp)
        self.OF = 0 #fp
        self.NT = 0 #fn
        self.NF = 0 #NF: Decision=Normal  and friendship=False (tn)
        self.stats = None   
    
    def getSummary(self):
        myStr = 'OT='+str(self.OT)+', OF='+str(self.OF)+', NT='+str(self.NT)+', NF='+str(self.NF)+', stats='+str(self.stats)
        return myStr
    
    def update(self, decisions, goldMarkers):
        for i in range(len(decisions)):   
            if(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.TRUE):
                self.OT += 1        
            elif(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.FALSE):
                self.OF += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.TRUE):
                self.NT += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.FALSE):
                self.NF += 1
    '''
        try:         
            rec  = float(self.OT)/float(self.OT + self.NT) #tp/tp+fn
            prec = float(self.OT)/float(self.OT + self.OF)
            fscore= (2*prec*rec) / (prec+rec)
            self.stats = [rec, prec, fscore]
        except:
            self.stats = [0,0,0]
    '''
            
    def calculateStats(self):
        try:         
            rec  = float(self.OT)/float(self.OT + self.NT) #tp/tp+fn
            prec = float(self.OT)/float(self.OT + self.OF)
            fscore= (2*prec*rec) / (prec+rec)
            self.stats = [rec, prec, fscore]
        except:
            self.stats = [0,0,0]
        
    
    

class Bayesian(Metric):    
    def __init__(self):  
        self.type = METRIC.BAYESIAN          
        self.OT = 0 #OT: Decision=outlier and friendship=True.
        self.OF = 0 
        self.NT = 0
        self.NF = 0 #NF: Decision=Normal  and friendship=False             
        self.stats = None
        self.samplesCount = 5000
    
    def getSummary(self):
        myStr = 'OT='+str(self.OT)+', OF='+str(self.OF)+', NT='+str(self.NT)+', NF='+str(self.NF)+', stats='+str(self.stats)
        return myStr
        
    def update(self, decisions, goldMarkers):
        for i in range(len(decisions)):        
            if(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.TRUE):
                self.OT += 1        
            elif(decisions[i] == DECISION.OUTLIER and goldMarkers[i] == GOLDMARKER.FALSE):
                self.OF += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.TRUE):
                self.NT += 1
            elif(decisions[i] == DECISION.NORMAL and goldMarkers[i] == GOLDMARKER.FALSE):
                self.NF += 1
            
        
        #self.stats = [fisher_exact([[self.OT, self.OF], [self.NT, self.NF]])]
    
    def calculateStats(self):
        #trueCount_TgO = 0
        #trueCount_OT = 0
        #trueCount_full = 0
        P_Tprior = float(self.NT+self.OT) / float(self.OF+self.OT+self.NT+self.NF)
        P_Fprior = float(self.NF+self.OF) / float(self.OF+self.OT+self.NT+self.NF)
        
        #prior_scale = 0.00001
        #P_Tprior = float(self.NT+self.OT+1) *prior_scale
        #P_Fprior = float(self.NF+self.OF+1) *prior_scale
        
        #P_Tprior = float(self.NT+self.OT+1)
        #P_Fprior = float(self.NF+self.OF+1)
        
        #print 'P_T:', P_Tprior, 'P_F:', P_Fprior
        
        OT_post = self.OT + P_Tprior
        OF_post = self.OF + P_Fprior
        NT_post = self.NT + P_Tprior
        NF_post = self.NF + P_Fprior
        
        count_truePandN = 0
        for i in range(self.samplesCount):
            
            P_T = np.random.beta(self.OT+self.NT+P_Tprior, self.OF+self.NF+P_Fprior)
            #P_F = 1 - P_T
            
            #P_OgT = np.random.beta(OT_post, NT_post)
            #P_OgF = np.random.beta(OF_post, NF_post)
            
            #P_OT = P_OgT * P_T
            #P_OF = P_OgF * P_F
            #P_NT = (1 - P_OgT) * P_T
            #P_NF = (1 - P_OgF) * P_F
            
            P_TgO = np.random.beta(OT_post, OF_post)
            P_TgN = np.random.beta(NT_post, NF_post)
            
            TruePos = (P_TgO > P_T) + 0
            TrueNeg = (P_TgN < P_T) + 0
            #count_truePandN += (TruePos * TrueNeg)
            count_truePandN += (TruePos * TrueNeg)
            
            #if((P_OT*P_NF) > (P_OF*P_NT)):
            #    trueCount_full += 1
                
        #self.probTrue_full = float(trueCount_full) / float(self.samplesCount)
        self.probTrue_full = float(count_truePandN)/float(self.samplesCount)
        
        #self.stats = ['Full', self.probTrue_full]
        self.stats = ['Prob_of_significance', self.probTrue_full]
        
    
    def calculateStats_dirichelet(self):
        trueCount_TgO = 0
        trueCount_OT = 0
        trueCount_full = 0
        P_Tprior = float(self.NT+self.OT) / float(self.OF+self.OT+self.NT+self.NF)
        P_Fprior = float(self.NF+self.OF) / float(self.OF+self.OT+self.NT+self.NF)
        #print 'P_T:', P_T, 'P_F:', P_F
        
        self.OT_priorConst = 1.0
        self.OF_priorConst = 1.0
        self.NT_priorConst = 606.0
        self.NF_priorConst = 1.0
        
        P_OT_list = []
        P_OF_list = []
        P_NT_list = []
        P_NF_list = []
        
        for i in range(self.samplesCount):
            P_T = np.random.beta(self.OT+self.NT+P_Tprior, self.OF+self.NF+P_Fprior)
            P_F = 1 - P_T
            
            OT_post = self.OT + self.OT_priorConst * P_T  
            OF_post = self.OF + self.OF_priorConst * P_F 
            NT_post = self.NT + self.NT_priorConst * P_T 
            NF_post = self.NF + self.NF_priorConst * P_F
            
            P = np.random.dirichlet((OT_post, OF_post, NT_post, NF_post), 1)
            #P = np.random.dirichlet((self.OT+1, self.OF+1, self.NT+1), 1)
            P_OT = P[0][0]
            P_OF = P[0][1]
            P_NT = P[0][2]
            P_NF = P[0][3]
            
            P_OT_list.append(P_OT)
            P_OF_list.append(P_OF)
            P_NT_list.append(P_NT)
            P_NF_list.append(P_NF)
            
            P_O = P_OT + P_OF
            P_N = P_NT + P_NF
            P_TgO = P_OT / P_O
            P_TgN = P_NT / P_N
            P_T = P_OT + P_NT
            
            
            if((P_OT*P_NF) > (P_OF*P_NT)):
                trueCount_full += 1
            
            if(P_TgO > P_T):
            #if(P_TgO > P_T and P_TgN < P_T):
                trueCount_TgO += 1
            
            if(P_OT > (P_T*P_O)):
                trueCount_OT += 1
            
        
        self.probTrue_TgO = float(trueCount_TgO) / float(self.samplesCount)
        self.probTrue_OT = float(trueCount_OT) / float(self.samplesCount)
        self.probTrue_full = float(trueCount_full) / float(self.samplesCount)
        
        self.stats = ['Full', self.probTrue_full,'T|O', self.probTrue_TgO,'OT', self.probTrue_OT]
        
        #print 'P_OT:', sum(P_OT_list)/len(P_OT_list), 'P_OF:', sum(P_OF_list)/len(P_OF_list), 'P_NT:', sum(P_NT_list)/len(P_NT_list), 'P_NF:', sum(P_NF_list)/len(P_NF_list)
    

def main():
    b = Bayesian()
    
    #OT=0, OF=0, NT=15289, NF=38983091, stats=['Full', 0.0036, 'T|O', 0.0036, 'OT', 0.0036]
    b.OT = 5
    b.OF = 1139
    b.NT = 16
    b.NF = 195240
    b.calculateStats()
    #b.calculateStats()
    print(b.getSummary())
    
    print()
    
    #OT=15289, OF=38983091, NT=0, NF=0, stats=['Full', 0.9952, 'T|O', 0.9952, 'OT', 0.9952]
    b.OT = 5
    b.OF = 1139
    b.NT = 16
    b.NF = 195240
    b.calculateStats_dirichelet()
    #b.calculateStats()
    print(b.getSummary())
    
    #OT=15289, OF=38983091, NT=0, NF=0, stats=['Full', 0.9952, 'T|O', 0.9952, 'OT', 0.9952]
    b = Fisher()
    b.OT = 5
    b.OF = 1139
    b.NT = 16
    b.NF = 195240
    b.calculateStats()
    #b.calculateStats()
    print(b.getSummary())
    
main() 
#alpha=0.0005, TECHNIQUE.MAJORITY_VOTING, HYP.EMPIRICAL, TScountAdj=False: OT=534, OF=852289, NT=1703, NF=2419088, stats=['Prob_of_significance', 0.0008]

        
