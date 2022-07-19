{
	'name': 'Payments Module Extension', 
	'description': 'Payments Module Extension',
	'author': 'Muhammad Jaffar Raza', 
	'depends': ['account','mail'], 
	'application': True,
	'data': [
	'security/access_security.xml',
	'security/ir.model.access.csv',
	'views/template.xml',
	'views/email_template.xml'
	],
}
