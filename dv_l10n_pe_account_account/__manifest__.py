{
    'name': """
        Serie y numero de factura
    """,

    'summary': """
        Permite registrar facturas de proveedores con campos personalizados para la contabilidad peruana.
    """,

    'description': """
        Agrega campos en facturas de proveedores.
    """,

    'author': 'Juan',
    'category': 'Localization',
    'version': '17.0',
    
    'price': 79.99,
    'currency': 'EUR',

    'depends': [
        'l10n_latam_invoice_document',
        'l10n_pe'
    ],

    'data': [
        'views/account_move.xml'
    ],
    
    'auto_install': False,
	'application': True,
	'installable': True,
}
