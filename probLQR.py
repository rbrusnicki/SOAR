#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 16:53:22 2018

@author: levi

A module for testing the MSGRA formulation with LQR problems.
"""

import numpy
from sgra import sgra
from itsme import problemConfigurationSGRA
import matplotlib.pyplot as plt

class problemConfigurationSGRA2(problemConfigurationSGRA):
    def dyn(self):
        """Dynamics parameters."""

        section = 'dyn'
        self.con['auto1'] = self.config.getfloat(section, 'auto1')
        self.con['auto2'] = self.config.getfloat(section, 'auto2')

    def restr(self):
        """Restriction parameters."""
        section = 'restr'
        self.con['start1'] = self.config.getfloat(section,'start1')
        self.con['start2'] = self.config.getfloat(section,'start2')
        self.con['finish1'] = self.config.getfloat(section,'finish1')
        self.con['finish2'] = self.config.getfloat(section,'finish2')

    def cost(self):
        """Cost function parameters."""
        section = 'cost'
        self.con['contCostWeig'] = self.config.getfloat(section,'contCostWeig')


class prob(sgra):
    probName = 'probLQR'

    def loadParsFromFile(self,file):
        pConf = problemConfigurationSGRA2(fileAdress=file)
        pConf.sgra()
        pConf.dyn()
        pConf.restr()
        pConf.cost()

        N = pConf.con['N']
        tolP = pConf.con['tolP']
        tolQ = pConf.con['tolQ']
        k = pConf.con['gradStepSrchCte']

        self.tol = {'P': tolP,
                    'Q': tolQ}
        self.constants['gradStepSrchCte'] = k

        self.constants['auto1'] = pConf.con['auto1']
        self.constants['auto2'] = pConf.con['auto2']
        self.constants['contCostWeig'] = pConf.con['contCostWeig']

        self.restrictions = {'start1': pConf.con['start1'],
                             'start2': pConf.con['start2'],
                             'finish1':pConf.con['finish1'],
                             'finish2':pConf.con['finish2']}
        self.N = N

        self.dt = 1.0/(N-1)
        self.t = numpy.linspace(0,1.0,N)

    def initGues(self,opt={}):

        # The parameters that go here are the ones that cannot be simply
        # altered from an external configuration file... at least not
        # without a big increase in the complexity of the code...

        n = 2
        m = 1
        p = 1
        q = 4
        s = 1
        self.n = n
        self.m = m
        self.p = p
        self.q = q
        self.s = s
        self.Ns = 2*n*s + p

        initMode = opt.get('initMode','default')
        if initMode == 'default':
            # matrix sizes
            self.log.printL("InitGues in default: Not implemented yet!")
#            N = 2000+1#20000+1#2000+1
#
#            self.N = N
#
#            dt = 1.0/(N-1)
#            t = numpy.arange(0,1.0+dt,dt)
#            self.dt = dt
#            self.t = t
#
#            #prepare tolerances
#            tolP = 1.0e-4#7#8
#            tolQ = 1.0e-6#8#5
#            tol = dict()
#            tol['P'] = tolP
#            tol['Q'] = tolQ
#
#            self.tol = tol
#
#
#            # Get initialization mode
#
#            x = numpy.zeros((N,n,s))
#            #u = numpy.zeros((N,m,s))#5.0*numpy.ones((N,m,s))
#            u = numpy.arctanh(0.5*numpy.ones((N,m,s)))
#            #x[:,0,0] = t.copy()
#            #for i in range(N):
#            #    x[i,1,0] = x[N-i-1,0,0]
#            #x[:,2,0] = numpy.sqrt(20.0*x[:,0,0])
#            pi = numpy.array([2.0/numpy.sqrt(10.0)])
#            td = t * pi[0]
#            x[:,0,0] = 2.5 * (td**2)
#            x[:,1,0] = 1.0 - x[:,0,0]
#            x[:,2,0] = numpy.sqrt(10.0 * x[:,0,0])
#
#            #x[:,0,0] = .5*t
#            #x[:,0,1] = .5+.5*t
#
#            lam = 0.0*x
#            mu = numpy.zeros(q)
#            #pi = 10.0*numpy.ones(p)
#
#
#            self.x = x
#            self.u = u
#            self.pi = pi
#            self.lam = lam
#            self.mu= mu
#
#            self.constants['gradStepSrchCte'] = 1e-3
#
#            solInit = self.copy()
#
#            self.log.printL("\nInitialization complete.\n")
#            return solInit

        elif initMode == 'extSol':
            inpFile = opt.get('confFile','')

            # Get parameters from file

            self.loadParsFromFile(file=inpFile)

            # The actual "initial guess"

            N,m,n,p,q,s = self.N,self.m,self.n,self.p,self.q,self.s

            x = numpy.zeros((N,n,s))
            #u = numpy.zeros((N,m,s))#5.0*numpy.ones((N,m,s))
            u = numpy.zeros((N,m,s))
            #x[:,0,0] = t.copy()
            #for i in range(N):
            #    x[i,1,0] = x[N-i-1,0,0]
            #x[:,2,0] = numpy.sqrt(20.0*x[:,0,0])
            pi = numpy.array([10.0])

            #x[:,0,0] = .5*t
            #x[:,0,1] = .5+.5*t

            lam = 0.0*x
            mu = numpy.zeros(q)
            #pi = 10.0*numpy.ones(p)

            self.x = x
            self.u = u
            self.pi = pi
            self.lam = lam
            self.mu = mu

            solInit = self.copy()

            self.log.printL("\nInitialization complete.\n")
            return solInit

#%%

    def calcPhi(self):
        N = self.N
        n = self.n
        s = self.s
        phi = numpy.empty((N,n,s))
        x = self.x
        u = self.u
        pi = self.pi
        auto1 = self.constants['auto1']
        auto2 = self.constants['auto2']

        for arc in range(s):
            phi[:,0,arc] = pi[arc] * (auto1 * x[:,0,arc] + u[:,0,arc])
            phi[:,1,arc] = pi[arc] * (auto2 * x[:,1,arc] + u[:,0,arc])


        return phi

#%%

    def calcGrads(self,calcCostTerm=False):
        Grads = dict()

        N,n,m,p,q,s = self.N,self.n,self.m,self.p,self.q,self.s
        pi = self.pi

        auto1 = self.constants['auto1']
        auto2 = self.constants['auto2']
        contCostWeig = self.constants['contCostWeig']

        finish1 = self.restrictions['finish1']
        finish2 = self.restrictions['finish2']

        # Pre-assign functions
        Grads['dt'] = 1.0/(N-1)

        phix = numpy.zeros((N,n,n,s))
        phiu = numpy.zeros((N,n,m,s))

        if p>0:
            phip = numpy.zeros((N,n,p,s))
        else:
            phip = numpy.zeros((N,n,1,s))

        fx = numpy.zeros((N,n,s))
        fu = numpy.zeros((N,m,s))
        fp = numpy.zeros((N,p,s))

        #psiy = numpy.eye(q,2*n*s)
        psiy = numpy.zeros((q,2*n*s))
        psiy[0,0] = 1.0 # x(0) = start1
        psiy[1,1] = 1.0 # y(0) = start2
        psiy[2,2] = 1.0 # x(1) = finish1
        psiy[3,3] = 1.0 # y(1) = finish2

        psip = numpy.zeros((q,p))

        for arc in range(s):
            phix[:,0,0,arc] = pi[arc] * auto1
            phix[:,1,1,arc] = pi[arc] * auto2

            phiu[:,0,0,arc] = pi[arc]
            phiu[:,1,0,arc] = pi[arc]

            phip[:,0,arc,arc] = numpy.zeros(N)#auto1 * self.x[:,0,arc] + self.u[:,0,arc]
            phip[:,1,arc,arc] = numpy.zeros(N)#auto2 * self.x[:,1,arc] + self.u[:,0,arc]

            #fp[:,arc,arc] = (self.x[:,0,arc] - finish1) ** 2 + \
            #                (self.x[:,1,arc] - finish2) ** 2 + \
            #                contCostWeig * self.u[:,0,arc]**2
            fx[:,0,arc] = 2.0 * (self.x[:,0,arc] - finish1) * pi[arc]
            fx[:,1,arc] = 2.0 * (self.x[:,1,arc] - finish2) * pi[arc]
            fu[:,0,arc] = 2.0 * contCostWeig * self.u[:,0,arc] * pi[arc]
        #

        Grads['phix'] = phix
        Grads['phiu'] = phiu
        Grads['phip'] = phip
        Grads['fx'] = fx
        Grads['fu'] = fu
        Grads['fp'] = fp
    #    Grads['gx'] = gx
    #    Grads['gp'] = gp
        Grads['psiy'] = psiy
        Grads['psip'] = psip
        return Grads

#%%
    def calcPsi(self):
        N = self.N
#        return numpy.array([x[0,0,0],x[0,1,0],x[N-1,0,0]-0.5,x[N-1,1,0],\
#                            x[0,0,1]-0.5,x[0,1,1],x[N-1,0,1]-1.0,x[N-1,1,1]])
        sttStrtP1 = self.restrictions['start1']
        sttStrtP2 = self.restrictions['start2']
        sttEndP1 = self.restrictions['finish1']
        sttEndP2 = self.restrictions['finish2']
        return numpy.array([self.x[0,0,0] - sttStrtP1,\
                            self.x[0,1,0] - sttStrtP2,\
                            self.x[N-1,0,0] - sttEndP1,\
                            self.x[N-1,1,0] - sttEndP2])

    def calcF(self):
        N,s = self.N,self.s
        f = numpy.empty((N,s))
        u = self.u
        x = self.x
        sttEndP1 = self.restrictions['finish1']
        sttEndP2 = self.restrictions['finish2']
        contCostWeig = self.constants['contCostWeig']
        for arc in range(s):
            f[:,arc] = self.pi[arc] * ( contCostWeig * u[:,0,arc]**2 + \
                       (x[:,0,arc]-sttEndP1)**2 + (x[:,1,arc]-sttEndP2)**2 )

        return f, f, 0.0*f

    def calcI(self):
        N,s = self.N,self.s
        f, _, _ = self.calcF()

        Ivec = numpy.empty(s)
        for arc in range(s):
            Ivec[arc] = .5*(f[0,arc]+f[N-1,arc])
            Ivec[arc] += f[1:(N-1),arc].sum()

        Ivec *= 1.0/(N-1)
        I = Ivec.sum()
        return I, I, 0.0
#%%

    def plotSol(self,opt={},intv=[]):

        pi = self.pi

#        if len(intv)==0:
#            intv = numpy.arange(0,self.N,1,dtype='int')
#        else:
#             intv = list(intv)

        if len(intv)>0:
            self.log.printL("plotSol: Sorry, currently ignoring plotting range.")


        if opt.get('mode','sol') == 'sol':
            I, _, _ = self.calcI()
            titlStr = "Current solution: I = {:.4E}".format(I) + \
            " P = {:.4E} ".format(self.P) + " Q = {:.4E} ".format(self.Q)
            titlStr += "\n(grad iter #" + str(self.NIterGrad) + ")"
            plt.subplot2grid((5,1),(0,0),colspan=5)
            self.plotCat(self.x[:,0,:])
            plt.grid(True)
            plt.ylabel("x1")
            plt.title(titlStr)
            plt.subplot2grid((5,1),(1,0),colspan=5)
            self.plotCat(self.x[:,1,:],color='g')
            plt.grid(True)
            plt.ylabel("x2")
            plt.subplot2grid((5,1),(2,0),colspan=5)
            self.plotCat(self.u[:,0,:],color='k')
            plt.grid(True)
            plt.ylabel("u1")
            plt.xlabel("Time [s]")

            plt.subplots_adjust(0.0125,0.0,0.9,2.5,0.2,0.2)

            self.savefig(keyName='currSol',fullName='solution')

            self.log.printL("pi = "+str(pi)+"\n")
        elif opt['mode'] == 'var':
            dx = opt['x']
            du = opt['u']
            dp = opt['pi']

            titlStr = "Proposed variations (grad iter #" + \
                      str(self.NIterGrad+1) + ")\n"+"Delta pi: "
            for i in range(self.p):
                titlStr += "{:.4E}, ".format(dp[i])
                #titlStr += str(dp[i])+", "

            plt.subplots_adjust(0.0125,0.0,0.9,2.5,0.2,0.2)

            plt.subplot2grid((5,1),(0,0))
            self.plotCat(dx[:,0,:])
            plt.grid(True)
            plt.ylabel("x1")
            plt.title(titlStr)

            plt.subplot2grid((5,1),(1,0))
            self.plotCat(dx[:,1,:],color='g')
            plt.grid(True)
            plt.ylabel("x2")

            plt.subplot2grid((5,1),(2,0))
            self.plotCat(du[:,0,:],color='k')
            plt.grid(True)
            plt.ylabel("u1")

            plt.xlabel("Time [s]")

            self.savefig(keyName='corr',fullName='corrections')

        elif opt['mode'] == 'lambda':
            titlStr = "Lambda for current solution"

            plt.subplot2grid((5,1),(0,0),colspan=5)
            self.plotCat(self.lam[:,0,:])
            plt.grid(True)
            plt.ylabel("lambda: x1")
            plt.title(titlStr)
            plt.subplot2grid((5,1),(1,0),colspan=5)
            self.plotCat(self.lam[:,1,:],color='g')
            plt.grid(True)
            plt.ylabel("lambda: x2")
            plt.subplot2grid((5,1),(2,0),colspan=5)
            self.plotCat(self.u[:,0,:],color='k')
            plt.grid(True)
            plt.ylabel("u1 [-]")
            plt.xlabel("Time [s]")

            plt.subplots_adjust(0.0125,0.0,0.9,2.5,0.2,0.2)
            self.savefig(keyName='currLamb',fullName='lambdas')

            self.log.printL("mu = "+str(self.mu))

        else:
            titlStr = opt['mode']

    def plotTraj(self,mustSaveFig=True):
        """Plot the trajectory on the state space."""

        X = self.x[:,0,0]
        Y = self.x[:,1,0]

        plt.plot(X,Y)
        plt.plot(X[0],Y[0],'o')
        plt.plot(X[-1],Y[-1],'s')
        plt.axis('equal')
        plt.grid(True)
        plt.xlabel("x1")
        plt.ylabel("x2")

        titlStr = "Trajectory "
        titlStr += "(grad iter #" + str(self.NIterGrad) + ")\n"
        plt.title(titlStr)
        #plt.legend(loc="upper left", bbox_to_anchor=(1,1))

        if mustSaveFig:
            self.savefig(keyName='traj',fullName='trajectory')
        else:
            plt.show()
            plt.clf()

    #
if __name__ == "__main__":
    print("\n\nRunning probLQR.py!\n")
    exmpProb = prob()

    print("Initializing problem:")
    exmpProb = exmpProb.initGues()
    exmpProb.printPars()
    s = exmpProb.s

    print("Plotting current version of solution:")
    exmpProb.plotSol()

    print("Calculating f:")
    f,_,_ = exmpProb.calcF()
    exmpProb.plotCat(f)
    plt.grid(True)
    plt.xlabel('Time')
    plt.ylabel('f')
    plt.show()

    print("Calculating grads:")
    Grads = exmpProb.calcGrads()
    for key in Grads.keys():
        print("Grads['",key,"'] = ",Grads[key])

    print("Calculating I:")
    I = exmpProb.calcI()
    print("I = ",I)