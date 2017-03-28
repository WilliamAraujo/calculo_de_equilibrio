#!/usr/bin/env python3.4
#############################################################################
## Ajuste de Parâmetros
## Faculdade de Engenharia de Alimentos - FEA / UNICAMP
## Prof. Dr. Fernando Antônio Cabral
## email: cabral@fea.unicamp.br
## Versão 1: 05 de Fevereiro de 2017
## Versão 2: 27 de Fevereiro de 2017
## versão 3: 17 de Março de 2017
#############################################################################

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import (QIcon, QKeySequence)
#from PyQt5.QtWidgets import QFileDialog
import sys
import time
import numpy as np
from datetime import datetime
import Calculo_Equilibrio
import Ajuste_Parametros
from DistUpgrade.DistUpgradeViewText import readline
from ufw.util import open_file_read
from builtins import int
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

Ui_Form1, QtBaseClass = uic.loadUiType("calculoEquilibrio.ui")
Ui_Form2, QtBaseClass = uic.loadUiType("ajusteParametros.ui")

class app_calculoEquilibrio(QDialog):

	def __init__(self, parent):
		super(app_calculoEquilibrio, self).__init__(parent)
		self.mainLayout = Ui_Form1()
		self.mainLayout.setupUi(self)		
		self.mainLayout.button_Calcular.clicked.connect(self.calcular)
		self.mainLayout.button_AbrirArquivo.clicked.connect(self.abrirArquivo)
		self.mainLayout.button_SalvarArquivo.clicked.connect(self.salvarArquivo)
		self.mainLayout.button_Informacoes.clicked.connect(self.informacoes)

	#############################################################################################	
	@pyqtSlot()
	def calcular(self):

		# Limpando Relatorio
		self.mainLayout.listWidget_Relatorio.clear()

		# Leitura do Número de Componentes
		NC = int(self.mainLayout.lineEdit_NumeroComponentes.text())
		nc = NC + 1	# Número de componentes + 1: para ficar compativel com Matlab

		# Leitura da Temperatura
		temperatura = float(self.mainLayout.lineEdit_Temperatura.text())

		# Leitura da Pressão
		pressao = float(self.mainLayout.lineEdit_Pressao.text())

		# Númenro de componentes sólidos
		NCS = int(self.mainLayout.lineEdit_ComponentesSolidos.text())

		# Leitura do tipo de Equilibrio
		TEQ = self.mainLayout.comboBox_TipoEquilibrio.currentIndex()
		if   TEQ == 0: tipoEquilibrio = 'Sólido-Vapor'
		elif TEQ == 1: tipoEquilibrio = 'Sólido-Líquido'
		elif TEQ == 2: tipoEquilibrio = 'Líquido-Líquido'
		elif TEQ == 3: tipoEquilibrio = 'Líquido-Vapor'
		
		# Declaracao e Inicializando dos vetores
		nomeComponente = np.zeros(nc, dtype = ('a30'))	# String de 30 caracteres
		temperaturaCritica = np.zeros(nc)
		pressaoCritica = np.zeros(nc)
		fatorAcentrico = np.zeros(nc)
		fracaoMolar_X = np.zeros(nc)
		fracaoMolar_Y = np.zeros(nc)
		pressaoSublimacao = np.zeros(nc)
		Vmolar_soluto = np.zeros(nc)
		resposta_calculo = np.zeros((3))

		# Leitura da Tabela ---> Lendo apenas as colunas
		for i in range(1, nc):
			index_i = i-1	
			print('i ', str(i))
			print('index_i ', str(index_i))		
			nomeComponente[i]		= self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 0).text()
			temperaturaCritica[i]	= float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 1).text())
			pressaoCritica[i]		= float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 2).text())
			fatorAcentrico[i]		= float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 3).text())
			fracaoMolar_X[i]		= float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 4).text())
			fracaoMolar_Y[i]		= float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 5).text())
			pressaoSublimacao[i]	= float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 6).text())
			Vmolar_soluto[i]		= float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i, 7).text())
		print('passou-1')
		# Leitura ka
		ka = np.zeros((nc, nc))
		for i in range(1, nc):		# linhas
			index_i = i-1
			for j in range(1, nc):	# colunas
				index_j = j-1
				ka[i][j] = float(self.mainLayout.tableWidget_Kaij.item(index_i, index_j).text())

		# Leitura Kbij
		kb = np.zeros((nc,nc))
		for i in range(1, nc):		# linhas
			index_i = i-1
			for j in range(1, nc):	# colunas
				index_j = j-1
				kb[i][j] = float(self.mainLayout.tableWidget_Kbij.item(index_i, index_j).text())


		self.mainLayout.listWidget_Relatorio.addItem(datetime.now().strftime('%d/%m/%Y    %H:%m:%S'))
		self.mainLayout.listWidget_Relatorio.addItem("Cálculo de Equilíbrio")
		self.mainLayout.listWidget_Relatorio.addItem("Tipo de Equilibrio = " + tipoEquilibrio)
		self.mainLayout.listWidget_Relatorio.addItem("Número de Componentes = " + str(NC))
		self.mainLayout.listWidget_Relatorio.addItem("Temperatura = " + str(temperatura))
		self.mainLayout.listWidget_Relatorio.addItem("Pressão = " + str(pressao))

		print('nomeComponente = ', nomeComponente, '\n')
		print('temperaturaCritica = ', temperaturaCritica, '\n')
		print('pressaoCritica = ', pressaoCritica, '\n')
		print('fatorAcentrico = ', fatorAcentrico, '\n')
		print('fracaoMolar_X = ', fracaoMolar_X, '\n')
		print('fracaoMolar_Y = ', fracaoMolar_Y, '\n')
		print('pressaoSublimacao = ', pressaoSublimacao, '\n')
		print('Vmolar_soluto = ', Vmolar_soluto, '\n') 
		print('Kaij = ', '\n', ka, '\n')
		print('Kbij = ', '\n', kb, '\n')
		
		# Cálculo de Equilíbrio
		#resposta_calculo = Calculo_Equilibrio.CalculaEquilibrioPR(numeroComponentes_int, nc, pressao_float, temperatura_float, pressaoSublimacao, tabela_Kaij, tabela_Kbij, TEQ, temperaturaCritica, pressaoCritica, fatorAcentrico, Vmolar_soluto, fracaoMolar_Y, fracaoMolar_X, NCS_int)
		OPCAO = 1
		resposta_calculo = Calculo_Equilibrio.CalculaEquilibrioPR(NC, TEQ, pressao, temperatura, temperaturaCritica, pressaoCritica, fatorAcentrico, ka, kb, Vmolar_soluto, pressaoSublimacao, fracaoMolar_Y, fracaoMolar_X, NCS, OPCAO)

		print('Calculo do Equilíbrio: ', '\n', 'x = ', resposta_calculo[0], '\n', 'y = ', '\n', resposta_calculo[1], '\n', 'iteração = ', resposta_calculo[2], '\n')
        
	#############################################################################################	
	def procura(self,data):

		length = len(data)
		dados = []

		for i in range(length):
			dados.append(data[i])  # armazena em um vetor

		for i in range(length):
			encontre = dados[i]

			if(encontre == '='):   # procura pelo caracter '='
				temp = dados[i+1:length-1]
				tamanho = len(temp)
				resultado = ''

				for i in range(tamanho):
					resultado = resultado + temp[i]

		return (resultado)
        
	#############################################################################################	
	@pyqtSlot()
	def abrirArquivo(self):
		
		fname = QFileDialog.getOpenFileName(self, 'Open file (*.txt)', '/home/dell/Documents/')
		
		f = open(fname[0],'r')
	
		with f:

			nomeMedida = f.readline()

			data = f.readline()
			resposta = self.procura(data)
			print(resposta)

			horario = f.readline()
			resposta = self.procura(horario)
			print(resposta)

			# Leitura do Número de Componentes
			numeroComponentes = f.readline()
			resposta = self.procura(numeroComponentes)
			self.mainLayout.lineEdit_NumeroComponentes.setText(resposta)
			numeroComponentes_int = int(resposta)

			# Leitura da Temperatura 
			temperatura = f.readline()
			resposta = self.procura(temperatura) 
			self.mainLayout.lineEdit_Temperatura.setText(resposta)
			    
			# Leitura da Pressão
			pressao = f.readline()
			resposta = self.procura(pressao)
			self.mainLayout.lineEdit_Pressao.setText(resposta)

			# Númenro de componentes sólidos
			componentesSolidos = f.readline()
			resposta = self.procura(componentesSolidos)
			self.mainLayout.lineEdit_ComponentesSolidos.setText(resposta)

			# Leitura do tipo de Equilibrio
			TEQ = f.readline() 
			resposta = self.procura(TEQ) 
			print(resposta)
			self.mainLayout.comboBox_TipoEquilibrio.setCurrentIndex(int(resposta))

			# Leitura da Tabela ---> Lendo apenas as colunas    
			print(f.readline()) 
			for i in range(numeroComponentes_int):
				for j in range(8):
					leitura_tabela = f.readline()
					print(leitura_tabela)
					self.mainLayout.tableWidget_PropriedadesCriticas.setItem(i, j, QTableWidgetItem(leitura_tabela))

			# Leitura Kaij
			print(f.readline())
			for i in range(10):     # linhas
				for j in range(10): # colunas
					tabela_Kaij = f.readline()
					self.mainLayout.tableWidget_Kaij.setItem(i, j, QTableWidgetItem(tabela_Kaij))

			# Leitura Kbij
			print(f.readline())
			for i in range(10):     # linhas
				for j in range(10): # colunas
					tabela_Kbij = f.readline()
					self.mainLayout.tableWidget_Kbij.setItem(i, j, QTableWidgetItem(tabela_Kbij))
			f.close()

	#############################################################################################
	@pyqtSlot()
	def salvarArquivo(self):

		self.mainLayout.listWidget_Relatorio.addItem('Salvar Arquivo')
		#name = QFileDialog.getSaveFileName(self, 'Save File')
		name = QFileDialog.getSaveFileName(self, 'Save File','/home/dell/Documents/test_save_file')
		print(name)
		file = open(name[0],'w')
		file.write('---  Calculo de Equilibrio  ---' +'\n')
		file.write('Data=' + '2017' +'\n')
		file.write('Horario=' + '02h57min' +'\n')

		# Leitura do Número de Componentes
		numeroComponentes = self.mainLayout.lineEdit_NumeroComponentes.text()
		numeroComponentes_int = int(numeroComponentes)
		file.write('numeroComponentes=' + numeroComponentes + '\n')

		# Leitura da Temperatura 
		temperatura = self.mainLayout.lineEdit_Temperatura.text()
		file.write('temperatura=' + temperatura + '\n')

		# Leitura da Pressão
		pressao = self.mainLayout.lineEdit_Pressao.text()
		file.write('pressao=' + pressao + '\n')

		# Númenro de componentes sólidos
		NCS = self.mainLayout.lineEdit_ComponentesSolidos.text()
		file.write('NumeroComponentesSolidos=' + NCS + '\n')

		# Leitura do tipo de Equilibrio
		tipoEquilibrio = self.mainLayout.comboBox_TipoEquilibrio.currentText()
		file.write('tipoEquilibrio=' + tipoEquilibrio + '\n')

		# Leitura da Tabela ---> Lendo apenas as colunas  
		file.write('--- Leitura dos parametros dos componentes ---' + '\n')

		for i in range(numeroComponentes_int):
			for j in range(8):
				tabela_parametros = self.mainLayout.tableWidget_PropriedadesCriticas.item(i,j).text()
				file.write(tabela_parametros + '\n')

		# Leitura Kaij
		file.write('--- Leitura dos parametros Kaij ---' + '\n')
		for i in range(10):     # linhas
			for j in range(10): # colunas
				tabela_Kaij = self.mainLayout.tableWidget_Kaij.item(i,j).text()
				file.write(tabela_Kaij + '\n')

		# Leitura Kbij
		file.write('--- Leitura dos parametros Kbij ---' + '\n')
		for i in range(10):     # linhas
			for j in range(10): # colunas
				tabela_Kbij = self.mainLayout.tableWidget_Kbij.item(i,j).text()
				file.write(tabela_Kbij + '\n')

		file.close()

	#############################################################################################
	@pyqtSlot()
	def informacoes(self):
		print("Informacoes")

#################################################################################################
class app_ajusteParametros(QDialog):

	def __init__(self, parent):
		super(app_ajusteParametros, self).__init__(parent)
		self.mainLayout = Ui_Form2()
		self.mainLayout.setupUi(self)
		#self.mainLayout = loadUi('ajusteParametros.ui',self)
		self.mainLayout.listWidget_Relatorio.addItem("Ajuste de Parametros")
		self.mainLayout.button_Calcular.clicked.connect(self.calcular)
		self.mainLayout.button_AbrirArquivo.clicked.connect(self.abrirArquivo)
		self.mainLayout.button_SalvarArquivo.clicked.connect(self.salvarArquivo)
		self.mainLayout.button_Informacoes.clicked.connect(self.informacoes)
		self.mainLayout.tableWidget_AjusteParametros.itemChanged.connect(self.adjustTableSize)
		self.mainLayout.tableWidget_PropriedadesCriticas.itemChanged.connect(self.adjustTableSize)
		# Fits initial contents
		self.adjustTableSize()
		self.mainLayout.tableWidget_AjusteParametros.resizeColumnsToContents()
		'''
		self.mainLayout.tableWidget_PropriedadesCriticas.setColumnWidth(0, 70)
		self.mainLayout.tableWidget_PropriedadesCriticas.setColumnWidth(1, 70)
		self.mainLayout.tableWidget_PropriedadesCriticas.setColumnWidth(2, 70)
		self.mainLayout.tableWidget_PropriedadesCriticas.setColumnWidth(3, 130)
		self.mainLayout.tableWidget_PropriedadesCriticas.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
		self.mainLayout.tableWidget_PropriedadesCriticas.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
		self.mainLayout.tableWidget_PropriedadesCriticas.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
		self.mainLayout.tableWidget_PropriedadesCriticas.horizontalHeaderItem(3).setTextAlignment(Qt.AlignHCenter)
		
		self.mainLayout.tableWidget_AjusteParametros.setWordWrap(True)
    	'''       
	@pyqtSlot()
	def adjustTableSize(self):
		#print('Adjusting table size!')
		self.mainLayout.tableWidget_AjusteParametros.resizeColumnsToContents()
		self.mainLayout.tableWidget_PropriedadesCriticas.resizeColumnsToContents()
		
	@pyqtSlot()
	def calcular(self):

		print('calcular')

		# Limpando Relatorio
		self.mainLayout.listWidget_Relatorio.clear()

		# Leitura do desvio
		desvio = self.mainLayout.lineEdit_Desvio.text()
		desvio_float = float(desvio)

		# Leitura do parametro Ka
		Ka = self.mainLayout.lineEdit_Ka.text()
		Ka_float = float(Ka)

		# Check se Ka vai ser fixo
		Ka_check = str(self.mainLayout.checkBox_Ka.isChecked())

		# Leitura do parametro Kb
		Kb = self.mainLayout.lineEdit_Kb.text()
		Kb_float = float(Kb)

		# Check se Kb vai ser fixo
		Kb_check = str(self.mainLayout.checkBox_Kb.isChecked())

		# Leitura da Função Objetivo
		fObj = self.mainLayout.comboBox_FuncaoObjetivo.currentIndex()
		if   fObj == 0: funcaoObjetivo = 'Pontos x & y'
		elif fObj == 1: funcaoObjetivo = 'Pontos y'
		elif fObj == 2: funcaoObjetivo = 'Pontos x'

		# Leitura do tipo de Equilibrio
		TEQ = self.mainLayout.comboBox_TipoEquilibrio.currentIndex()
		if   TEQ == 0: tipoEquilibrio = 'Sólido  - Vapor'
		elif TEQ == 1: tipoEquilibrio = 'Sólido  - Líquido'
		elif TEQ == 2: tipoEquilibrio = 'Líquido - Líquido'
		elif TEQ == 3: tipoEquilibrio = 'Líquido - Vapor'

		# Declaracao e Inicializando dos vetores
		nomeComponente = np.zeros(3, dtype = ('a30'))	# String de 30 caracteres
		temperaturaCritica = np.zeros(3)
		pressaoCritica = np.zeros(3)
		fatorAcentrico = np.zeros(3)
		Vmolar_soluto = np.zeros(3)

		# Leitura da Tabela (Propriedades Críticas) ---> Lendo apenas as colunas
		for i in range(1, 3):
			index_i = i - 1
			temperaturaCritica[i] = float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i,0).text())
			pressaoCritica[i]     = float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i,1).text())
			fatorAcentrico[i]     = float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i,2).text())
			Vmolar_soluto[i]      = float(self.mainLayout.tableWidget_PropriedadesCriticas.item(index_i,3).text())

		# ajusta o tamanho do vetor conforme os pontos experimentais selecionados
		counter = 0
		pontos = 0
		for i in range(20):
			pontos = int(self.mainLayout.tableWidget_AjusteParametros.item(i,0).text())
			if(pontos == 1):
				counter = counter + 1
			else: pass  
      
		pontosExp = np.zeros(counter+1)
		temperatura = np.zeros(counter+1)
		pressao = np.zeros(counter+1)
		x2 = np.zeros(counter+1)
		y2 = np.zeros(counter+1)
		pressao_sublimacao = np.zeros(counter+1)

		# Leitura da Tabela (Ajuste de Parametros) --> Lendo apenas as colunas
		j = 1
		for i in range(20):
			pontosExp = int(self.mainLayout.tableWidget_AjusteParametros.item(i,0).text())
			#print('pontosExp = ', pontosExp, '\n')
			if (pontosExp == 1):
				print('j = ', j, '\n')
				temperatura[j]        = float(self.mainLayout.tableWidget_AjusteParametros.item(i,1).text())
				pressao[j]            = float(self.mainLayout.tableWidget_AjusteParametros.item(i,2).text())
				x2[j]                 = float(self.mainLayout.tableWidget_AjusteParametros.item(i,3).text())
				y2[j]                 = float(self.mainLayout.tableWidget_AjusteParametros.item(i,4).text())
				pressao_sublimacao[j] = float(self.mainLayout.tableWidget_AjusteParametros.item(i,5).text())
				j = j + 1

		self.mainLayout.listWidget_Relatorio.addItem(datetime.now().strftime('%d/%m/%Y    %H:%m:%S'))
		self.mainLayout.listWidget_Relatorio.addItem("Ajuste de Parametros")
		self.mainLayout.listWidget_Relatorio.addItem("Tipo de Equilibrio = " + tipoEquilibrio)
		self.mainLayout.listWidget_Relatorio.addItem("Função Objetivo = " + funcaoObjetivo)
		self.mainLayout.listWidget_Relatorio.addItem("Desvio = " + desvio)
		self.mainLayout.listWidget_Relatorio.addItem("Ka = " + Ka)
		self.mainLayout.listWidget_Relatorio.addItem("Kb = " + Kb)
		self.mainLayout.listWidget_Relatorio.addItem("check Ka = " + str(Ka_check))
		self.mainLayout.listWidget_Relatorio.addItem("check Kb = " + str(Kb_check))
		self.mainLayout.listWidget_Relatorio.addItem('temperaturaCritica = ' + str(temperaturaCritica))
		self.mainLayout.listWidget_Relatorio.addItem('pressaoCritica = ' + str(pressaoCritica))
		self.mainLayout.listWidget_Relatorio.addItem('fatorAcentrico = ' + str(fatorAcentrico))
		self.mainLayout.listWidget_Relatorio.addItem('Vmolar_soluto = ' + str(Vmolar_soluto))
		self.mainLayout.listWidget_Relatorio.addItem('temperatura = ' + str(temperatura))
		self.mainLayout.listWidget_Relatorio.addItem('pressao = ' + str(pressao))
		self.mainLayout.listWidget_Relatorio.addItem('x2 = ' + str(x2))
		self.mainLayout.listWidget_Relatorio.addItem('y2 = ' + str(y2))
		self.mainLayout.listWidget_Relatorio.addItem('pressao_subli = ' + str(pressao_sublimacao))

		resposta = Ajuste_Parametros.AjusteParametros(desvio_float, Ka_float, Ka_check, Kb_float, Kb_check, fObj, TEQ, temperaturaCritica, pressaoCritica, 
		fatorAcentrico, Vmolar_soluto, counter, temperatura, pressao, x2, y2, pressao_sublimacao)

		print(resposta)


	def procura(self,data):
		length = len(data)
		dados = []
		for i in range(length):
			dados.append(data[i])  # armazena em um vetor
		for i in range(length):
			encontre = dados[i]
			if(encontre == '='):   # procura pelo caracter '='
				temp = dados[i+1:length-1]
				tamanho = len(temp)
				resultado = ''
				for i in range(tamanho):
				    resultado = resultado + temp[i]
		return (resultado)

	@pyqtSlot()
	def abrirArquivo(self):
		print('\n' + 'calcular: ajuste parametros' + '\n')

		self.mainLayout.listWidget_Relatorio.addItem('Ajuste de Parametros')
		fname = QFileDialog.getOpenFileName(self, 'Open file (*.txt)','/home/dell/Documents/')

		f = open(fname[0],'r')

		with f:
			numeroLinhas = sum(1 for _ in f)
			print ('numeros de linhas = ', str(numeroLinhas), '\n')
			f.close()

		f = open(fname[0],'r')

		with f:
			nomeMedida = f.readline()
			data = f.readline()
			resposta = self.procura(data)

			horario = f.readline() 
			resposta = self.procura(horario)

			desvio = f.readline()
			resposta = self.procura(desvio)
			self.mainLayout.lineEdit_Desvio.setText(resposta)

			ka = f.readline()
			resposta = self.procura(ka)
			self.mainLayout.lineEdit_Ka.setText(resposta) 

			ka_check = f.readline()
			resposta = self.procura(ka_check)
			if  (resposta == 'True' ): 
				self.mainLayout.checkBox_Ka.setChecked(True)
			elif(resposta == 'False'): 
				self.mainLayout.checkBox_Ka.setChecked(False)

			kb = f.readline()
			resposta = self.procura(kb)
			self.mainLayout.lineEdit_Kb.setText(resposta)

			kb_check = f.readline()
			resposta = self.procura(kb_check)
			if  (resposta == 'True' ): 
				self.mainLayout.checkBox_Kb.setChecked(True)
			elif(resposta == 'False'): 
				self.mainLayout.checkBox_Kb.setChecked(False)

			fObj = f.readline()
			resposta = self.procura(fObj)
			self.mainLayout.comboBox_FuncaoObjetivo.setCurrentIndex(int(resposta))

			TEQ = f.readline()
			resposta = self.procura(TEQ)
			self.mainLayout.comboBox_TipoEquilibrio.setCurrentIndex(int(resposta))

			### Preenchendo Tabela --> Propriedades Criticas ###
			f.readline() # temperatura_critica
			for i in range(2): self.mainLayout.tableWidget_PropriedadesCriticas.setItem(i, 0, QTableWidgetItem(f.readline()))
			f.readline() # pressao_critica
			for i in range(2): self.mainLayout.tableWidget_PropriedadesCriticas.setItem(i, 1, QTableWidgetItem(f.readline()))
			f.readline() # fator_acentrico
			for i in range(2): self.mainLayout.tableWidget_PropriedadesCriticas.setItem(i, 2, QTableWidgetItem(f.readline()))
			f.readline() # volume_molar_soluto
			for i in range(2): self.mainLayout.tableWidget_PropriedadesCriticas.setItem(i, 3, QTableWidgetItem(f.readline()))
			f.readline() # pontos_experimentais 
			for i in range(20): self.mainLayout.tableWidget_AjusteParametros.setItem(i, 0, QTableWidgetItem(f.readline()))
			f.readline() # temperatura 
			for i in range(20): self.mainLayout.tableWidget_AjusteParametros.setItem(i, 1, QTableWidgetItem(f.readline()))
			f.readline() # pressao 
			for i in range(20): self.mainLayout.tableWidget_AjusteParametros.setItem(i, 2, QTableWidgetItem(f.readline()))
			f.readline() # componente_X2
			for i in range(20): self.mainLayout.tableWidget_AjusteParametros.setItem(i, 3, QTableWidgetItem(f.readline()))
			f.readline() # componente_Y2
			for i in range(20): self.mainLayout.tableWidget_AjusteParametros.setItem(i, 4, QTableWidgetItem(f.readline()))
			f.readline() # pressao_sublimacao
			for i in range(20): self.mainLayout.tableWidget_AjusteParametros.setItem(i, 5, QTableWidgetItem(f.readline()))
			f.close()
       
	@pyqtSlot()
	def salvarArquivo(self):
		self.mainLayout.listWidget_Relatorio.addItem('Salvar Arquivo')
		name = QFileDialog.getSaveFileName(self, 'Save File','/home/dell/Documents/config_Ajuste_Parametros')
		print(name)
		file = open(name[0],'w')
		file.write('ajuste_parametros' +'\n')
		file.write('Data=' + '2017' +'\n')
		file.write('Horario=' + '02h57min' +'\n')
		# Desvio 
		file.write('desvio=' + self.mainLayout.lineEdit_Desvio.text() + '\n')
		# Ka
		file.write('Ka=' + self.mainLayout.lineEdit_Ka.text() + '\n')
		# Ka_check
		file.write('Ka_check=' + str(self.mainLayout.checkBox_Ka.isChecked()) + '\n')
		# Kb
		file.write('Kb=' + self.mainLayout.lineEdit_Kb.text() + '\n')
		# Kb_check
		file.write('Kb_check=' + str(self.mainLayout.checkBox_Kb.isChecked()) + '\n')
		# fObj
		file.write('fObj=' + str(self.mainLayout.comboBox_FuncaoObjetivo.currentIndex()) + '\n')
		# TEQ
		file.write('TEQ=' + str(self.mainLayout.comboBox_TipoEquilibrio.currentIndex()) + '\n')        
		# Temperatura Critica
		file.write('temperatura_critica' + '\n')
		temperatura_critica = []
		for i in range(2): 
			temperatura_critica.append(self.mainLayout.tableWidget_PropriedadesCriticas.item(i,0).text())
			print('temperatura_critica ', temperatura_critica) 
			file.write(temperatura_critica[i])
			file.write('\n')
		# Pressao Critica
		file.write('pressao_critica' + '\n')
		for i in range(2): 
			file.write(self.mainLayout.tableWidget_PropriedadesCriticas.item(i,1).text())
			file.write('\n')        
		# Fator Acentrico
		file.write('fator_acentrico' + '\n')
		for i in range(2): file.write(self.mainLayout.tableWidget_PropriedadesCriticas.item(i,2).text() + '\n')
		# Volume molar do soluto
		file.write('volume_molar_do_soluto' + '\n')
		for i in range(2): file.write(self.mainLayout.tableWidget_PropriedadesCriticas.item(i,3).text() + '\n')        
		# Pontos Experimentais
		file.write('pontos_experimentais' + '\n')
		for i in range(20): file.write(self.mainLayout.tableWidget_AjusteParametros.item(i,0).text() + '\n')
		# Temperatura
		file.write('temperatura' + '\n')
		for i in range(20): file.write(self.mainLayout.tableWidget_AjusteParametros.item(i,1).text() + '\n')
		# Pressao
		file.write('pressao' + '\n')
		for i in range(20): file.write(self.mainLayout.tableWidget_AjusteParametros.item(i,2).text() + '\n')
		# X2
		file.write('componente_X2' + '\n')
		for i in range(20): file.write(self.mainLayout.tableWidget_AjusteParametros.item(i,3).text() + '\n')
		# Y2
		file.write('componente_Y2' + '\n')
		for i in range(20): file.write(self.mainLayout.tableWidget_AjusteParametros.item(i,4).text() + '\n')
		# Pressao de Sublimacao
		file.write('pressao_de_sublimacao' + '\n')
		for i in range(20): file.write(self.mainLayout.tableWidget_AjusteParametros.item(i,5).text() + '\n')
		file.close()      

	@pyqtSlot()
	def informacoes(self):
		print("Informacoes")














