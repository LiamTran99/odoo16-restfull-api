{
    "name": "Odoo rest API",
    "description": """The Rest API for Odoo 16""",
    "summary": """This app helps to interact with odoo
     backend with help of rest api requests""",
    "category": "Tools",
    "version": "16.0.1",
    "depends": ['base', 'web'],
    "data": [
        'security/ir.model.access.csv',
        'views/connection_api_views.xml'
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': True,
}
