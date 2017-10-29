'''
Created on Sep 19, 2017

@author: mohame11
'''
from DetectionTechnique import *
import sys
import math
import numpy as np
import os.path
sys.path.append('myCython/')
import pyximport; pyximport.install()
import cythonOptimize
import MyEnums
import gzip
import tables
import scipy
class TribeFlowpp (DetectionTechnique):
    def __init__(self):
        DetectionTechnique.__init__(self)
        self.type = SEQ_PROB.TRIBEFLOWPP
        self.hyper2id = {} #mapping users to ids
        self.obj2id = {} #mapping objects to ids
        self.Theta_zh = None #per user preference over envs
        self.Psi_zss = None #transition between objects for each env
        self.smoothedProbs = None
        self.trace_fpath = None
        self.STAT_FILE = None
        self.UNBIAS_CATS_WITH_FREQ = None
        
        self.userMappingsPath = None
        self.actionMappingsPath = None
    
    def loadModel(self):
        
        self.obj2id = {}
        self.id2obj = {}
        r = open(self.actionMappingsPath, 'r')
        for line in r:
            parts = line.split()
            self.obj2id[parts[0]] = int(parts[1])
            self.id2obj[int(parts[1])] =  parts[0]
        r.close()
        
        self.hyper2id = {}
        r = open(self.userMappingsPath, 'r')
        for line in r:
            parts = line.split()
            self.hyper2id[parts[0]] = int(parts[1])
        r.close()
        
        print('loading trace and model ...')
        trace, num_obj = self.load_trace(self.trace_fpath)
        self.model = self.load_model(self.model_path)
        
        #self.Theta_zh = np.zeros((10,1000)) 
        self.Theta_zh = self.model['P'][-1].T
        self.Theta_zh = np.array(self.Theta_zh, dtype = 'd').copy()
        print('Building transition matrix ...')
         
        #counts = self.get_counts_numpy_array(self.model, trace)}

        self.Psi_zss = self.get_counts_numpy_array(self.model, trace)

        a = self.model['param']['a']
        #a = 1.0
        '''
        self.Psi_zss = {}
        for env in counts:
            P = counts[env] + a #  Add the Dirichlet hyperparameter
            #print 'THIS LINE IS REMOVED FROM MEM ISSUES: P = (P.T / P.sum(axis=1)).T'
            P = (P.T / P.sum(axis=1)).T  #  Normalize rows
            self.Psi_zss[env] = P

        lst = [None]*len(self.Psi_zss)
        for e in self.Psi_zss:
            lst[e] = self.Psi_zss[e]
        self.Psi_zss = np.array(lst, dtype = 'd').copy()
        '''
        #for optimization
        #envs = counts.keys()
        #lst = [None]*len(envs)
        #for env in envs:
            #print 'add dirch'
        #    P = counts[env]
           # print 'normalize'
           # P = (P.T / P.sum(axis=1)).T
        #    del counts[env]
        #    print 'deleted',env
            
            #P = (P.T / P.sum(axis=1)).T  #  Normalize rows
        #    print 'save'
        #    lst[env] = P
        #print 'finished all envs'
        #self.Psi_zss = np.array(lst, dtype = 'd').copy()
        print 'finished loading model ...'
            
    
    def createTestingSeqFile(self, store):
        from_ = store['from_'][0][0]
        to = store['to'][0][0]
        trace_fpath = store['trace_fpath']
        Dts = store['Dts']
        winSize = Dts.shape[1]
        tpath = '/home/zahran/Desktop/tribeFlow/zahranData/pinterest/test_traceFile_win5'
        w = open(tpath,'w')
        r = open(trace_fpath[0][0],'r')
        
        cnt = 0
        for line in r:
            if(cnt > to):
                p = line.strip().split('\t')
                usr = p[winSize]
                sq = p[winSize+1:]
                w.write(str(usr)+'\t')
                for s in sq:
                    w.write(s+'\t')
                w.write('\n')
            cnt += 1
        w.close()
        r.close()
        return tpath         
        
    def calculatingItemsFreq(self, smoothingParam):
        self.smoothedProbs = {}    
        if os.path.isfile(self.STAT_FILE):
            r = open(self.STAT_FILE, 'r')
            for line in r:
                parts = line.strip().split('\t')               
                #print(parts, parts[1]) 
                #self.smoothedProbs[parts[0]] = math.log10(float(parts[1]))                    
                self.smoothedProbs[parts[0]] = float(parts[1]) 
            r.close()
            return
            
        
        freqs = {}            
        r = open(self.trace_fpath)
        counts = 0
        for line in r:
            cats = line.strip().split('\t')[self.true_mem_size+1:]
            for c in cats:
                if(c in freqs):
                    freqs[c] += 1
                else:
                    freqs[c] = 1                
                counts += 1
        for k in freqs:
            prob = float(freqs[k]+ smoothingParam) / float(counts + (len(freqs) * smoothingParam))
            self.smoothedProbs[k] = math.log10(prob)
        
        w = open(self.STAT_FILE, 'w')
        for key in self.smoothedProbs:
            w.write(key+'\t'+str(self.smoothedProbs[key])+'\n')
        w.close()
        #return self.smoothedProb                            

    def getProbability(self, userId, newSeq):
         
        '''
        a = self.model['param']['a'] #Dirch prior
        newSeqIds = [self.obj2id[s] for s in newSeq]  
        seqProb = 0.0
        #window = min(self.true_mem_size, len(newSeq))
        envCount = len(self.Psi_zss)
        logSeqProbZ = np.zeros(envCount, dtype='d').copy()
        for z in xrange(envCount): #for envs
            #print('self.Theta_zh', self.Theta_zh.shape)
            #print('envcount', envCount)
            #print('z',z,'userid',userId)
            seqProbZ = math.log10(self.Theta_zh[z, userId])    
            for i in range(0,len(newSeqIds)-1): 
                src = newSeqIds[i]
                dest = newSeqIds[i+1]
                norm = sum(self.Psi_zss[z][src])
                #print 'self.Psi_zss[z][src]=', self.Psi_zss[z][src].shape
                #print 'sum=',norm
                prob_s_d_in_z = float(self.Psi_zss[z][src][dest]+a) / float(norm + (len(self.Psi_zss[z][src])*a))
                seqProbZ += math.log10(prob_s_d_in_z)
            logSeqProbZ[z] = seqProbZ
        logSeqScore = cythonOptimize.getLogProb(logSeqProbZ, envCount)
        '''
        
        
        #cython
        a = self.model['param']['a']
        S = self.model["param"]["S"]
        newSeqIds = [self.obj2id[s] for s in newSeq]       
        newSeqIds_np = np.array(newSeqIds, dtype = 'i4').copy()
        logSeqProbZ = np.zeros(self.Theta_zh.shape[0], dtype='d').copy()
        logSeqScore = cythonOptimize.calculateSequenceProb_trpp(newSeqIds_np, len(newSeqIds_np), logSeqProbZ, userId, self.Theta_zh, self.Psi_zss, float(a), float(S))
        
    
        if(self.UNBIAS_CATS_WITH_FREQ):
            #unbiasingProb = 1.0
            logUnbiasingProb = 0 
            for ac in newSeq:
                if(ac in self.smoothedProbs):
                    #unbiasingProb *= self.smoothedProbs[ac]
                    logUnbiasingProb += self.smoothedProbs[ac]                                          
            #seqScore = float(seqScore)/float(unbiasingProb)  
            logSeqScore = logSeqScore - logUnbiasingProb
        #return seqScore
        return logSeqScore      
    
    def prepareTestSet(self):
        seqsCountWithNonExistingUsers = 0
        nonExistingUsers = set()
        testDic = {}
        print(">>> Tribeflowpp Preparing testset ...")
        print('window', self.useWindow)
        testSetCount = 0
        print(self.SEQ_FILE_PATH)
        r = open(self.SEQ_FILE_PATH, 'r')    
        for line in r:
            line = line.strip() 
            tmp = line.split()  
            actionStartIndex = 1
            user = tmp[0]   
            if(user not in self.hyper2id):
                #print("User: "+str(user)+" is not found in training set !")
                seqsCountWithNonExistingUsers += 1
                nonExistingUsers.add(user)
                continue
            if(self.VARIABLE_SIZED_DATA == True):
                if('###' not in tmp):
                    seq = tmp[actionStartIndex:]
                    goldMarkers = ['false']*len(seq)
                else:
                    indx = tmp.index('###')
                    seq = tmp[:indx]
                    goldMarkers = tmp[indx+1:]
            #print(seq,goldMarkers)
            else:
                seq = tmp[actionStartIndex:self.true_mem_size+2]
                goldMarkers = tmp[self.true_mem_size+2:]
                if(len(goldMarkers) != len(seq)):
                    goldMarkers = ['false']*len(seq)

            t = TestSample()  
            t.user = user
            t.actions = list(seq)
            t.goldMarkers = list(goldMarkers)   
            
            testSetCount += 1
            if(user in testDic):
                testDic[user].append(t)                                                    
            else:
                testDic[user]=[t]
            #print(testSetCount)
        r.close()
        #print(testDic, len(testDic))
        if(self.useWindow == USE_WINDOW.FALSE): # we need to use the original sequence instead of overlapping windows
            testSetCount = len(testDic)
            print('No overlapping window ... ')
            print('testDic len before fixing window', testSetCount)
            for u in testDic:
                tests = testDic[u]
                originalSeq, originalGoldMarkers = self.formOriginalSeq(tests)
                t = TestSample()  
                t.user = u
                t.actions = list(originalSeq)
                t.goldMarkers = list(originalGoldMarkers)   
                testDic[u] = [t]
        print 'seqsCountWithNonExistingUsers=',seqsCountWithNonExistingUsers
        print 'number of nonExistingUsers=',len(nonExistingUsers)
        #print nonExistingUsers
        ww = open(self.SEQ_FILE_PATH+'_nonExistingUsers', 'w')
        for us in nonExistingUsers:
            ww.write(str(us)+'\n')
        ww.close()
        print('#users', len(testDic))
        return testDic, len(testDic)
    
    def getAllPossibleActions(self):
        return self.obj2id.keys()  
        
    def getUserId(self, uid):
        return self.hyper2id[uid]  
    
    
    def load_trace(self, filename):
        traces = {}
        with gzip.open(filename, "rt") as source:
            for row in source:
                _, hypernode, object = row.strip().split("\t")
                hypernode = int(hypernode)
                object = int(object)
                if hypernode not in traces:
                    traces[hypernode] = []
                traces[hypernode].append(object)
        K = np.max([np.max(traces[u]) for u in traces]) + 1
        return traces, K

# -------------------------- #

    def load_model(self, filename):
        model = {}
    
        h5_file = tables.open_file(filename, "r")
    
        model['param'] ={}
        row = h5_file.root.params.read()[0]
        model['param']['N'] = row['NumHypernodes']
        model['param']['M'] = row['NumEnvironments']
        model['param']['S'] = row['NumStates']
        model['param']['a'] = row['a']
        model['param']['r'] = row['r']
        model['param']['s'] = row['s']
        model['param']['g'] = row['g']
        model['param']['q'] = row['q']
    
        model['P'] = h5_file.root.P.read()
        model['rho'] = h5_file.root.rho.read()
    
        model['C'] = {}
        model['J'] = {}
        model['E'] = {}
        for hn in range(model['param']['N']):
            name = 'HYPERNODE_{}'.format(hn)
            model['C'][hn] = h5_file.root._v_children[name].C.read()
            model['J'][hn] = h5_file.root._v_children[name].J.read()
            model['E'][hn] = h5_file.root._v_children[name].E.read()
    
        h5_file.close()
    
        return model
    
    
    # ==================================================== #

    def get_counts_numpy_array(self, model, trace):
        """
        Extract the count of transitions from the MCMC output
        :param model: the MCMC output
        :param trace: the observed data (traces)
        :return: a dictionary with the transition counts. counts[e][i][j] keeps the
        counts of transitions out of i into j while in environment e
        """
        N = model["param"]["N"]
        M = model["param"]["M"]
        S = model["param"]["S"]
        print 'Dirich: a=', self.model['param']['a']   
        #counts = {e: np.full((S, S), self.model['param']['a']) for e in range(M)}
        print 'Init counts'
        counts = {e: np.zeros((S, S)) for e in range(M)}
        #counts = {e: np.ones((S, S)) for e in range(M)}
        #counts = {e: scipy.sparse.csr_matrix((S, S)) for e in range(M)}
        print 'counts inited'
        for u in range(N):
            Z = trace[u]
            T = len(Z)
    
            C = np.concatenate([model['C'][u][-1], [T]])
            J = model['J'][u][-1]
            E = model['E'][u][-1]
    
            # The current jump (index in J)
            curr = 0
    
            # The index of the observation when the next jump occurs or the
            # index past the end of the trace, if there is no more jumps
            if curr + 1 < len(J):
                next_jump = C[J[curr + 1]]
            else:
                next_jump = T
    
            # The environment assigned to the transitions until the next jump
            env = E[curr]
    
            # We go through the trace, counting the transitions between jumps
            for t in range(1, T):
                # If we haven't got to the next jump yet, we must count the
                # current transition
                if t < next_jump:
                    z_from = Z[t - 1]
                    z_to = Z[t]
                    counts[env][z_from, z_to] += 1
                # If we get to the next jump, we don't count the transition,
                # but we update the indices and the environment to the next
                # stretch of the trace
                else:
                    curr += 1
                    if curr + 1 < len(J):
                        next_jump = C[J[curr + 1]]
                    else:
                        next_jump = T
                    env = E[curr]
    
        return counts

# -------------------------- #

    def get_counts_as_dict(self, model, trace):
        """
        Extract the count of transitions from the MCMC output
        :param model: the MCMC output
        :param trace: the observed data (traces)
        :return: a dictionary with the transition counts. counts[e][i][j] keeps the
        counts of transitions out of i into j while in environment e
        """
        N = model["param"]["N"]
        M = model["param"]["M"]
        S = model["param"]["S"]
    
        # Get the dense counts
        # counts = {e: np.zeros(S, S) for e in range(M)}
        # Or a sparse dictionary version of counts
        counts = {e: {} for e in range(M)}
    
        for u in range(N):
            Z = trace[u]
            T = len(Z)
    
            C = np.concatenate([model['C'][u][-1], [T]])
            J = model['J'][u][-1]
            E = model['E'][u][-1]
    
            # The current jump (index in J)
            curr = 0
    
            # The index of the observation when the next jump occurs or the
            # index past the end of the trace, if there is no more jumps
            if curr + 1 < len(J):
                next_jump = C[J[curr + 1]]
            else:
                next_jump = T
    
            # The environment assigned to the transitions until the next jump
            env = E[curr]
    
            # We go through the trace, counting the transitions between jumps
            for t in range(1, T):
                # If we haven't got to the next jump yet, we must count the
                # current transition
                if t < next_jump:
                    z_from = Z[t - 1]
                    z_to = Z[t]
                    if z_from not in counts[env]: counts[env][z_from] = {}
                    if z_to not in counts[env][z_from]: counts[env][z_from][z_to] = 0
                    counts[env][z_from][z_to] += 1
                # If we get to the next jump, we don't count the transition,
                # but we update the indices and the environment to the next
                # stretch of the trace
                else:
                    curr += 1
                    if curr + 1 < len(J):
                        next_jump = C[J[curr + 1]]
                    else:
                        next_jump = T
                    env = E[curr]
    
        return counts

    def simulatedSeq(self, uid, size):
        seq = []
        candidates = []
        for i in range(size):
            cand = np.random.binomial(1, p=self.model['param']['q'])
            if(cand == 1):
                candidates.append(i)
                
        u_z = self.Theta_zh[:,uid]
        u_z = u_z / sum(u_z)
        #numpy.random.choice(a, size=None, replace=True, p=None)
        #replace =True. i.e. put back the sampled item to the space
        #replace =False. i.e. once picked, it's removed and thus affecting the probability of the remainging items
        currEnv = np.random.choice(list(range(0,self.Theta_zh.shape[0])), 1, replace =True, p=u_z)[0]
        currAction = np.random.choice(list(range(0,self.model['param']['S'] )))     #self.model['param']['S']
        seq.append(self.id2obj[currAction])
        newAction = currAction
        newEnv = currEnv
        for i in range(1, size):
            if(i in candidates):
                pz = np.random.beta(self.model['param']['r'], self.model['param']['s']) #pz: Beta(r,s)
                rd = np.random.random()
                if(rd <= pz):
                    
                    while(newEnv == currEnv):
                        newEnv = np.random.choice(list(range(0,self.Theta_zh.shape[0])), 1, replace =True, p=u_z)[0]
                    currEnv = newEnv
                        
            
            ss = self.Psi_zss[currEnv]
            #s = ss[currAction] 
            s = ss[currAction] + self.model['param']['a']
            s = s / sum(s) 
            while(newAction == currAction):
                newAction = np.random.choice(list(range(0,self.model['param']['S'] )), 1, replace =True, p=s)[0]
            
            seq.append(self.id2obj[newAction])
            currAction = newAction
            
                
        return seq

def formOriginalSeq(tests):
    origSeq = list(tests[0].actions)  
    if(len(tests) <= 1):
        return origSeq
    for i in range(1,len(tests)):
        a = tests[i].actions[-1]
        origSeq.append(a)           
    return origSeq

def getUserTrajectoryLengths(trainPath):
    userTrajLen = {}
    testDic = {}
    print(">> Reading training set ...")
    testSetCount = 0
    r = open(trainPath, 'r')    
    for line in r:
        line = line.strip() 
        tmp = line.split()  
        actionStartIndex = 10
        
        user = tmp[9]   
        
        seq = tmp[actionStartIndex :]

        t = TestSample()  
        t.user = user
        t.actions = list(seq)  
        
        testSetCount += 1
        if(user in testDic):
            testDic[user].append(t)                                                    
        else:
            testDic[user]=[t]
    r.close()

    testSetCount = len(testDic)
    for u in testDic:
        tests = testDic[u]
        originalSeq = formOriginalSeq(tests)
        userTrajLen[u] = len(originalSeq)
    
    return userTrajLen  

def simulateData():
    THE_PATH = '/u/scratch1/mohame11/lastFm/'
    trpp = TribeFlowpp()
    trpp.actionMappingsPath = THE_PATH + 'lastfm_win10_trace_tribeflowpp_actionMappings'
    trpp.userMappingsPath = THE_PATH + 'lastfm_win10_trace_tribeflowpp_userMappings'
    trpp.model_path = THE_PATH + 'lastfm_win10_trace_tribeflowpp_model/lastfm_win10_trace_tribeflowpp_model.mcmc'
    trpp.trace_fpath = THE_PATH + 'lastfm_win10_trace_tribeflowpp.tsv.gz'

    outputFile = THE_PATH + 'simulatedData/trpp9_www_simData_perUser20'
    #print(outputFile)
    w = open(outputFile, 'w')
    trpp.loadModel()
    
    TRAIN_PATH = THE_PATH + 'lastfm_win10_trace'
    userTrajLen = getUserTrajectoryLengths(TRAIN_PATH)
    for u in userTrajLen:
        userTrajLen[u] = 20
    
    print('Simulated data ...')
    cnt = 0
    for u in trpp.hyper2id:
        print(cnt, len(trpp.hyper2id))
        seq = trpp.simulatedSeq(trpp.hyper2id[u], userTrajLen[u])
        w.write(str(u)+' '+' '.join(seq) + '\n')
        w.flush()
        cnt += 1
    w.close()   
    
            
        
    

def experiments():
    '''
    in the sample example
    #objects (actions) = 1000
    #envs = 100
    #users = 10
    model['P'].shape = 11,100,10 #all user preference samples
    model['P'][-1].shape = 100,10 #the last sampled user preference vector
    S is the #objects, so the transition matrix should be SxS matrix
    a is the dirichelet param
    counts is M matrices of size S x S (M=10, S=1000). I.e. counts[0].shape = 1000x1000
    tr_matrices is a dic. key is an env, value is a 1000x1000 trans matrix of that env    
    '''
    #cythonOptimize.getLogProb([1,2,3],3)
    trpp = TribeFlowpp()
    # Read training trace file and MCMC output
    trace, num_obj = trpp.load_trace("/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/tribeflowpp/example/traces.tsv.gz")
    model = trpp.load_model("/Users/mohame11/Documents/myFiles/Career/Work/Purdue/PhD_courses/projects/tribeflowpp/example/output.mcmc")

    # You can access the user preference over environment:
    last_sampled_user_pref = model['P'][-1]
    print("User preference over environments: ({} x {} matrix)\n{}".format(model['param']['N'], model['param']['M'], last_sampled_user_pref))

    S = model['param']['S']
    print("Num obj: {}, S = {}. These should be the same!".format(num_obj, S))

    print("Computing transition counts...")
    # This gets the counts as M matrices of size S x S
    # M is the number of environments
    # S is the states space (number of possible items)
    counts = trpp.get_counts_numpy_array(model, trace)

    # The next code computes the point estimate (expected value)
    # of the transition probability matrices, using the transition counts
    # according to the last sampled environment assignment
    print("Computing point estimate of the transition matrix")
    a = model['param']['a']
    tr_matrices = {}
    for env in counts:
        P = counts[env] + a #  Add the Dirichlet hyperparameter
        P = (P.T / P.sum(axis=1)).T  #  Normalize rows
        #la place smoothing
        alpha = 1.0
        P = ( (P.T+alpha) / (P.sum(axis=1)+S) ).T  #  Normalize rows
        tr_matrices[env] = P
    
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            print P[i][j],',',
        print 'row sum=', sum(P[i:])
        
                

    print("Getting environment of last observation of each user (in the last MCMC sample)")
    # The first [-1] is to pick the last MCMC sample, the second [-1] is to pick
    # the environment of the last item
    last_envs = {u: model['E'][u][-1][-1] for u in range(model['param']['N'])}
    
    print('..')

    

    
    
if __name__ == "__main__": 
    #experiments()
    simulateData()
    
    
    
     
        
