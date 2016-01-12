import numpy as np
import linAlgSolve

# This function puts a 3d array on a grid with
# indicies (i,j,k) into a 1d array. 
#   PHI[i] = phi[i]
#   PHI[(Ny+1)*i + j] = phi[i][j]
#   PHI[(Nz+1)*(Ny+1)*i+(Nz+1)*j+k] = phi[i][j][k]
def indexTo1D(N,i,j,k):
  return (N[2]+1)*(N[1]+1)*i+(N[2]+1)*j+k

def useBCs(index1,index2,V1,V2,potBC,D,rowsNotBC):
  indexes = [index1,index2]
  V = [V1,V2]
  for i in range(2):
    index = indexes[i]
    myV = V[i]
    if index not in rowsNotBC:
      if potBC[index] != myV:
        print("inconsistent BCs")
    else:  
      potBC[index] = myV
      D[index][index] = 1.0
      rowsNotBC.remove(index)

# Takes 1-D array and puts it on the computational grid
# returning a d-D array
def putPotentialOnGrid(N,PHI):
  (NX,NY,NZ) = (N[0],N[1],N[2])
  if NY == 0 and NZ == 0:
    phi = np.zeros(NX+1)
    for i in range(len(phi)):
      phi[i] = PHI[indexTo1D(N,i,0,0)]

  elif NY != 0 and NZ == 0:
    phi = np.zeros((NX+1,NY+1))
    for i,j in np.ndindex(phi.shape):
      phi[i][j] = PHI[indexTo1D(N,i,j,0)]

  else:
    phi = np.zeros((NX+1,NY+1,NZ+1))
    for i,j,k in np.ndindex(phi.shape):
      phi[i][j][k] = PHI[indexTo1D(N,i,j,k)]

  return phi

# Solve linear system A x = B
def solveLinearSystem(A,B,relTol,absTol,solType):
  if solType == "direct":
    x = linAlgSolve.direct(A,B)
  elif solType == "iterative":
    x = linAlgSolve.iterate(A,B,relTol,absTol)
  else:
    sys.exit("esSolve::solveForPotential() -- invalid solution type")

  return x

# Solve linear system D * PHI = potBC but return
# PHI on the computational grid
def solveForPotential(N,D,potBC,relTol,absTol,solType):
  return putPotentialOnGrid(N,solveLinearSystem(D,potBC,relTol,absTol,solType))

def laplace1D(NX,DX,V0x,VNx,solType,relTol,absTol):
  return laplace([NX,0,0],[DX,1.0,1.0],[V0x],[VNx],solType,relTol,absTol)

def laplace2D(NX,DX,V0x,VNx,NY,DY,V0y,VNy,solType,relTol,absTol):
  return laplace([NX,NY,0],[DX,DY,1.0],[V0x,V0y],[VNx,VNy],solType,relTol,absTol)

def laplace3D(NX,DX,V0x,VNx,NY,DY,V0y,VNy,NZ,DZ,V0z,VNz,solType,relTol,absTol):
  return laplace([NX,NY,NZ],[DX,DY,DZ],[V0x,V0y,V0z],[VNx,VNy,VNz],solType,relTol,absTol)

### General Laplace Solver ###
def laplace(N,D,V0,VN,solType,relTol,absTol):
  (NX,NY,NZ) = (N[0],N[1],N[2])
  (DX,DY,DZ) = (D[0],D[1],D[2])
  pts = (NX+1)*(NY+1)*(NZ+1)
  D = np.zeros(shape=(pts,pts))
  potBC = np.zeros(shape=(pts))
#  PHI = np.zeros(shape=(pts))
  rowsNotBC = [i for i in range(pts)]

  # Set up rows corresponding to a boundary condition
  for j in range(NY+1):
    for k in range(NZ+1):
      if NY == 0 and NZ == 0:
        useBCs(indexTo1D(N,0,j,k),indexTo1D(N,NX,j,k),V0[0],VN[0],potBC,D,rowsNotBC)
      if NY != 0 and NZ == 0:
        useBCs(indexTo1D(N,0,j,k),indexTo1D(N,NX,j,k),V0[0][j],VN[0][j],potBC,D,rowsNotBC)
      if NY != 0 and NZ != 0:
        useBCs(indexTo1D(N,0,j,k),indexTo1D(N,NX,j,k),V0[0][j][k],VN[0][j][k],potBC,D,rowsNotBC)

  if NY > 0:
    for i in range(NX+1):
      for k in range(NZ+1):
        if NZ == 0:
          useBCs(indexTo1D(N,i,0,k),indexTo1D(N,i,NY,k),V0[1][i],VN[1][i],potBC,D,rowsNotBC)
        else:
          useBCs(indexTo1D(N,i,0,k),indexTo1D(N,i,NY,k),V0[1][i][k],VN[1][i][k],potBC,D,rowsNotBC)

    if NZ > 0:
      for i in range(NX+1):
        for j in range(NY+1):
          useBCs(indexTo1D(N,i,j,0),indexTo1D(N,i,j,NZ),V0[2][i][j],VN[2][i][j],potBC,D,rowsNotBC)

  # Set up rows not corresponding to a boundary condition
  for row in rowsNotBC:
    coeffX = pow(DY*DZ,2.0)
    if NY == 0.0:
      coeffY = 0.0
    else:
      coeffY = pow(DX*DZ,2.0)
    if NZ == 0.0:
      coeffZ = 0.0
    else:
      coeffZ = pow(DX*DY,2.0)
    coeffXYZ = -2.0*(coeffX+coeffY+coeffZ)

    D[row][row - (NZ+1)*(NY+1)] = coeffX
    D[row][row + (NZ+1)*(NY+1)] = coeffX
    if NY != 0.0:
      D[row][row - (NZ+1)] = coeffY
      D[row][row + (NZ+1)] = coeffY
    if NZ != 0.0:
      D[row][row - 1] = coeffZ
      D[row][row + 1] = coeffZ
    D[row][row] = coeffXYZ

  return solveForPotential(N,D,potBC,relTol,absTol,solType)
