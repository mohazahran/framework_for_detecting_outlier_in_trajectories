'''
Created on Nov 27, 2016

@author: Mohamed Zahran
'''
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

#plt.ion()
import numpy as np
from math import log

import sys 
sys.path.append('../')
#sys.path.append('/Users/mohame11/anaconda/lib/python2.7/site-packages/')
from MyEnums import *

class MyPlot():

    def __init__(self, tag, path, metric, figs, smallestAlpha):
        self.tag = tag
        self.path = path
        self.metric = metric        
        self.mapping = {}
        self.x = []
        self.figs = figs
        self.smallestAlpha = smallestAlpha
        self.parse()       
    
    def parse(self):
        r = open(self.path, 'r')
        for line in r:
            parts = line.split(':')
            params = parts[0].split(', ')
            results = parts[-1].replace(')','').replace('(','').split(', ')
            
            config = ', '.join(params[1:])
            alpha = float(params[0].split('=')[-1])
            if(alpha < self.smallestAlpha):
                continue
            if(alpha not in self.x):
                self.x.append(alpha)
                
            if(self.metric == METRIC.CHI_SQUARE):  
                res = float(results[-1].split('=')[-1])  
                              
            elif(self.metric == METRIC.FISHER):  
                res = float(results[-1].split('=')[-1].replace(']',''))
                                            
            elif(self.metric == METRIC.RECALL):
                res = float(results[-3].split('=')[-1].replace('[',''))
                
            elif(self.metric == METRIC.PRECISION):
                res = float(results[-2])
                
            elif(self.metric == METRIC.FSCORE):
                res = float(results[-1].split('=')[-1].replace(']',''))
                
            elif(self.metric == METRIC.ACCURACY):
                tp=float(results[0].split('=')[-1])
                fp=float(results[1].split('=')[-1])
                fn=float(results[2].split('=')[-1])
                tn=float(results[3].split('=')[-1])
                res = (tp+tn)/(tp+tn+fp+fn)
                
            elif(self.metric == METRIC.TRUE_NEGATIVE_RATE):
                tp=float(results[0].split('=')[-1])
                fp=float(results[1].split('=')[-1])
                fn=float(results[2].split('=')[-1])
                tn=float(results[3].split('=')[-1])
                res = tn/(tn+fp)
            
            if(config not in self.mapping):                
                self.mapping[config] = {alpha:res}
            else:
                self.mapping[config][alpha] = res
        
        
        r.close()
    
    def plot(self):       
        plt.rc('legend',**{'fontsize':13})
        for i in range(len(self.figs)):
            plt.figure(i)
            plt.xlabel('Alpha')
            plt.ylabel(str(self.metric))
            plt.xticks([log(x,10) for x in self.x])  
            
            #plt.legend(loc='upper right')   
                             
            #plt.title(self.figs[i])                      
            figConfigSet = {}               
            for cf in self.mapping:
                if(self.figs[i] in cf):
                    if('TScountAdj=True' in cf):
                        continue
                    figConfigSet[cf] = []
                
            for x in self.x:    
                for cf in figConfigSet:                    
                    figConfigSet[cf].append(self.mapping[cf][x])
            
            lgx = [log(x,10) for x in self.x]
            flg = True
            for cf in figConfigSet:                                                          
#                 if(flg):                                                                                                           
#                     lines = plt.plot(lgx, figConfigSet[cf], '--r', label=cf)
#                     flg = False
#                 else:
#                     lines = plt.plot(lgx, figConfigSet[cf], 'b', label=cf)
                
                lines = plt.plot(lgx, figConfigSet[cf], label=cf)
                plt.setp(lines, linewidth=2.0)  
                plt.legend(bbox_to_anchor=(0., 1.00, 1.00, .101), loc=3, ncol=1, mode="expand", borderaxespad=0.)
                #lines = plt.plot(lgx, figConfigSet[cf], label=cf)                                                            
                
        plt.show()
    
       
    @staticmethod
    def fusePlots(allPlots, useLog=True, my_yaxis_label='', savedFigFileName = 'foo.pdf'):
        plt.rc('legend',**{'fontsize':10})        
        plt.figure(0)
        plt.ylabel(my_yaxis_label)
        if(useLog):
            plt.xticks([log(x,10) for x in allPlots[0].x])
            plt.xlabel('log10(Alpha 1)')
        else:
            plt.xticks([x for x in allPlots[0].x])
            plt.xlabel('Alpha 1')  
        
        
        
        flg = 0 
        for p in allPlots:
            figConfigSet = {}               
            for cf in p.mapping:                
                if(p.figs[0] in cf):
                    if('TScountAdj=True' in cf or 'HOLMS' in cf):
                        continue
                    figConfigSet[cf] = []
            
              
            for x in p.x:    
                for cf in figConfigSet:                    
                    figConfigSet[cf].append(p.mapping[cf][x])
            
            if(useLog):
                lgx = [log(x,10) for x in p.x]
            else:
                lgx = [x for x in  p.x]     
                
            
            for cf in figConfigSet:   
                if(len(allPlots) == 2):
                    if(flg == 0):
                        #lines = plt.plot(lgx, figConfigSet[cf], '--r', label=p.tag+'_'+cf)
                        #lines = plt.plot(lgx, figConfigSet[cf], '--r', label='Simulated data: True negative rate')
                        lines = plt.plot(lgx, figConfigSet[cf], '--r', label='Tribeflow')
                        flg = 1
                    else:
                        lines = plt.plot(lgx, figConfigSet[cf], 'b', label='Ngram LM')
                        #lines = plt.plot(lgx, figConfigSet[cf], 'b', label='Likes trajectories: Fisher\'s test pvalue')
                        #lines = plt.plot(lgx, figConfigSet[cf], 'b', label=p.tag+'_'+cf)
                else:                                                                     
                    lines = plt.plot(lgx, figConfigSet[cf], label=p.tag+'_'+cf)
                    
                plt.setp(lines, linewidth=2.0)  
                plt.legend(bbox_to_anchor=(0., 1.00, 1.00, .101), loc=3, ncol=2, mode="expand", borderaxespad=0., prop={'size':5}) #legend font size
                
                axes = plt.gca()
                #axes.set_xlim([-10,0.01])
                axes.set_ylim([-0.1,1.1])
                plt.yticks(list(np.arange(-0.1, 1.1, 0.1)))
                
                #add a line at y=0.05 (Alpha2)
                lines = plt.plot(lgx, [0.05 for x in lgx], ':g', label='Alpha2')
                                                                                        
        #plt.savefig(savedFigFileName, bbox_inches='tight')
        plt.show()
        
            
        
            
        


def main():
    mpl.rcParams.update({'font.size': 14})
    
    smallestAlpha = -1
    
    lastFm_path = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/lastFm/'
    pins_win10_path = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win10/'
    pins_win4_path = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/pins_repins_fixedcat/win4/'
    
    resultsPath = '/Users/mohame11/Documents/newResults/'
    
    #tribeflow win 10
    '''
    pins10_sim = pins_win10_path+'tribeflow/'+'pins_repins_simulatedData_5perUser_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'    
    allLikes10_fisher = pins_win10_path+'tribeflow/'+'allLikes_METRIC.FISHER_PVALUE.WITHOUT_RANKING'
    allLikes10_chisq = pins_win10_path+'tribeflow/'+'allLikes_METRIC.CHI_SQUARE_PVALUE.WITHOUT_RANKING'
    '''
    #without ranking
    tr9_likes = resultsPath+'tribeflow9/'+'pins_repins_tribeflow9_noWin_log_allLikes_METRIC.FISHER_PVALUE.WITHOUT_RANKING'
    tr9_sim = resultsPath+'tribeflow9/'+'pins_repins_tribeflow9_noWin_log_simData_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    tr9_injSim = resultsPath+'tribeflow9/'+'pins_repins_tribeflow9_noWin_log_simInjectedData_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    
    #with ranking
    #tr9_likes = resultsPath+'tribeflow9/'+'pins_repins_tribeflow9_noWin_log_allLikes_METRIC.FISHER_PVALUE.WITH_RANKING'
    #tr9_sim = resultsPath+'tribeflow9/'+'pins_repins_tribeflow9_noWin_log_simData_METRIC.REC_PREC_FSCORE_PVALUE.WITH_RANKING'
    #tr9_injSim = resultsPath+'tribeflow9/'+'pins_repins_tribeflow9_noWin_log_simInjectedData_METRIC.REC_PREC_FSCORE_PVALUE.WITH_RANKING'
    
    #p1 = MyPlot('tr9_likes', tr9_likes, METRIC.FISHER, [str(TECHNIQUE.MAJORITY_VOTING)])
    #p2 = MyPlot('tr9_sim', tr9_sim, METRIC.TRUE_NEGATIVE_RATE, [str(TECHNIQUE.MAJORITY_VOTING)])
    #p3 = MyPlot('tr9_injSim', tr9_injSim, METRIC.FSCORE, [str(TECHNIQUE.MAJORITY_VOTING)])
    #MyPlot.fusePlots([p1 , p2, p3], useLog=True, my_yaxis_label = 'True negative rate / Fisher\'s test pvalue', savedFigFileName = 'tr9.pdf')
    
    #tribeflow win 4
    pins4_sim = pins_win4_path +'tribeflow/'+'pins_repins_win4_simData_new_1perBurst_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    allLikes_fisher_win4 = pins_win4_path+'tribeflow/'+'allLikes_win4_METRIC.FISHER_PVALUE.WITHOUT_RANKING'
    
    #p3 = MyPlot('pins4_sim', pins4_sim, METRIC.TRUE_NEGATIVE_RATE, [str(TECHNIQUE.ALL_OR_NOTHING)])
    #p4 = MyPlot('allLikes_fisher_win4', allLikes_fisher_win4, METRIC.FISHER, [str(TECHNIQUE.ALL_OR_NOTHING)])
    #MyPlot.fusePlots([p3 , p4], useLog=True, my_yaxis_label = 'True negative rate / Fisher\'s test pvalue', savedFigFileName = 'tr_burst4_bon_AND.pdf')
    
    #3gram win4
    allLikes_fisher_4gramLM = pins_win4_path + 'ngram/'+ 'pins_repins_3gram_allLikes_log_allActions_noWin_METRIC.FISHER_PVALUE.WITHOUT_RANKING'
    pins_sim_norank_4gram = pins_win4_path+ 'ngram/'+'pins_repins_3gram_sim_log_allActions_noWin_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    #pins_sim_rank_4gram = pins_win4_path+ 'pins_repins_simulatedData_4gram_noWindow_logprob_METRIC.REC_PREC_FSCORE_PVALUE.WITH_RANKING'
    
    #p5 = MyPlot('pins_sim_norank_4gram', pins_sim_norank_4gram, METRIC.TRUE_NEGATIVE_RATE, [str(TECHNIQUE.MAJORITY_VOTING)])
    #p6 = MyPlot('allLikes_fisher_4gramLM', allLikes_fisher_4gramLM, METRIC.FISHER, [str(TECHNIQUE.MAJORITY_VOTING)])
    #MyPlot.fusePlots([p5 , p6], useLog=True, my_yaxis_label = 'True negative rate / Fisher\'s test pvalue', savedFigFileName = 'ngram_burst4_bon_noRank.pdf')
    
    #9gram win10
    pins_sim_norank_9gram = pins_win10_path+'ngram/'+'pins_repins_simulatedDate_9gram_log_allActions_noWin_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    allLikes_fisher_9gramLM = pins_win10_path+'ngram/'+'pins_repins_allLikes_9gram_log_allActions_noWin_METRIC.FISHER_PVALUE.WITHOUT_RANKING'
    #pins_sim_rank_9gram = pins_win4_path+ 'pins_repins_simulatedData_4gram_noWindow_logprob_METRIC.REC_PREC_FSCORE_PVALUE.WITH_RANKING'
    
    #p7 = MyPlot('pins_sim_norank_9gram', pins_sim_norank_9gram, METRIC.TRUE_NEGATIVE_RATE, [str(TECHNIQUE.MAJORITY_VOTING)])
    #p8 = MyPlot('allLikes_fisher_9gramLM', allLikes_fisher_9gramLM, METRIC.FISHER, [str(TECHNIQUE.MAJORITY_VOTING)])
    #MyPlot.fusePlots([p7 , p8], useLog=True, my_yaxis_label = 'True negative rate / Fisher\'s test pvalue', savedFigFileName = 'ngram_burst10_bon_noRank.pdf')
    
    
    #rnnlm3
    smallestAlpha = 0.0001
    rnn3_likes = resultsPath+'rnnlm3/'+'pins_repins_rnnlm3_noWin_log_allLikes_METRIC.FISHER_PVALUE.WITHOUT_RANKING'
    rnn3_sim = resultsPath+'rnnlm3/'+'pins_repins_rnnlm3_noWin_log_simData_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    rnn3_injSim = resultsPath+'rnnlm3/'+'pins_repins_rnnlm3_noWin_log_simInjectedData_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    '''
    rnn3_likes = resultsPath+'rnnlm3/'+'pins_repins_rnnlm3_noWin_log_allLikes_METRIC.FISHER_PVALUE.WITH_RANKING'
    rnn3_sim = resultsPath+'rnnlm3/'+'pins_repins_rnnlm3_noWin_log_simData_METRIC.REC_PREC_FSCORE_PVALUE.WITH_RANKING'
    rnn3_injSim = resultsPath+'rnnlm3/'+'pins_repins_rnnlm3_noWin_log_simInjectedData_METRIC.REC_PREC_FSCORE_PVALUE.WITH_RANKING'
    '''
    
    p1 = MyPlot('rnn3_likes', rnn3_likes, METRIC.FISHER, [str(TECHNIQUE.MAJORITY_VOTING)], smallestAlpha)
    p2 = MyPlot('rnn3_sim', rnn3_sim, METRIC.TRUE_NEGATIVE_RATE, [str(TECHNIQUE.MAJORITY_VOTING)], smallestAlpha)
    p3 = MyPlot('rnn3_injSim', rnn3_injSim, METRIC.FSCORE, [str(TECHNIQUE.MAJORITY_VOTING)], smallestAlpha)
    MyPlot.fusePlots([p1 , p2, p3], useLog=False, my_yaxis_label = 'True negative rate / Fisher\'s test pvalue', savedFigFileName = 'rnn3.pdf')
    
    
    ########################################################################
    unixdata_win10_path = '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/UNIX_user_data/win10/'
    unixdata_win4_path =  '/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/outlierDetection/UNIX_user_data/win4/'
    
    #win10
    tribeflow_win10_simInj = unixdata_win10_path + 'tribeflow/' + 'unixdata_tribeflow_win10_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    ngram_win10_simInj = unixdata_win10_path + 'ngram/' + 'unixdata_9gram_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    
    #p9 =  MyPlot('tribeflow_win10_simInj', tribeflow_win10_simInj, METRIC.FSCORE, [str(TECHNIQUE.MAJORITY_VOTING)])
    #p10 = MyPlot('ngram_win10_simInj', ngram_win10_simInj, METRIC.FSCORE, [str(TECHNIQUE.MAJORITY_VOTING)])  
    #MyPlot.fusePlots([p9 , p10], useLog=True, my_yaxis_label = 'F1 score', savedFigFileName = 'unixdata_simInj_win10.pdf')
    
    
    
    #win4
    tribeflow_win4_simInj = unixdata_win4_path + 'tribeflow/' + 'unixdata_tribeflow4_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    ngram_win4_simInj = unixdata_win4_path + 'ngram/' + 'unixdata_ngram3_METRIC.REC_PREC_FSCORE_PVALUE.WITHOUT_RANKING'
    
    #p11 =  MyPlot('tribeflow_win4_simInj', tribeflow_win4_simInj, METRIC.FSCORE, [str(TECHNIQUE.MAJORITY_VOTING)])
    #p12 = MyPlot('ngram_win4_simInj', ngram_win4_simInj, METRIC.FSCORE, [str(TECHNIQUE.MAJORITY_VOTING)])  
    #MyPlot.fusePlots([p11 , p12], useLog=True, my_yaxis_label = 'F1 score', savedFigFileName = 'unixdata_simInj_win4.pdf')
    
    

    print('Done !')
      
    
main()
