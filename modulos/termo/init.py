from modules.data_compiler import DataCompiler
from modules.pdf_constructor import PdfConstructor

def stageComponents():

	# modelo_de_dados = {
	# 	"unidade":"E.M.Professor de testes", 
	# 	"nome": "Thyéz de Oliveira", 
	# 	"serial":"SIOUH29872", 
	# 	"matricula":"2987-2",
	# 	"cpf":"78978944221",
	# 	"celular":"22998883377"
	# }
	
	mock_data = {
		"unidade":"E.Municipalizada Elcira de Oliveira Coutinho", 
		"nome": "Gianne Frade Pezzino", 
		"serial":"0A1G9QARB01168W", 
		"matricula":"10286-1",
		"cpf":"15787602757",
		"celular":"(21)99181-7889"
	}
	
	data_comp = DataCompiler()
	data_comp.set_data(mock_data)
	data_from_compiler = data_comp.define_first_paragraph()

	res = PdfConstructor(data_from_compiler, "Termo de responsabilidade", data_comp.get_data())

def initialize():
	print("Starting...")
	stageComponents()
	print("... Gerado. FIM.")
	
initialize()

