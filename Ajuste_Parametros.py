import sys
import time
import numpy as np
import math
import threading
import Calculo_Equilibrio

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# PROGRAMA DE AJUSTE DOS PARÂMETROS DE INTERAÇÃO BINÁRIO USANDO
# PR-EOS                                                                  
# Última alteração em: 03/04/2017
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def AjusteParametros(desvio, Ka, Ka_check, Kb, Kb_check, fObjtivo, TEQ, temperaturaCritica, pressaoCritica, fatorAcentrico, Vmolar, counter, temperatura, pressao, x2, y2, pressao_sublimacao):

	###############################################################################
	#####      Print dos dados recebidos pela método AjusteParametros         #####
	###############################################################################
	tamDados = counter					# 
	Y = np.zeros(tamDados+1)
	X = np.zeros(tamDados+1)
	Vmolar_soluto = np.zeros(tamDados+1)
	Psat_soluto = np.zeros(tamDados+1)
	pPrimeiro = np.zeros(4)
	pUltimo = np.zeros(4)
	var_temp = np.zeros(4)
	fObj = np.zeros(4)
	fObjNovo = np.zeros(4)
	#resp = np.zeros(4)
	P_Centroide = np.zeros(4)
	P = np.zeros((4,4))
	P_Refletido = np.zeros((2,4))
	P_Expandido = np.zeros((2,4))
	P_Contraido = np.zeros((2,4))

	TA = fObjtivo # TA = tipo de ajuste, comparar só y(opção 1), x (opção 2), ou x e y (opção 3)
	NC = counter
	nc = counter + 1
	Tc = temperaturaCritica
	Pc = pressaoCritica
	w = fatorAcentrico	
	tol = desvio
	Temperatura = temperatura			# temperatura
	Pressao = pressao					# pressão
	yExp = y2							# fração molar do componente 2 na fase leve
	xExp = x2							# fração molar do componente 2 na fase pesada
	OPCAO = 2
	Psat_soluto = pressao_sublimacao	# pressão de vapor
	Vmolar_soluto = Vmolar

	# Constantes
	alfa = 1
	beta = 1/2
	gama = 2
	sigma = 1/2

	''' 
	if (TEQ == 3 or TEQ == 4): # ELL | ELV
		Vmolar_soluto = [0.0, 0.0, 0.0]
		Psat_soluto = [0.0, 0.0, 0.0]
		Y = [0.0, 0.0, 0.0]
	 
	if (TEQ == 1 or TEQ == 2): # ESL ou ESV
		X = [0.0, 0.0, 0.0]
	 
	if (NC <= 2):
		print('X e Y', '\n')
		Y = [0.0, 1.0, 1.0]
		X = [0.0, 1.0, 1.0]
	'''
	
	#Y[1] = 1

	# AJUSTE DOS PARAMETROS DE INTERAÇÃO BINARIOS
	
	# Entrada de valores
	numParametros = 2		# Número de parâmetros
	iteracao = 0
	solucao = False
	 
	#Pontos do triângulo --> Ka e Kb: Estimativa Inicial
	# Inicializacao das matrizes com zeros
	
	if(Ka_check == 'True' and Kb_check == 'False'):
		print('1','\n')
		P[1,1] = Ka
		P[2,1] = Ka
		P[3,1] = Ka
		P[1,2] = Kb
		P[2,2] = Kb
		P[3,2] = 0.9*Kb

	elif(Ka_check == 'False' and Kb_check == 'True'):
		print('2','\n')
		P[1,1] = Ka
		P[2,1] = 0.9*Ka
		P[3,1] = Ka		
		P[1,2] = Kb
		P[2,2] = Kb
		P[3,2] = Kb	

	elif(Ka_check == 'True' and Kb_check == 'True'):
		print('3','\n')
		P[1,1] = Ka
		P[2,1] = Ka
		P[3,1] = Ka		
		P[1,2] = Kb
		P[2,2] = Kb
		P[3,2] = Kb	
	elif(Ka_check == 'False' and Kb_check == 'False'):
		print('4','\n')
		P[1,1] = Ka
		P[1,2] = Kb
		P[2,1] = 0.9*Ka
		P[2,2] = Kb
		P[3,1] = Ka
		P[3,2] = 0.9*Kb	
			 
	tamDados = len(yExp)
	
	# Calculo da Y e X pelo modelo (parâmetro)
	for i in range(1,tamDados):

		fObj[1] = fObj[1] + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[1,1], P[1,2], Vmolar_soluto, Psat_soluto[i], Y, X)

		fObj[2] = fObj[2] + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[2,1], P[2,2], Vmolar_soluto, Psat_soluto[i], Y, X)

		fObj[3] = fObj[3] + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[3,1], P[3,2], Vmolar_soluto, Psat_soluto[i], Y, X)
	
	resp_ordenacao = ordenacao(fObj, P)
	fObjOrdenado = resp_ordenacao[0]
	P_Ordenado = resp_ordenacao[1]
				
	# Condição de parada (a ser satisfeita)
	if (math.fabs((fObjOrdenado[3]- fObjOrdenado[1])/fObjOrdenado[3]) < tol):
		solucao = True	

	# Caso as condições não sejam satisfeitas, o programa abaixo é executado
	while(solucao == False):
		iteracao = iteracao + 1		

		#### Cálculo do centroide ####
		P_Centroide[1] = (P_Ordenado[1,1] + P_Ordenado[2,1])/2	# Ka
		P_Centroide[2] = (P_Ordenado[1,2] + P_Ordenado[2,2])/2	# Kb

		#### REFLEXAO ####
		P_Refletido[1] = P_Centroide + alfa*(P_Centroide - P[3]) # criou um novo triângulo
		fObjReflexao = 0
			
		for i in range(1,tamDados):

			fObjReflexao = fObjReflexao + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Refletido[1,1], P_Refletido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X)
					
		if (fObjReflexao <= fObjOrdenado[1]):

			#### Condição: Expansão ####
			P_Expandido[1] = P_Centroide + gama*(P_Refletido[1] - P_Centroide) 
			fObjExpansao = 0				

			for i in range(1, tamDados):
				fObjExpansao = fObjExpansao + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Expandido[1,1], P_Expandido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X)

			if (fObjExpansao <= fObjOrdenado[1]):
				fObjOrdenado[3] = fObjOrdenado[1]
				fObjOrdenado[2] = fObjReflexao
				fObjOrdenado[1] = fObjExpansao
				P[3] = P[1]
				P[2] = P_Refletido[1]
				P[1] = P_Expandido[1]

				resp_ordenacao = ordenacao(fObjOrdenado, P)
				fObjOrdenado = resp_ordenacao[0]
				P_Ordenado = resp_ordenacao[1]
						
			else:
				fObjOrdenado[3] = fObjReflexao
				P[3] = P_Refletido[1]
				resp_ordenacao = ordenacao(fObjOrdenado, P)
				fObjOrdenado = resp_ordenacao[0]
				P_Ordenado = resp_ordenacao[1]

		#### Condição: Contração ####
		elif (fObjReflexao > fObjOrdenado[2]):

			if (fObjReflexao < fObjOrdenado[3]):
				fObjOrdenado[3] = fObjReflexao
				P_Ordenado[3] = P_Refletido[1]
			
			P_Contraido[1] = P_Centroide - beta*(P_Centroide - P[3])

			fObjContracao = 0

			for i in range(1, tamDados):

				fObjContracao = fObjContracao + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Contraido[1,1], P_Contraido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X)
		
			# Condições para o valor contraído
			if (fObjContracao > fObjOrdenado[3]):
				print('calcula novos pontos', '\n')
				P[2] = (P[2] + P[1])/2
				P[3] = (P[3] + P[1])/2

				for i in range(1, tamDados):

					fObjNovo[2] = fObjNovo[2] + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[2,1], P[2,2], Vmolar_soluto, Psat_soluto[i], Y, X)

					fObjNovo[3] = fObjNovo[3] + funcao_objetivo(TA, yExp[i], xExp[i], TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[3,1], P[3,2], Vmolar_soluto, Psat_soluto[i], Y, X)
					print('fObjNovo[3] = ', fObjNovo[3], '\n')

			else:
				fObjOrdenado[3] = fObjContracao
				P[3] = P_Contraido[1]

			resp_ordenacao = ordenacao(fObjOrdenado, P)
			fObjOrdenado = resp_ordenacao[0]
			P_Ordenado = resp_ordenacao[1]

		else:
			print('Condição: Reflexão')
			fObjOrdenado[3] = fObjOrdenado[2]
			fObjOrdenado[2] = fObjReflexao
			P[3] = P[2]
			P[2] = P_Refletido[1]
				
		# Condição de parada (a ser satisfeita)
		if (math.fabs((fObjOrdenado[3]- fObjOrdenado[1])/fObjOrdenado[3]) < tol):
			#print('solucao = True', '\n')
			print('\n#############################################\n')
			print('numero de iterações = ', iteracao, '\n')
			print('\n#############################################\n')
			var_temp = np.zeros(4)
			var_temp = P_Ordenado[1]
			Ka = var_temp[1]
			Kb = var_temp[2]
			print('Ka =  ', Ka, '\t \t', 'Kb =  ', Kb, '\n')
			print('\n#############################################\n')
			print('Funcao Objetivo = ', fObjOrdenado[1], '\n')
			print('\n#############################################\n')
			solucao = True
			#input('\n encontrou a minima função objetivo...pressione entre para sair do programa \n')
			print('condicao satisfeita')
			for i in range(1,tamDados):

				resp1 = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, Ka, Kb, Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
				print('resp1 = ', resp1, '\n')
				print('pressao = ', Pressao[i], '\n')
				
			break  
				
		if (iteracao >= 500):
			print ('O algoritmo SIMPLEX não convergiu em 500 iterações.')	
			#print ('condicao de parada =  ', '\n')
			#input('\n Pressione < Entrer > para Continuar \n')	
			return(False)
			s._stop()
			break
			print("saindo")
			sys.exit(0)
		
	# MOSTRANDO OS RESULTADOS
	if (solucao == True):
		print('\n','######################Vmolar_soluto###########################################')
		print('O algoritmo convergiu em ' , str(iteracao), ' iterações.', '\n')
		print('#################################################################','\n')

	return(True)			


def ordenacao(fObj, P):
	for i in range(1,3):		# i = 1 e i = 2
		for j in range(i+1, 4):	# j = 2 e j = 3
			if(fObj[j] < fObj[i]):
				apoio1 = fObj[i]
				fObj[i] = fObj[j]
				fObj[j] = apoio1
				var1 = P[i,1]
				var2 = P[i,2]
				P[i,1] = P[j,1]
				P[i,2] = P[j,2]
				P[j,1] = var1
				P[j,2] = var2
	return(fObj, P)


def funcao_objetivo(TA, yExp, xExp, TEQ, Pressao, Temperatura, Tc, Pc, w, ka, kb, Vmolar_soluto, Psat_soluto, Y, X):

	fObjetivo = 0
	resp = np.zeros(4)
	xExperimental = int(xExp)
	yExperimental = int(yExp)

	resp = Calculo_Equilibrio.CalculaEquilibrioPR(2,TEQ,Pressao,Temperatura,Tc,Pc,w,ka,kb,Vmolar_soluto,Psat_soluto,Y,X,1,2)
	print('resp = ', resp, '\n')
	yCal = resp[0]
	xCal = resp[1]
	iteracao = resp[2]
	
	if (iteracao >= 500):
		fObjetivo = 4

	else:
		if (TA == 0):	# AJUSTANDO COM BASE EM Y
			if(yExperimental == 10):
				fObjetivo = fObjetivo

			else:
				fObjetivo = ((yCal - yExp)/(1- yExp))**2 + (1 - yCal/yExp)**2
				
		if (TA == 1):	# AJUSTANDO COM BASE EM X
			if(xExperimental == 10):
				fObjetivo = fObjetivo

			else:
				fObjetivo = ((xCal - xExp)/(1- xExp))**2 + (1 - xCal/xExp)**2

		# Função objetivo	
		if (TA == 2):	# AJUSTANDO COM BASE EM X E Y

			if(xExperimental == 10):
				fObjetivo = ((yCal - yExp)/(1-yExp))**2 + (1 - yCal/yExp)**2

			elif(yExperimental == 10):
				fObjetivo = ((xCal - xExp)/(1- xExp))**2 + (1 - xCal/xExp)**2

			elif(yExperimental == 10 and xExperimental == 10):
				fObjetivo = fObjetivo 

			else:
				fObjetivo = ((yCal - yExp)/(1-yExp))**2 + (1 - yCal/yExp)**2 + ((xCal - xExp)/(1- xExp))**2 + (1 - xCal/xExp)**2

	return(fObjetivo)
