import sys
import time
import numpy as np
import math
import Calculo_Equilibrio

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# PROGRAMA DE AJUSTE DOS PARÂMETROS DE INTERAÇÃO BINÁRIO USANDO
# PR-EOS                                                                  
# Última alteração em: 27/03/2017
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def AjusteParametros(desvio, Ka, Ka_check, Kb, Kb_check, fObj, TEQ, temperaturaCritica, pressaoCritica, fatorAcentrico, Vmolar_soluto, counter, temperatura, pressao, x2, y2, pressao_sublimacao):

	###############################################################################
	#####      Print dos dados recebidos pela método AjusteParametros         #####
	###############################################################################
	'''
	print('Ajuste de Parametros', '\n')
	print('desvio =  ', desvio, '\n')
	print('Ka = ', Ka, '\n')
	print('Ka_check =  ', Ka_check, '\n')
	print('Kb = ', Kb, '\n')
	print('Kb_check = ', Kb_check, '\n')
	print('fObj = ', fObj, '\n')
	print('TEQ = ', TEQ, '\n')
	print('temperaturaCritica = ', temperaturaCritica, '\n')
	print('pressaoCritica = ', pressaoCritica, '\n')
	print('fatorAcentrico = ', fatorAcentrico, '\n')
	print('Vmolar_soluto = ', Vmolar_soluto, '\n')
	print('counter = ', counter, '\n')
	print('temperatura = ', temperatura, '\n')
	print('pressao = ', pressao, '\n')
	print('x2 = ', x2, '\n')
	print('y2 = ', y2, '\n')
	print('pressao_sublimacao = ', pressao_sublimacao, '\n')
	
	###############################################################################
	'''

	TA = fObj # TA = tipo de ajuste, comparar só y(opção 1), x (opção 2), ou x e y (opção 3)
	NC = counter
	nc = counter + 1
	Tc = temperaturaCritica
	Pc = pressaoCritica
	w = fatorAcentrico
	
	tol = desvio
	Temperatura = temperatura				# temperatura
	Pressao = pressao						# pressão
	yExp = y2								# fração molar do componente 2 na fase leve
	Psat_soluto = pressao_sublimacao		# pressão de vapor
	xExp = x2								# fração molar do componente 2 na fase pesada
	tamDados = counter						# 
	#print('tamDados [counter] = ', tamDados, '\n')
	OPCAO = 2

	Y = np.zeros(tamDados+1)
	X = np.zeros(tamDados+1)
	Vmolar_soluto = np.zeros(tamDados+1)
	Psat_soluto = np.zeros(tamDados+1)

	yCal1 = np.zeros(tamDados+1)
	xCal1 = np.zeros(tamDados+1)
	yCal2 = np.zeros(tamDados+1)
	xCal2 = np.zeros(tamDados+1)
	yCal3 = np.zeros(tamDados+1)
	xCal3 = np.zeros(tamDados+1)
	pPrimeiro = np.zeros(tamDados+1)
	pUltimo = np.zeros(tamDados+1)
	var_temp = np.zeros(tamDados+1)
	P_Centroide = np.zeros(tamDados+1)
	resp = np.zeros(4)
	fObj = np.zeros(tamDados+1)

	P = np.zeros((4,4))
	P_Refletido = np.zeros((2,4))


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
	    	    
	# AJUSTE DOS PARAMETROS DE INTERAÇÃO BINARIOS
	if (OPCAO == 2):
	
		# Entrada de valores
		numParametros = 2		# Número de parâmetros
		iteracao = 0
	 
		#Pontos do triângulo --> Ka e Kb: Estimativa Inicial
		# Inicializacao das matrizes com zeros
		P[1,1] = Ka
		P[1,2] = Kb
		P[2,1] = 0.9*Ka
		P[2,2] = Kb
		P[3,1] = Ka
		P[3,2] = 0.9*Kb
		 			
		# Condição inicial
		solucao = False
		 
		while (solucao == False):

			print('P =  ', P, '\n')

			iteracao = iteracao + 1

			print('Iteracoes Ajuste =  ' , str(iteracao), ' iterações.', '\n')

			tamDados = len(yExp)

			#print('tamDados [yExp] = ', tamDados, '\n')

			# Calculo da Y e X pelo modelo (parâmetro)
			for i in range(1,tamDados):

				resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[1,1], P[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)

				yCal1, xCal1 = resp[0], resp[1]

				#print('yCal1 = ', yCal1, '\n')

				#print('xCall1 = ', xCal1, '\n')

				print('######################## terminou 1 #########################', '\n')

				resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[2,1], P[2,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)

				yCal2, xCal2 = resp[0], resp[1]

				#print('yCal2 = ', yCal2, '\n')

				#print('xCal2 = ', xCal2, '\n')		
	
				print('######################## terminou 2 #########################', '\n')

				resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[3,1], P[3,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)

				yCal3, xCal3 = resp[0], resp[1]

				#print('yCal3 = ', yCal3, '\n')

				#print('xCal3 = ', xCal3, '\n')

				print('######################## terminou 3 #########################', '\n')

			#print('TA = ', TA, '\n')

			'''
			print('fObj = ', fObj, '\n')
			print('yCal1 = ', yCal1, '\n')
			print('yCal2 = ', yCal2, '\n')
			print('yCal3 = ', yCal3, '\n')
			print('xCal1 = ', xCal1, '\n')
			print('xCal2 = ', xCal2, '\n')
			print('xCal3 = ', xCal3, '\n')
			print('yExp = ', yExp, '\n')
			print('xExp = ', xExp, '\n')
			input('Digite para continuar \n')
			'''

			# Função objetivo	
			if (TA == 0):	# AJUSTANDO COM BASE EM X E Y

				for i in range(1,tamDados-1):

					fObj[1] = fObj[1] + ((yCal1[i] - yExp[i])/(1-yExp[i]))**2 + (1 - yCal1[i]/yExp[i])**2 + ((xCal1[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal1[i]/xExp[i])**2

					#print('fObj[1] = ', fObj, '\n')

					fObj[2] = fObj[2] + ((yCal2[i] - yExp[i])/(1-yExp[i]))**2 + (1 - yCal2[i]/yExp[i])**2 + ((xCal2[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal2[i]/xExp[i])**2

					#print('fObj[2] = ', fObj, '\n')

					fObj[3] = fObj[3] + ((yCal3[i] - yExp[i])/(1-yExp[i]))**2 + (1 - yCal3[i]/yExp[i])**2 + ((xCal3[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal3[i]/xExp[i])**2

					#print('fObj[3] = ', fObj, '\n')

					#print('i = ', i, '\n')

					#input('Digite para continuar \n')

			#print('fObj (TA == 0) : ', fObj, '\n')

			if (TA == 1):	# AJUSTANDO COM BASE EM Y
				for i in range(1,tamDados):

					fObj[1] = fObj[1] + ((yCal1[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal1[i]/yExp[i])**2

					fObj[2] = fObj[2] + ((yCal2[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal2[i]/yExp[i])**2

					fObj[3] = fObj[3] + ((yCal3[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal3[i]/yExp[i])**2

			#print('fObj (TA == 1) : ', fObj, '\n')
					
			if (TA == 2):	# AJUSTANDO COM BASE EM X
				for i in range(1,tamDados):

					fObj[1] = fObj[1] + ((xCal1[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal1[i]/xExp[i])**2

					fObj[2] = fObj[2] + ((xCal2[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal2[i]/xExp[i])**2

					fObj[3] = fObj[3] + ((xCal3[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal3[i]/xExp[i])**2

			#print('fObj (TA == 2) : ', fObj, '\n')

			fObj = np.delete(fObj, 0) # deleta o primeiro elemento do array

			#print('fObj (index 0 deletado) : ', fObj, '\n')

			#pUltimo = find(fObj == max(fObj))		# Ponto do triângulo com maior erro 

			var_temp = np.where(fObj == fObj.max())	# Ponto do triângulo com maior erro 

			#print('var_temp = ', var_temp, '\n')

			var_temp = var_temp[0]

			print('var_temp = ', var_temp, '\n')

			tamanho = len(var_temp)

			#print('tamanho = ', tamanho, '\n')

			if (tamanho > 1):

				for i in range(tamanho-1):

					pUltimo = var_temp[0]
			else:

				pUltimo = var_temp[0]

			print('pUltimo = ', pUltimo, '\n')

			'''
			if (len(pUltimo) != 1):
				pUltimo = pUltimo[0]
			'''
	
			#pPrimeiro = find(fObj == min(fObj))		# Ponto do triângulo com menor erro
			var_temp = np.where(fObj == fObj.min())	# Ponto do triângulo com menor erro

			#print('var_temp = ', var_temp, '\n')

			var_temp = var_temp[0]

			#print('var_temp = ', var_temp, '\n')	

			tamanho = len(var_temp)

			#print('tamanho = ', tamanho, '\n')

			if (tamanho > 1):

				for i in range(tamanho-1):

					pPrimeiro = var_temp[0]

			else:

				pPrimeiro = var_temp[0]

			#print('pPrimeiro = ', pPrimeiro, '\n')
	
			'''
			if (len(pPrimeiro) !=1):
				pPrimeiro = pPrimeiro[0]
			'''
				
			if ((pUltimo == 1 and pPrimeiro == 2) or (pUltimo == 2 and pPrimeiro == 1)):

				pMeio = 3
				#print('pMeio = 3')
				
			elif ((pUltimo == 1 and pPrimeiro == 3) or (pUltimo == 3 and pPrimeiro == 1)):

				pMeio = 2
				#print('pMeio = 2')
				
			elif ((pUltimo == 2 and pPrimeiro == 3) or (pUltimo == 3 and pPrimeiro == 2)):

				pMeio = 1
				#print('pMeio = 1')
				
			fObjOrdenado = np.sort(fObj)			# Ordena função objetivo onde o primeiro
													# valor é o que possui menor erro

			#print('fObjOrdenado = ', fObjOrdenado, '\n')
			#print('fObj = ', fObj, '\n')

			fObjOrdenado = np.insert(fObjOrdenado, 0, 0)

			fObj = np.insert(fObj, 0, 0)

			#print('new fObjOrdenado = ', fObjOrdenado, '\n')
			#print('new fObj = ', fObj, '\n')

			#input('Digite para continuar \n')

			#FuncaoObj(iteracao,:) = fObjOrdenado

			cp = math.fabs((fObjOrdenado[3]- fObjOrdenado[1])/fObjOrdenado[3])

			print ('condicao de parada =  ', cp, '\n')
				
			# Condição de parada (a ser satisfeita)
			if (math.fabs((fObjOrdenado[3]- fObjOrdenado[1])/fObjOrdenado[3]) < tol):

				solucao = True

				break  
				
			if (iteracao == 500):

				print ('O algoritmo SIMPLEX não convergiu em 500 iterações.')
				break
				
			# Caso as condições não sejam satisfeitas, o programa abaixo é executado
			# Cálculo do centroide

			for i in range(1,4):

				if (i != pUltimo):

					P_Centroide[1] = P_Centroide[1] + P[i,1]

					P_Centroide[2] = P_Centroide[2] + P[i,2]
					
			P_Centroide = P_Centroide/2

			#print('P_Centroide = ', P_Centroide, '\n')
			#print('P = ', P[pUltimo], '\n')
			#print('alfa = ', alfa, '\n')
			
			# Reflexão
			P_Refletido[1:] = P_Centroide + alfa*(P_Centroide - P[pUltimo])

			fObjReflexao = 0

			#print('P_Refletido = ', P_Refletido, '\n')
			
			for i in range(1,tamDados-1):

				resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Refletido[1,1], P_Refletido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)

				yCal_Reflexao, xCal_Reflexao = resp[0], resp[1]

				#print('yCal_Reflexao = ', yCal_Reflexao, '\n')

				#print('xCal_Reflexao = ', xCal_Reflexao, '\n')

				print('######################## terminou 4 #########################', '\n')

				#input('Digite para continuar \n')
				
				if (TA == 1):

					fObjReflexao = fObjReflexao + ((yCal_Reflexao[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal_Reflexao[i]/yExp[i])**2
					
				if (TA == 2):

					fObjReflexao = fObjReflexao + ((xCal_Reflexao[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal_Reflexao[i]/xExp[i])**2
					
				if (TA == 0):

					fObjReflexao = fObjReflexao + ((yCal_Reflexao[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal_Reflexao[i]/yExp[i])**2 + ((xCal_Reflexao[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal_Reflexao[i]/xExp[i])**2

					
			# Análise da Reflexão
			# 1ª Condição: Reflexão
			if (fObjReflexao < fObjOrdenado[2] and fObjReflexao > fObjOrdenado[1]):

				print('1ª Condição: Reflexão')

				#input('Digite para continuar \n')

				P[pUltimo:] = P[pMeio:]

				P[pMeio:] = P_Refletido[1:]
					
			# 2ª Condição: Expansão
			elif (fObjReflexao <= fObjOrdenado[1]):

				print('2ª Condição: Reflexão')

				#input('Digite para continuar \n')

				P_Expandido = P_Centroide - gama*(P_Centroide - P[pUltimo:])

				fObjExpansao = 0
				
				for i in range(1, tamDados-1):

					resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Expandido[1,1], P_Expandido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)

					yCal_Expansao, xCal_Expansao = resp[0], resp[1]

					#print('yCal_Expansao = ', yCal_Expansao, '\n')
					#print('xCal_Expansao = ', xCal_Expansao, '\n')
					print('######################## terminou 5 #########################', '\n')

					#input('Digite para continuar \n')

					if (TA == 1):

						fObjExpansao = fObjExpansao + ((yCal_Expansao[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal_Expansao[i]/yExp[i])**2

					if (TA == 2 ):

						fObjExpansao = fObjExpansao + ((xCal_Expansao[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal_Expansao[i]/xExp[i])**2

					if (TA == 3):

						fObjExpansao = fObjExpansao + ((yCal_Expansao[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal_Expansao[i]/yExp[i])**2 + ((xCal_Expansao[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal_Expansao[i]/xExp[i])**2

				
				# Condições para o valor expandido
				if (fObjExpansao <= fObjReflexao):

					P[pUltimo:] = P_Expandido

				else:

					P[pUltimo:] = P_Refletido

			# 3ª Condição: Contração
			elif (fObjReflexao >= fObjOrdenado[2]):

				print('3ª Condição: Reflexão')

				#input('Digite para continuar \n')

				P_Contraido = P[pUltimo:] + beta*(P_Centroide - P[pUltimo:])

				fObjContracao = 0

				for i in range(1, tamDados-1):

					resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Contraido[1,1], P_Contraido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)

					yCal_Contracao, xCal_Contracao = resp[0], resp[1]

					#print('yCal_Contracao = ', yCal_Contracao, '\n')
					#print('xCal_Contracao = ', xCal_Contracao, '\n')
					print('######################## terminou 6 #########################', '\n')
	
					#input('Digite para continuar \n')

					if (TA == 1):

						fObjContracao = fObjContracao + ((yCal_Contracao[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal_Contracao[i]/yExp[i])**2
						
					if (TA == 2):

						fObjContracao = fObjContracao + ((xCal_Contracao[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal_Contracao[i]/xExp[i])**2
						
					if (TA == 3):

						fObjContracao = fObjContracao + ((yCal_Contracao[i] - yExp[i])/(1- yExp[i]))**2 + (1 - yCal_Contracao[i]/yExp[i])**2 + ((xCal_Contracao[i] - xExp[i])/(1- xExp[i]))**2 + (1 - xCal_Contracao[i]/xExp[i])**2

						
				# Condições para o valor contraído
				if (fObjContracao < fObjOrdenado[3]):

					P[pUltimo:] = P_Contraido
				
			# Caso a condição acima não seja satisfeita, deve-se fazer uma redução
			else:

				print('Caso a condição acima não seja satisfeita, deve-se fazer uma redução')

				#input('Digite para continuar \n')

				P[pMeio:] = (P[pMeio:] + P[pPrimeiro:])/2

				P[pUltimo:] = (P[pUltimo:] + P[pPrimeiro:])/2
			
		
		# MOSTRANDO OS RESULTADOS
		if (solucao == true):

			print('solucao == true', '\n')

			print('O algoritmo convergiu em ' , str(iteracao), ' iterações.', '\n')

			input('Digite para continuar \n')

			texto1 = 'O valor do parâmetro ka é %4.12f.\n'

			fprintf(texto1,P[1,1])

			texto2 = 'O valor do parâmetro kb é %4.12f.\n'

			fprintf(texto2,P[1,2])

			disp (strcat('O menor valor da função objetivo foi ' , num2str( fObj(1) ) , '.'))

			yCal = yCal1

			yExp

			xCal = xCal1

			xExp
	
	return(True)
