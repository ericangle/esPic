import os
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../solvers')
import esSolve
from mpl_toolkits.mplot3d import axes3d
from dirichlet import dirichlet as dirBC

NX = 35
NY = 40
LX = 1.25
LY = 2.3
DX = LX / NX
DY = LY / NY
X0 = 1.0
Y0 = 2.0

amplitude = 2.0

def nonGroundedWall(Yindex):
  return amplitude * np.sin(np.pi * Yindex / NY)

# Boundary conditions
V0x = dirBC(np.zeros((NY+1)))
VNx = dirBC(np.fromfunction(nonGroundedWall, (NY+1,)))

V0y = dirBC(np.zeros((NX+1)))
VNy = dirBC(np.zeros((NX+1)))

start = time.clock()
potential_NoCython = esSolve.laplace2D(NX,DX,V0x,VNx,NY,DY,V0y,VNy,"gaussSeidel",relTol=0.0,absTol=1.0e-3,useCython=False)
end = time.clock()
seconds_NoCython = end - start
print("No Cython took",round(seconds_NoCython,1),"seconds.")

start = time.clock()
potential_Cython = esSolve.laplace2D(NX,DX,V0x,VNx,NY,DY,V0y,VNy,"gaussSeidel",relTol=0.0,absTol=1.0e-3,useCython=True)
end = time.clock()
seconds_Cython = end - start
print("Cython took",round(seconds_Cython,1),"seconds.")

print("Cython was",round(100.0*(1.0-seconds_Cython/seconds_NoCython),1),"percent faster.")
