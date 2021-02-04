import os

areas = [
	'Psicologia',
	'Medicina',
	'Física',
	'Matemática'
	'Bioquímica',
	'Química',
	'Ciência da Computação',
	'Microbiologia',
	'Filosofia',
	'Astronomia'
]

for area in areas:
	os.system('python3 lattes_scrap.py ' + area)