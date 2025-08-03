{
	'name': "Analytic Account on Stock Move and Stock Valuation Layer",
	'summary': "Allows to select an Analytic Account on Stock Move and Stock Valuation Layer",
	'author': 'Develogers',
	'maintainer': 'Dany Chavez',
	'website': 'https://develogers.com',
	'support': 'especialistas@develogers.com',
	'live_test_url': 'https://demo.develogers.com',
	'license': 'LGPL-3',
	'category': 'Extra Tools',
	'version': '17.0.1.0.2',
	'price': '49.99',
	'currency': 'EUR',
	'depends': [
		'base',
  		'account',
		'stock_account',
		'purchase_stock',
		'stock_analytic'
	],
	'data': [
		'views/stock_valuation_layer_views.xml',
	],
	'images': ['static/description/banner.gif'],
	'installable': True,
	'application': False,
	'auto_install': False,
	'secuence': '1'
}
