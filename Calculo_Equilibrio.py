#!/usr/bin/python3.4

import math
import numpy as np
import Volume_Molar

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# FUNCAO DE CALCULOS DO EQUILIBRIO USANDO PR-EOS                          
# Matlab - Criado em: 19/02/2014                                                   
# Matlab - Ultima alteracao em: 14/03/2015
# Python - Criado em: 20/11/2016
# Python - Ultima alteracao em: 26/03/2017    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def	CalculaEquilibrioPR(NC, TEQ, pressao, temperatura, temperaturaCritica, pressaoCritica, fatorAcentrico, ka, kb, Vmolar_soluto, pressaoSublimacao, fracaoMolar_Y, fracaoMolar_X, NCS, OPCAO):

	# ENTRADAS DA FUNCAO
	NC										#	numero de componentes

	nc = NC + 1								#	numero de componentes + 1,
											# adaptação reutilizar código do Matlab

	TEQ										#	tipo de equilibrio:
											# (1:ESL ou 2:ESV ou 3: ELL ou 4: ELV)

	P = pressao								#	Pressao do sistema (bar)

	T = temperatura							#	Temperatura do sistema (K)

	Tc = temperaturaCritica					#	Temperatura critica (K) 

	Pc = pressaoCritica						#	Pressao critica (bar) 

	w = fatorAcentrico						#	Fator acêntrico 

	ka										#	Parametro de interacao ka entre 
											#	componentes da mistura

	kb 										#	Parametro de interacao kb entre
											# componentes da mistura

	Vmolar_soluto							#	Volume molar do soluto (L/mol) 

	Psat_soluto = pressaoSublimacao			#	Pressao de saturacao do soluto (bar)
											#	na T do sistema

	Y = fracaoMolar_Y						#	Fracao molar em base livre do soluto
											#	(soluto sólido no equilíbrio sólido-fluido)

	X = fracaoMolar_X						#	Fracao molar em base livre do componente 1
											#	(para equilíbrio ELL ou ELV)

	NCS 									#	Número de componentes sólidos
	
	
	R = 0.0831434		# EM BAR.L/K.mol
			
	# Inicializacao dos vetores com zeros
	Km = np.zeros(nc)
	alfa = np.zeros(nc)
	y = np.zeros(nc)
	x = np.zeros(nc)
	k = np.zeros(nc)
	Sx = np.zeros(nc)
	am = np.zeros(nc)
	bm = np.zeros(nc)
	A = np.zeros(nc)
	B = np.zeros(nc)
	Vm = np.zeros(nc)
	SA = np.zeros(nc)
	SB = np.zeros(nc)

	# Inicializacao das matrizes com zeros
	a    = np.zeros((nc,nc))
	b    = np.zeros((nc,nc))
	F    = np.zeros((nc,nc))
	LNFI = np.zeros((nc,nc))

	# Cálculo a(i,i) e b(i,i) 
	for i in range(1, nc):

		Km[i] = 0.37464+1.54226*w[i]-0.26992*(w[i]**2)  

		alfa[i] = (1 + Km[i]*(1-math.sqrt(T/Tc[i])))**2

		a[i,i] = 0.45724 * ((R*Tc[i])**2)*(alfa[i]/Pc[i])

		b[i,i] = 0.07780*R*(Tc[i]/Pc[i])

	#print('Km = ', Km, '\n')
	#print('alfa = ', alfa, '\n')
	#print('a = ', a, '\n')
	#print('b = ', b, '\n')
	#print('Ka = ', ka, '\n')
	#print('Kb = ', kb, '\n')

	# Cálculo a(i,j) e b(i,j) 
	for i in range(1, nc-1): 

		for j in range(i+1, nc): 

			if(OPCAO == 1):	

				#print('OPCAO 1 ? ==>  ', OPCAO, '\n')

				a[i,j] = (1-ka[i,j])*math.sqrt(a[i,i]*a[j,j])

				b[i,j] = (1-kb[i,j])*((b[i,i]+b[j,j])/2)

			else:

				#print('OPCAO 2 ? ==>  ', OPCAO, '\n')

				a[i,j] = (1-ka)*math.sqrt(a[i,i]*a[j,j])

				b[i,j] = (1-kb)*((b[i,i]+b[j,j])/2)
			
			a[j,i] = a[i,j]  

			b[j,i] = b[i,j]

	#print('a(i,j)', '\n', a, '\n')
	#print('b(i,j)', '\n', b, '\n')

	# ESTIMATIVA INICIAL DE x1, k1  
	# k = coeficiente de distribuicao; 
	# x = fracao molar na fase pesada; 
	# y = fracao molar na fase leve;
	
	if (TEQ == 1 or TEQ == 2):		# Estimativa inicial para ESL ou ESV

		y[NC] = 0.001/NCS	
	
		x[NC] = 1/NCS				# zerando os valores de x pra poder manter o algoritmo
									# calculando fugacidade de todos os componentes em todas
									# as fases, msm nao sendo necessario em ESL e ESV
						
		for i in range((NC-NCS+1), nc-1):

			y[i] = y[NC]

			x[i] = x[NC]
			
		for i in range(1, nc-NCS):

			y[i] = Y[i]*(1-0.001)
		
		x[1] = 0

		for i in range(2, nc-NCS):

			x[i] = x[i-1]

	if (TEQ == 3 or TEQ == 4):		# Estimativa inicial para ELL ou ELV

		if(NC == 2):

			X[2] = 1
	
		x[1] = 0.001

		k[1] = 0.999/x[1]

		Sx = 1-x[1]
		
		k[2] = (1-x[1]*k[1])/Sx
		
		for i in range(3, nc):

			k[i] = k[i-1]

		#print('Sx = ', Sx, '\n')
		#print('X = ', X, '\n')

		for i in range(2,nc):

			x[i] = Sx*X[i]
		
		for i in range(1,nc):

			y[i] = x[i]*k[i]

	#print('componentes_Solidos = ', NCS, '\n')
	#print('y = ', y, '\n')
	#print('x = ', x, '\n')
	#print('Y = ', Y, '\n')
	#print('X = ', X, '\n')
	#print('k = ', k, '\n')
	#print('Sx = ', Sx, '\n') 
	
	# INICIO DO PROCESSO ITERATIVO
	solucao = False

	iteracao = 0

	while (solucao == False):

		iteracao = iteracao + 1

		#print("iteracao.....................   ", iteracao, '\n')         
		
		# CALCULO DO PARAMETRO A E B DE MISTURA --> Regra de Mistura Classica
		# 1 --> fase pesada
		# 2 --> fase leve

		for j in range(1, 3): # j = 1 e j =2

			am[j] = 0

			bm[j] = 0
		
		# cálculo dos parâmetros am e bm das fases 1 e 2.
		for i in range(1,nc):	

			for j in range(1,nc):

				am[1] = am[1] + x[i]*x[j]*a[i,j]

				bm[1] = bm[1] + x[i]*x[j]*b[i,j]

				am[2] = am[2] + y[i]*y[j]*a[i,j]

				bm[2] = bm[2] + y[i]*y[j]*b[i,j]  

		#print('am = ', am, '\n')
		#print('bm = ', bm, '\n')
		#print('P = ', P, '\n')
		#print('T = ', T, '\n')

		# Cálculo do volume molar das fases (fase 1 e fase 2)	  
		for i in range(1, 3):

			A[i] = (am[i]*P)/(R*T)**2

			B[i] = (bm[i]*P)/(R*T)

		#print('A = ', A, '\n')
		#print('B = ', B, '\n')
		
		Vm = Volume_Molar.CalculaVolumeMolarEOS(nc, A, B, TEQ, R, T, P)

		#print("Vm =  ", Vm)

		# float( '%0.3g' % (Vm))  # número float com 2 casas decimais
		
		# CALCULO DA FUGACIDADE DO SOLUTO NA FASE SOLIDA
		if (TEQ == 1 or TEQ == 2):

			for i in range(NC-NCS+1,nc):

				F[i,1] = Psat_soluto[i]*math.exp((Vmolar_soluto[i]*(P-Psat_soluto[i]))/(R*T))

			#print(F)
			
		# CALCULO DO COEFICIENTE DE FUGACIDADE E FUGACIDADE NAS FASES FLUIDAS
		# 2 eh a fase leve e 1 eh a fase pesada!
		
		vol_ideal = R*T/P

		#print('vol_ideal = ', vol_ideal)
	
		for i in range(1,nc):

			SA[1] = 0
			SB[1] = 0
			SA[2] = 0
			SB[2] = 0

			for j in range(1,nc):

				SA[1] = SA[1] + x[j]*a[i,j]

				SA[2] = SA[2] + y[j]*a[i,j]

				SB[1] = SB[1] + x[j]*b[i,j]

				SB[2] = SB[2] + y[j]*b[i,j]
			
			for j in range(1,3):

				apoio = R*T*bm[j]*(Vm[j]+bm[j]*(1+math.sqrt(2)))*(Vm[j]+bm[j]*(1-math.sqrt(2)))

				apoio = -2*am[j]*Vm[j]*(SB[j]-bm[j])/apoio

				apoio = apoio+(2*(SB[j]-bm[j])/(Vm[j]-bm[j]))

				sos = (Vm[j]+bm[j]*(1+math.sqrt(2)))/(Vm[j]+bm[j]*(1-math.sqrt(2)))

				sos = math.log(sos)*(2*am[j]*SB[j]-am[j]*bm[j]-2*bm[j]*SA[j])

				sos = sos/(2*math.sqrt(2)*R*T*(bm[j])**2)

				sos = (P*Vm[j])/(R*T)-1 + math.log(vol_ideal/(Vm[j]-bm[j])) + sos	
		
				LNFI[i,j] = sos + apoio
					
			# CALCULO DA FUGACIDADE NA FASE FLUIDA PARA EQULIBRIO ELV E ELL
			if (TEQ == 3 or TEQ == 4):

				#print('P = ', P, '\n')
				#print('x = ', x[i], '\n')
				#print('y = ', y[i], '\n')

				F[i,1] = P*x[i]*math.exp(LNFI[i,1])

				F[i,2] = P*y[i]*math.exp(LNFI[i,2])
		
		#print('SA = ', SA, '\n')
		#print('SB = ', SB, '\n')
		#print('apoio = ', apoio, '\n')
		#print('sos = ', sos, '\n')
		#print('LNFI = ', LNFI, '\n')
		#print('F (ELV/ELL) = ', F, '\n')

		# CALCULO DA FUGACIDADE NA FASE FLUIDA PARA EQULIBRIO ESV E ESL
		if (TEQ == 1 or TEQ == 2):

			for i in range(NC-NCS+1,nc):

				F[i,2] = P*y[i]*math.exp(LNFI[i,2])
					
		# CONDICAO DE ISOFUGACIDADE
		FO = 0

		if (TEQ == 1 or TEQ == 2):

			for i in range(NC-NCS+1,nc):

				FO = FO + (math.log(F[i,2]/F[i,1]))**2
			
		if (TEQ == 3 or TEQ == 4):

			for i in range(1,nc):

				FO = FO + (math.log(F[i,2]/F[i,1]))**2
			
		if (FO <= 1e-12):

			solucao = True
			
		# NOVA ESTIMATIVA DE x1 e y1
		if (solucao == False):

			if (TEQ == 1 or TEQ == 2):	# Nova estimativa de y(soluto)
										# para ESL e ESV
				soma = 0

				for i in range(NC-NCS+1,nc):

					y[i] = y[i]*(F[i,1]/F[i,2])

					# MODIFICADO EM MAIO DE 2015: INICIO (PARA NAO DEIXAR FRACAO
					# MOLAR ATINGIR VALORES MENORES QUE ZERO E MAIORES QUE 1

					if (y[i] > 1):

						y[i] = y[i]/(y[i]+1)

					soma = soma + y[i]
					
				#print("soma = ", soma)
									
				for i in range(1,nc-NCS):

					y[i] = Y[i]*(1.0-soma)
				
			if (TEQ == 3 or TEQ == 4): # Nova estimativa de x(1) para ELL e ELV
			
				for i in range(1,nc):

					k[i] = k[i]*(F[i,1]/F[i,2])
					
				apoio = 0

				for i in range(2,nc):

					apoio = apoio + X[i]*(k[i]-1)

				apoio = (1-k[1])/apoio

				x[1] = 1/(apoio +1)
				
				if (x[1] < 0):

					x[1] = x[1]**2

					if x[1] < 1e-13:

						x[1] = 1e-13

					k[1] = 0.999/x[1]

					Sx = 1 - x[1]

					k[2] = (1-(x[1]*k[1]))/Sx
					
					for i in range(3,nc):

						k[i] = k[i-1]
				
				if x[1] > 1:

					x[1] = x[1]**(1/2)

					if (1-x[1]) < 1e-8:

						x[1] = 0.9999999

					k[1] = 0.999/x[1]

					Sx = 1-x[1]

					k[2] = (1-x[1]*k[1])/Sx
					
					for i in range(3,nc):

						k[i] = k[i-1]
						
				if (math.fabs(1-k[1]) < 1e-5):

					x[1] = 0.999*x[1]

					k[1] = 0.999/x[1]

					Sx = 1-x[1]

					k[2] = (1-x[1]*k[1])/Sx
					
					for i in range(3,nc):

						k[i] = k[i-1]
						
				Sx = 1-x[1]

				for i in range(2,nc):

					x[i] = Sx*X[i]
					
				for i in range(1,nc):

					y[i] = k[i]*x[i]

		#print("x = ")
		#print(x)
		#print("y = ")
		#print(y)

		#%% CONDICAO DE PARADA: 200 ITERACOES
		if iteracao > 200:

			print ('O algoritmo nao convergiu em 200 iteracoes')
			print('A = ', A, '\n')
			print('B = ', B, '\n')
			print("Vm =  ", Vm, '\n')
			print('tolerancia = ', math.fabs(1-k[1]), '\n')
			print('F =  ', F, '\n')
			input('Digite para continuar \n')
			break

	print("iteracao -> calculo Equilibrio....   ", iteracao, '\n')	
	#print('### Volume Molar ###')
	return (x,y,iteracao)
