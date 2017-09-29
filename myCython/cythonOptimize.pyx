from cython import boundscheck, wraparound
cdef extern from "<math.h>" nogil:
    double log10(double x)
    double pow(double x, double y)

'''
def get_norm_from_logScores(logScores):
    if(len(logScores) == 1):
        return logScores[0]
    pw = (-1)*logScores[0] + get_norm_from_logScores(logScores[1:])
    return logScores[0]+math.log10(1+math.pow(10,pw))
'''

@boundscheck(False)
cpdef double getLogProb(double[:] logProbs, int listLen) nogil:
    cdef double pw = 0.0
    cdef double res = 0.0
    if(listLen == 1):
        return logProbs[0]
    
    pw = (-1)*logProbs[0] + getLogProb(logProbs[1:], (listLen-1))
    if(pw<100):
        res = logProbs[0]+log10(1+(pow(10,pw)))
    else:
        res = logProbs[0]+pw
    '''
    try:
        res = logProbs[0]+log10(1+(pow(10,pw))) #this sometimes can cause overflow
    except:
        res = logProbs[0]+pw #an approximation that log10(1+x)=log10(x), where x is a very large number
    '''
    
    return res

@boundscheck(False)
cpdef double evaluate(int userId, int[:] history, int historyLen, int targetObjId, double[:, ::1] Theta_zh, double[:, ::1] Psi_sz, int env) nogil:        
    cdef double mem_factor = 0.0    
    cdef double candidateProb = 0.0    
    cdef int j = 0
    for j in xrange(historyLen):#for all B
        #i.e. multiply all psi[objid1,z]*psi[objid2,z]*..psi[objidB,z]
        mem_factor += log10(Psi_sz[history[j], env]) # Psi[objId, env z]            
    #mem_factor *= 1.0 / (1 - Psi_sz[history[len(history)-1], env])# 1-Psi_sz[mem[B-1],z] == 1-psi_sz[objIdB,z]       
    candidateProb = mem_factor + log10(Psi_sz[targetObjId, env]) + log10(Theta_zh[env, userId])                                              
    return candidateProb

@boundscheck(False)
cpdef double calculateSequenceProb(int[:] theSequence, int theSequenceLen, double[:] logSeqProbZ, int true_mem_size, int userId, double[:, ::1] Theta_zh, double[:, ::1] Psi_sz) nogil:                     
    cdef double seqProb = 0.0   
    cdef double seqProbZ = 1.0    
    cdef int targetObjId = -1
    cdef double prior = 0.0
    cdef double candProb = 0.0
    cdef int window = 0   
    #cdef int[:] history = np.zeros(theSequenceLen, dtype='i4')
    cdef int[:] history
    cdef int historyLen = 0
    cdef int targetObjIdx, z, i = 0
    cdef int wmax = 0
   
    window = min(true_mem_size, theSequenceLen)
    for z in xrange(Psi_sz.shape[1]): #for envs
        seqProbZ = 0.0        
        for targetObjIdx in range(0,theSequenceLen): #targetObjIdx=0 cannot be predicted we have to skip it
            if(targetObjIdx == 0):                
                targetObjId = theSequence[targetObjIdx]                            
                prior = Psi_sz[targetObjId, z]
                seqProbZ += log10(prior)
            else:                                                                            
                targetObjId = theSequence[targetObjIdx]      
                wmax = max(0,targetObjIdx-window)           
                history = theSequence[wmax: targetObjIdx] # look back 'window' actions.                                                            
                historyLen = targetObjIdx-wmax                            
                candProb = evaluate(userId, history, historyLen, targetObjId, Theta_zh, Psi_sz, z) #(int[:, ::1] HOs, double[:, ::1] Theta_zh, double[:, ::1] Psi_sz, int[::1] count_z, int env):                                
                seqProbZ += candProb
        logSeqProbZ[z] = seqProbZ             
        #seqProb += seqProbZ
    #return logSeqProbZ  
    return getLogProb(logSeqProbZ, Psi_sz.shape[1])   


@boundscheck(False)
cpdef double calculateSequenceProb_trpp(int[:] theSequence, int theSequenceLen, double[:] logSeqProbZ, int userId, double[:, :] Theta_zh, double[:, :, :] Psi_zss) nogil:
    cdef int envCount = Theta_zh.shape[0]  
    cdef double seqProbZ = 0.0   
    cdef int src = -1
    cdef int dest = -1
    cdef double prob = 0.0
    cdef int nexti = 0
    cdef int oneLessSeqLen = theSequenceLen - 1
    cdef int i,z = 0
    for z in xrange(envCount):  
        seqProbZ = log10(Theta_zh[z, userId])      
        for i in range(0, oneLessSeqLen):
            nexti = i+1
            src = theSequence[i]
            dest = theSequence[nexti]
            prob = Psi_zss[z, src, dest]
            seqProbZ += log10(prob)
        logSeqProbZ[z] = seqProbZ
    return getLogProb(logSeqProbZ, envCount) 
    
    

 
