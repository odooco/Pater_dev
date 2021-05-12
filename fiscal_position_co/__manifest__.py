# -*- coding: utf-8 -*-
#########################################################################################################################
#
# Odoo Dev: Luis Felipe Paternina - lfpaternina93@gmail.com
#
# Odoo Funcional: Julian Bocanegra
#
# Bogotá, Colombia
#
########################################################################################################################

{
    'name': "Fiscal Positions Colombia",

    'summary': "Fiscal Positions CO",

    'description': "Fiscal Positions Base",

    'author': "Luis Felipe Paternina",
    
    

    'category': 'Accounting/Accounting',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['account','sale','product','purchase'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/account_fiscal_position_view.xml',
        'views/product_concept_type.xml',
        'views/product_view.xml',
        'views/account_move_view.xml',
    ],
}
