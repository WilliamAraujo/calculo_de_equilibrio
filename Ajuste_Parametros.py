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
	pPrimeiro = np.zeros(4)
	pUltimo = np.zeros(4)
	var_temp = np.zeros(4)
	fObj = np.zeros(4)
	resp = np.zeros(4)
	P_Centroide = np.zeros(4)
	P = np.zeros((4,4))
	P_Refletido = np.zeros((2,4))
	P_Expandido = np.zeros((2,4))
	P_Contraido = np.zeros((2,4))
	# Constantes
	alfa = 1
	beta = 1/2
	gama = 2
	sigma = 1/2

	print('Ajuste de Parametros', '\n')
	print('TA = ', TA, '\n')
	print('NC = ', NC, '\n')
	print('nc = ', nc, '\n')
	print('Tc = ', Tc, '\n')
	print('Pc = ', Pc, '\n')
	print('w = ', w, '\n')
	print('tol =  ', tol, '\n')
	print('Temperatura = ', Temperatura, '\n')
	print('Pressao = ', Pressao, '\n')
	print('yExp = ', yExp, '\n')
	print('Psat_soluto = ', Psat_soluto, '\n')
	print('xExp = ', xExp, '\n')
	print('tamDados(counter) = ', tamDados, '\n')
	print('Ka = ', Ka, '\n')
	print('Ka_check =  ', Ka_check, '\n')
	print('Kb = ', Kb, '\n')
	print('Kb_check = ', Kb_check, '\n')
	print('TEQ = ', TEQ, '\n')
	print('Vmolar_soluto = ', Vmolar_soluto, '\n')
	input('\n Dados carregados da interface......pressione entre para continuar \n')

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

	print('Ponto P = ', '\n', P, '\n')	
	input('\n verifica p ponto P \n')
			 
	tamDados = len(yExp)
	print('tamDados [yExp] = ', tamDados, '\n')

	# Calculo da Y e X pelo modelo (parâmetro)
	for i in range(1,tamDados):

		resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[1,1], P[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
		#print('resp = ', resp, '\n')
		yCal1, xCal1 = resp[0], resp[1]
		#print('yCal1 = ', yCal1, '\n')
		#print('xCall1 = ', xCal1, '\n')
		#print('terminou calculo de P[1,1] e P[1,2]', '\n')
		resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[2,1], P[2,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
		#print('resp = ', resp, '\n')
		yCal2, xCal2 = resp[0], resp[1]
		#print('yCal2 = ', yCal2, '\n')
		#print('xCal2 = ', xCal2, '\n')			
		#print('terminou calculo de P[2,1] e P[2,2]', '\n')

		resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[3,1], P[3,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
		#print('resp = ', resp, '\n')
		yCal3, xCal3 = resp[0], resp[1]
		#print('yCal3 = ', yCal3, '\n')
		#print('xCal3 = ', xCal3, '\n')
		#print('terminou calculo de P[3,1] e P[3,2]', '\n')		

		if (TA == 0):	# AJUSTANDO COM BASE EM Y
			#print('TA = 0,  AJUSTANDO COM BASE EM Y')
			#for i in range(1,tamDados):
			fObj[1] = fObj[1] + ((yCal1 - yExp[i])/(1- yExp[i]))**2 + (1 - yCal1/yExp[i])**2
			fObj[2] = fObj[2] + ((yCal2 - yExp[i])/(1- yExp[i]))**2 + (1 - yCal2/yExp[i])**2
			fObj[3] = fObj[3] + ((yCal3 - yExp[i])/(1- yExp[i]))**2 + (1 - yCal3/yExp[i])**2
					
		if (TA == 1):	# AJUSTANDO COM BASE EM X
			#print('TA = 1,  AJUSTANDO COM BASE EM X')
			#for i in range(1,tamDados):
			fObj[1] = fObj[1] + ((xCal1 - xExp[i])/(1- xExp[i]))**2 + (1 - xCal1/xExp[i])**2
			fObj[2] = fObj[2] + ((xCal2 - xExp[i])/(1- xExp[i]))**2 + (1 - xCal2/xExp[i])**2
			fObj[3] = fObj[3] + ((xCal3 - xExp[i])/(1- xExp[i]))**2 + (1 - xCal3/xExp[i])**2

		# Função objetivo	
		if (TA == 2):	# AJUSTANDO COM BASE EM X E Y
			#print('TA = 2,  AJUSTANDO COM BASE EM X e Y')
			#for i in range(1,tamDados-1):
			fObj[1] = fObj[1] + ((yCal1 - yExp[i])/(1-yExp[i]))**2 + (1 - yCal1/yExp[i])**2 + ((xCal1 - xExp[i])/(1- xExp[i]))**2 + (1 - xCal1/xExp[i])**2
			fObj[2] = fObj[2] + ((yCal2 - yExp[i])/(1-yExp[i]))**2 + (1 - yCal2/yExp[i])**2 + ((xCal2 - xExp[i])/(1- xExp[i]))**2 + (1 - xCal2/xExp[i])**2
			fObj[3] = fObj[3] + ((yCal3 - yExp[i])/(1-yExp[i]))**2 + (1 - yCal3/yExp[i])**2 + ((xCal3 - xExp[i])/(1- xExp[i]))**2 + (1 - xCal3/xExp[i])**2

	print('fObj : ', fObj, '\n')
	#input('\n Terminou de calcular a função objetivo para os três pontos...pressione entre para continuar \n')

	resp_ordenacao = ordenacao(fObj, P)
	#input('\n verificar se está ordenado...pressione entre para continuar \n')
	fObjOrdenado = resp_ordenacao[0]
	P_Ordenado = resp_ordenacao[1]

	print('new fObjOrdenado = ', fObjOrdenado, '\n')
	print('new P_Ordenado[0] = ', P_Ordenado[0], '\n')
	print('new P_Ordenado[1] = ', P_Ordenado[1], '\n')
	print('new P_Ordenado[2] = ', P_Ordenado[2], '\n')
	print('new P_Ordenado[3] = ', P_Ordenado[3], '\n')

	cp = math.fabs((fObjOrdenado[3]- fObjOrdenado[1])/fObjOrdenado[3])
	print ('condicao de parada =  ', cp, '\n')

	#input('\n realizou a ordenação da função objetivo...pressione entre para continuar \n')
				
	# Condição de parada (a ser satisfeita)
	if (math.fabs((fObjOrdenado[3]- fObjOrdenado[1])/fObjOrdenado[3]) < tol):
		print('solucao = True', '\n')
		solucao = True
		input('\n encontrou a minima função objetivo em 1 iteração...pressione entre para sair do programa \n')		

	# Caso as condições não sejam satisfeitas, o programa abaixo é executado
	#input('Caso as condições não sejam satisfeitas, o programa abaixo é executado \n')

	while(solucao == False):
		iteracao = iteracao + 1		
		# Cálculo do centroide
		#for i in range(1,4): # i = 1, 2, 3
		#	if (i != P_Ordenado[3]):

		#### REFLEXAO ####
		P_Centroide[1] = (P_Ordenado[1,1] + P_Ordenado[2,1])/2	# Ka
		P_Centroide[2] = (P_Ordenado[1,2] + P_Ordenado[2,2])/2	# Kb
		#print('P_Centroide/2 = ', P_Centroide, '\n')
		P_Refletido[1] = P_Centroide + alfa*(P_Centroide - P[3]) # criou um novo triângulo
		fObjReflexao = 0
		#print('P_Refletido = ', P_Refletido, '\n')
		#input('\n Vai calcular funcao objetivo para P_Refletido \n')			
		for i in range(1,tamDados):
			resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Refletido[1,1], P_Refletido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
			yCal_Reflexao, xCal_Reflexao = resp[0], resp[1]
			#print('yCal_Reflexao = ', yCal_Reflexao, '\n')
			#print('xCal_Reflexao = ', xCal_Reflexao, '\n')

			#print('terminou calculo de P_Refletido[1,1] e P_Refletido[1,2]', '\n')
				
			if (TA == 0):
				#print('TA = 0,  AJUSTANDO COM BASE EM Y')
				fObjReflexao = fObjReflexao + ((yCal_Reflexao-yExp[i])/(1-yExp[i]))**2 + (1-yCal_Reflexao/yExp[i])**2
					
			if (TA == 1):
				#print('TA = 1,  AJUSTANDO COM BASE EM X')
				fObjReflexao = fObjReflexao + ((xCal_Reflexao-xExp[i])/(1-xExp[i]))**2 + (1-xCal_Reflexao/xExp[i])**2
					
			if (TA == 2):
				#print('TA = 2,  AJUSTANDO COM BASE EM X e Y')
				fObjReflexao = fObjReflexao + ((yCal_Reflexao-yExp[i])/(1-yExp[i]))**2 + (1-yCal_Reflexao/yExp[i])**2 + ((xCal_Reflexao-xExp[i])/(1-xExp[i]))**2 + (1-xCal_Reflexao/xExp[i])**2

		#print('fObjReflexao : ', fObjReflexao, '\n')
		#print('fObjOrdenado = ', fObjOrdenado, '\n')
		#input('Agora vai comparar se fObjReflexao <= fObjOrdenado[1]...pressione entre para continuar \n')
					
		if (fObjReflexao <= fObjOrdenado[1]):

			#### Condição: Expansão ####
			#print('2ª Condição: Expansão')
			P_Expandido[1] = P_Centroide + gama*(P_Refletido[1] - P_Centroide) 
			#print('P_Expandido = ', P_Expandido, '\n')
			fObjExpansao = 0				
			for i in range(1, tamDados):
				resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Expandido[1,1], P_Expandido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
				yCal_Expansao, xCal_Expansao = resp[0], resp[1]
				#print('yCal_Expansao = ', yCal_Expansao, '\n')
				#print('xCal_Expansao = ', xCal_Expansao, '\n')
				#print('terminou calculo de P_Expandido[1,1] e P_Expandido[1,2]', '\n')

				if (TA == 0):
					#print('TA = 0,  AJUSTANDO COM BASE EM Y')
					fObjExpansao = fObjExpansao + ((yCal_Expansao-yExp[i])/(1-yExp[i]))**2 + (1-yCal_Expansao/yExp[i])**2

				if (TA == 1):
					#print('TA = 1,  AJUSTANDO COM BASE EM X')
					fObjExpansao = fObjExpansao + ((xCal_Expansao-xExp[i])/(1-xExp[i]))**2 + (1-xCal_Expansao/xExp[i])**2

				if (TA == 2):
					#print('TA = 2,  AJUSTANDO COM BASE EM X e Y')
					fObjExpansao = fObjExpansao + ((yCal_Expansao-yExp[i])/(1-yExp[i]))**2 + (1-yCal_Expansao/yExp[i])**2 + ((xCal_Expansao-xExp[i])/(1-xExp[i]))**2 + (1-xCal_Expansao/xExp[i])**2

			#print('fObjExpansao = ', fObjExpansao, '\n')
			#input('Fim da Expansao...pressione entrer para continuar \n')					
			#### Fim da Expansao ####

			#print('fObjReflexao = ', fObjReflexao, '\n')
			#print('fObjOrdenado = ', fObjOrdenado, '\n')
			#input('Agora vai comparar se fObjExpansao < fObjOrdenado[1]...pressione entre para continuar \n')

			if (fObjExpansao <= fObjOrdenado[1]):
				fObjOrdenado[3] = fObjOrdenado[1]
				fObjOrdenado[2] = fObjReflexao
				fObjOrdenado[1] = fObjExpansao
				P[3] = P[1]
				P[2] = P_Refletido[1]
				P[1] = P_Expandido[1]
				#print('antes', '\n')
				#print('fObjOrdenado = ', fObjOrdenado, '\n')
				#print('P = ', P, '\n')
				resp_ordenacao = ordenacao(fObjOrdenado, P)
				fObjOrdenado = resp_ordenacao[0]
				P_Ordenado = resp_ordenacao[1]
				#print('new fObjOrdenado = ', fObjOrdenado, '\n')
				#print('new P_Ordenado[0] = ', P_Ordenado[0], '\n')
				#print('new P_Ordenado[1] = ', P_Ordenado[1], '\n')
				#print('new P_Ordenado[2] = ', P_Ordenado[2], '\n')
				#print('new P_Ordenado[3] = ', P_Ordenado[3], '\n')
				#input('\n verificar se está ordenado...pressione entre para continuar \n')
						
			else:
				fObjOrdenado[3] = fObjReflexao
				P[3] = P_Refletido[1]
				#print('else: fObjExpansao > fObjReflexao', '\n')
				#print('P[3] = ', P[3], '\n')
				#input('condicao: fObjExpansao > fObjOrdenado[1] \n')
				#print('antes', '\n')
				#print('fObjOrdenado = ', fObjOrdenado, '\n')
				#print('P = ', P, '\n')
				resp_ordenacao = ordenacao(fObjOrdenado, P)
				fObjOrdenado = resp_ordenacao[0]
				P_Ordenado = resp_ordenacao[1]
				#print('new fObjOrdenado = ', fObjOrdenado, '\n')
				#print('new P_Ordenado[0] = ', P_Ordenado[0], '\n')
				#print('new P_Ordenado[1] = ', P_Ordenado[1], '\n')
				#print('new P_Ordenado[2] = ', P_Ordenado[2], '\n')
				#print('new P_Ordenado[3] = ', P_Ordenado[3], '\n')
				#input('\n verificar se está ordenado...pressione entre para continuar \n')					

		# Condição: Contração
		elif (fObjReflexao > fObjOrdenado[2]):
			#input('\n fObjReflexao > fObjOrdenado[2]...pressione entre para continuar \n')

			if (fObjReflexao < fObjOrdenado[3]):
				fObjOrdenado[3] = fObjReflexao
				P_Ordenado[3] = P_Refletido[1]
			
			#### Contracao ####				

			#print('3ª Condição: Contração')
			P_Contraido[1] = P_Centroide - beta*(P_Centroide - P[3])
			#print('P_Contraido = ', P_Contraido, '\n')
			#print('fObjOrdenado[2] = ', fObjOrdenado, '\n')
			fObjContracao = 0
			for i in range(1, tamDados):
				resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P_Contraido[1,1], P_Contraido[1,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
				yCal_Contracao, xCal_Contracao = resp[0], resp[1]
				#print('yCal_Contracao = ', yCal_Contracao, '\n')
				#print('xCal_Contracao = ', xCal_Contracao, '\n')
				#print('terminou calculo de P_Contraido[1,1] e P_Contraido[1,2]', '\n')

				if (TA == 0):
					#print('TA = 0,  AJUSTANDO COM BASE EM Y')
					fObjContracao = fObjContracao + ((yCal_Contracao-yExp[i])/(1-yExp[i]))**2 + (1-yCal_Contracao/yExp[i])**2
						
				if (TA == 1):
					#print('TA = 1,  AJUSTANDO COM BASE EM X')
					fObjContracao = fObjContracao + ((xCal_Contracao-xExp[i])/(1-xExp[i]))**2 + (1-xCal_Contracao/xExp[i])**2
						
				if (TA == 2):
					#print('TA = 2,  AJUSTANDO COM BASE EM X e Y')
					fObjContracao = fObjContracao + ((yCal_Contracao-yExp[i])/(1-yExp[i]))**2 + (1-yCal_Contracao/yExp[i])**2 + ((xCal_Contracao-xExp[i])/(1-xExp[i]))**2 + (1-xCal_Contracao/xExp[i])**2

			#### Fim da Contracao ###
		
			# Condições para o valor contraído
			print('fObjOrdenado[3] = ', fObjOrdenado[3], '\n')

			if (fObjContracao > fObjOrdenado[3]):
				input('calcula_novos_pontos...pressione entre para continuar \n')
				print('calcula novos pontos', '\n')
				P[2] = (P[2] + P[1])/2
				P[3] = (P[3] + P[1])/2

				for i in range(1, tamDados):
					resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[2,1], P[2,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
					yCal1_Novo, xCal1_Novo = resp[0], resp[1]
					#print('yCal1_Novo = ', yCal1_Novo, '\n')
					#print('xCal_Novo = ', xCal_Novo, '\n')
					#print('terminou calculo de P[2,1] e P[2,2]', '\n')

					resp = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, P[3,1], P[3,2], Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
					yCal2_Novo, xCal2_Novo = resp[0], resp[1]
					#print('yCal2_Novo = ', yCal2_Novo, '\n')
					#print('xCal2_Novo = ', xCal2_Novo, '\n')
					#print('terminou calculo de P[3,1] e P[3,2]', '\n')

					if (TA == 0):
						#print('TA = 0,  AJUSTANDO COM BASE EM Y')
						fObjNovo[2] = fObjNovo[2] + ((yCal1_Novo-yExp[i])/(1-yExp[i]))**2 + (1-yCal1_Novo/yExp[i])**2
						fObjNovo[3] = fObjNovo[3] + ((yCal2_Novo-yExp[i])/(1-yExp[i]))**2 + (1-yCal2_Novo/yExp[i])**2
					if (TA == 1):
						#print('TA = 1,  AJUSTANDO COM BASE EM X')
						fObjNovo[2] = fObjNovo[2] + ((xCal1_Novo-xExp[i])/(1-xExp[i]))**2 + (1-xCal1_Novo/xExp[i])**2
						fObjNovo[3] = fObjNovo[3] + ((xCal2_Novo-xExp[i])/(1-xExp[i]))**2 + (1-xCal2_Novo/xExp[i])**2
					if (TA == 2):
						#print('TA = 2,  AJUSTANDO COM BASE EM X e Y')
						fObjNovo[2] = fObjNovo[2] + ((yCal1_Novo-yExp[i])/(1-yExp[i]))**2 + (1-yCal1_Novo/yExp[i])**2 + ((xCal1_Novo-xExp[i])/(1-xExp[i]))**2 + (1-xCal1_Novo/xExp[i])**2
						fObjNovo[3] = fObjNovo[3] + ((yCal2_Novo-yExp[i])/(1-yExp[i]))**2 + (1-yCal2_Novo/yExp[i])**2 + ((xCal2_Novo-xExp[i])/(1-xExp[i]))**2 + (1-xCal2_Novo/xExp[i])**2

			else:
				fObjOrdenado[3] = fObjContracao
				P[3] = P_Contraido[1]
				#print('P = ', P, '\n')
				#print('fObjContracao : ', fObjContracao, '\n')
				#input('condicao de fObjContracao < fObjOrdenado[3]...pressione entre para continuar \n')

			#print('antes', '\n')
			#print('fObjOrdenado = ', fObjOrdenado, '\n')
			#print('P = ', P, '\n')
			resp_ordenacao = ordenacao(fObjOrdenado, P)
			fObjOrdenado = resp_ordenacao[0]
			P_Ordenado = resp_ordenacao[1]
			#print('new fObjOrdenado = ', fObjOrdenado, '\n')
			#print('new P_Ordenado[0] = ', P_Ordenado[0], '\n')
			#print('new P_Ordenado[1] = ', P_Ordenado[1], '\n')
			#print('new P_Ordenado[2] = ', P_Ordenado[2], '\n')
			#print('new P_Ordenado[3] = ', P_Ordenado[3], '\n')
			#input('\n verificar se está ordenado...pressione entre para continuar \n')


		# Condição: Reflexão
		#elif (fObjReflexao < fObjOrdenado[2] and fObjReflexao > fObjOrdenado[1]):
		else:
			print('Condição: Reflexão')
			fObjOrdenado[3] = fObjOrdenado[2]
			fObjOrdenado[2] = fObjReflexao
			P[3] = P[2]
			P[2] = P_Refletido[1]
			#input('condicao reflexão...pressione enter para continuar \n')

		cp = math.fabs((fObjOrdenado[3]- fObjOrdenado[1])/fObjOrdenado[3])
		print ('condicao de parada =  ', cp, '\n')

		#input('pressione enter para continuar \n')
				
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
			input('\n encontrou a minima função objetivo...pressione entre para sair do programa \n')

			for i in range(1,tamDados):

				resp1 = Calculo_Equilibrio.CalculaEquilibrioPR(2, TEQ, Pressao[i], Temperatura[i], Tc, Pc, w, Ka, Kb, Vmolar_soluto, Psat_soluto[i], Y, X, 1, 2)
				print('resp1 = ', resp1, '\n')
				print('pressao = ', Pressao[i], '\n')
				#yCal1, xCal1 = resp[0], resp[1]

				input('\n Está fazendo certo ?...pressione entre para sair do programa \n')

			break  
				
		if (iteracao == 500):
			print ('O algoritmo SIMPLEX não convergiu em 500 iterações.')	
			print ('condicao de parada =  ', cp, '\n')
			input('\n O algoritmo SIMPLEX não convergiu em 500 iterações. \n')
			break
		
		print('numero de iteracoes = ', iteracao, '\n')
	# MOSTRANDO OS RESULTADOS
	if (solucao == True):
		print('solucao == true', '\n')
		print('O algoritmo convergiu em ' , str(iteracao), ' iterações.', '\n')
		input('Digite para continuar \n')
		sys.exit()
		'''
		texto1 = 'O valor do parâmetro ka é %4.12f.\n'
		fprintf(texto1,P[1,1])
		texto2 = 'O valor do parâmetro kb é %4.12f.\n'
		fprintf(texto2,P[1,2])
		disp (strcat('O menor valor da função objetivo foi ' , num2str( fObj(1) ) , '.'))
		yCal = yCal1
		yExp
		xCal = xCal1
		xExp
		'''
	
	return(True)			


def ordenacao(fObj, P):
	for i in range(1,3):		# i = 1 e i = 2
		for j in range(i+1, 4):	# j = 2 e j = 3
			if(fObj[j] < fObj[i]):
				#print('fObj[i] = ', fObj[i], '  i = ', i, '  j = ', j, '\n')
				apoio1 = fObj[i]
				#print('apoio1 = ', apoio1, '  i = ', i, '  j = ', j, '\n')
				#print('-----------------', '\n')

				#print('fObj[j] = ', fObj[j], '  i = ', i, '  j = ', j, '\n')
				fObj[i] = fObj[j]
				#print('fObj[i] = ', fObj[i], '  i = ', i, '  j = ', j, '\n')
				#print('-----------------', '\n')

				#print('apoio1 = ', apoio1, '  i = ', i, '  j = ', j, '\n')
				fObj[j] = apoio1
				#print('fObj[j] = ', fObj[j], '  i = ', i, '  j = ', j, '\n')
				#print('-----------------', '\n')

				var1 = P[i,1]
				var2 = P[i,2]
				#print('var1 = P[', i, ',1] =  =>  ', var1,    '\n')
				#print('var2 = P[', i, ',2] =  =>  ', var2,    '\n')
				#print('----------------', '\n')

				P[i,1] = P[j,1]
				P[i,2] = P[j,2]
				#print('P[',i,'1] = P[', j, ',1] =  =>  ', P[i,1],    '\n')
				#print('P[',i,'2] = P[', j, ',2] =  =>  ', P[i,2],    '\n')
				#print('----------------', '\n')

				P[j,1] = var1
				P[j,2] = var2
				#print('P[',j,'1] = var1  =>  ', P[j,1],    '\n')
				#print('P[',j,'2] = var2  =>  ', P[j,2],    '\n')
				#print('----------------', '\n')
		
		#print('fObj = ', fObj, '\n')
		#print('P = ', P, '\n')

	return(fObj, P)
