#!/usr/bin/python3.4
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#% FUNÇÃO DE CÁLCULOS DO VOlUME MOLAR DA EOS                          
#% Criado em: 20/12/2016                                                   
#% Última alteração em: 26/12/2016                                         
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

import math
import numpy as np

def CalculaVolumeMolarEOS(nc, A, B, TEQ, R, T, P):
    
    # ENTRADAS DA FUNÇÃO
    #   T : temperatura (K)
    #   P : Pressão (bar)
    #   A : parâmetro A da EOS
    #   B : parâmetro B da EOS
    #   TEQ: tipo de equilibrio

    # Declaracao dos vetores
    Rp         = []
    Rq         = []
    Rr         = []
    z1         = []
    z2         = []
    z3         = []
    tresRaizes = []
    Ra         = []
    Rb         = []
    DCM        = []
    valor1     = []
    valor2     = []
    Ar         = []
    Br         = []
    modulo     = []
    arg        = []
    apoio      = []
    Vm         = []
    raizes     = []
    
    # Inicializando os vetores com zeros.
    for i in range(nc):
        Rp.append(0)
        Rq.append(0)
        Rr.append(0)
        Ra.append(0)
        Rb.append(0)
        DCM.append(0)
        arg.append(0)
        raizes.append(np.array([0]))
        apoio.append(0)
        modulo.append(0)
        tresRaizes.append(0)
        z1.append(np.array([0]))
        z2.append(np.array([0]))
        z3.append(np.array([0]))        
        Ar.append(np.array([0]))
        Br.append(np.array([0]))
        Vm.append(np.array([0]))
        valor1.append(np.array([0]))
        valor2.append(np.array([0]))
        
    # MÉTODO ANALÍTICO DE RESOLUÇÃO DA EQUAÇÃO CÚBICA
    for i in range(1,3):   # duas interações: i = 1 e i = 2
        
        # PENG-ROBINSON
        Rp[i] = B[i] - 1
        Rq[i] = (A[i] - 3*(B[i]**2) - 2*B[i])
        Rr[i] = -(A[i]*B[i]) + B[i]**2 + B[i]**3      
        
        z1[i] = 0
        z2[i] = 0
        z3[i] = 0
        tresRaizes[i] = True
    
        Ra[i] = (3*Rq[i] - ((Rp[i])**2))/3
        Rb[i] = (2*(Rp[i]**3) - 9*Rp[i]*Rq[i] + 27*Rr[i])/27  
        DCM[i] = (Rb[i]**2)/4 + (Ra[i]**3)/27
        
        if DCM[i] >= 0:         # se [DCM] for maior que zero, faça:
            valor1[i] = math.sqrt(DCM[i]) - Rb[i]/2
                   
            if valor1[i] == 0:  # se [valor1] for igual a zero, faça:
                Ar[i] = 0
                
            if valor1[i] > 0:   # se [valor1] for maior que zero, faça:
                Ar[i] = math.exp(math.log(valor1[i])/3)
               
            if valor1[i] < 0:   # se [valor1] for menor que zero, faça:
                valor1[i] = abs(valor1[i])
                Ar[i] = -math.exp(math.log(valor1[i])/3)
    
            valor2[i] = -math.sqrt(DCM[i])-Rb[i]/2
            
            if valor2[i] == 0:  # se [valor2] for igual a zero, faça:
                Br[i] = 0
            
            if valor2[i] > 0:   # se [valor2] for maior que zero, faça:
                Br[i] = math.exp(math.log(valor2[i])/3)
            
            if valor2[i] < 0:   # se [valor2] for menor que zero, faça:
                valor2[i] = abs(valor2[i])
                Br[i] = -math.exp(math.log(valor2[i])/3)
    
            if Ar[i] != Br[i]:  # se [Ar] for diferente de [Br], faça:
                z1[i] = Ar[i] + Br[i]
                tresRaizes[i] = False
                         
            elif Ar[i] != 0:    # se [Ar] for diferente de zero, faça:
                z1[i] = Ar[i] + Br[i]
                z2[i] = -(Ar[i] + Br[i])/2
                z3[i] = z2[i]
            
        if DCM[i] < 0:          # se [DCM] for menor que zero, faça:
            DCM[i] = abs(DCM[i])
            modulo[i] = math.sqrt((-Rb[i]/2)**2 + DCM[i])
            arg[i] = math.atan(-2*math.sqrt(DCM[i])/Rb[i])
            
            if modulo[i] == 0:  # se [modulo] for igual a zero, faça:
                apoio[i] = 0    #%apoio = CBRT(modulo) no algoritmo Pascal
            
            if modulo[i] > 0:   # se [modulo] for maior que zero, faça:
                apoio[i] = math.exp(math.log(modulo[i])/3) 
                
            if modulo[i] < 0:   # se [modulo] for menor que zero, faça:
                modulo[i] = abs(modulo[i])
                apoio[i] = -math.exp(math.log(modulo[i])/3) 
            
            z1[i] =  2*math.cos(arg[i]/3)*apoio[i]
            z2[i] =  2*math.cos((arg[i] + 2*math.pi)/3)*apoio[i]
            z3[i] =  2*math.cos((arg[i] + 4*math.pi)/3)*apoio[i]
        
        #% ESCOLHA DAS RAÍZES    
        if tresRaizes[i] == True:   # se [tresRaizes] for igual a "True", faça:
            z1[i] = z1[i]-(Rp[i]/3)
            z2[i] = z2[i]-(Rp[i]/3)
            z3[i] = z3[i]-(Rp[i]/3)
            
            raizes = [z1[i], z2[i], z3[i]]
            raizesOrdenadas = np.sort(raizes, axis=None)
            
            if (TEQ == 1 or TEQ == 3):
                Vm[i] = raizesOrdenadas[0]*R*T/P  #% UTILIZA A MENOR RAIZ
            
            if TEQ == 2:
                Vm[i] = raizesOrdenadas[2]*R*T/P   #% UTILIZA A MAIOR RAIZ
                
            if TEQ == 4:
                if i == 1: #%(fase pesada)
                    Vm[1] = raizesOrdenadas[0]*R*T/P #% UTILIZA A MENOR RAIZ
                    
                if i == 2:  #%(fase leve)
                    Vm[2] = raizesOrdenadas[2]*R*T/P  #% UTILIZA A MAIOR RAIZ
        
        if tresRaizes[i] == False:  # se [tresRaizes] for igual a "False", faça:
            z1[i] = z1[i]-(Rp[i]/3)
            Vm[i] = z1[i]*R*T/P     #% Utiliza a única raiz
                      
    return (Vm)
