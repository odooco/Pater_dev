#Luis Felipe Paternina
#
#Ingeniero de Sistemas
#
# lfpaternina93@gmail.com
#
# Cel: +573215062353
#
# Bogotá,Colombia
#
#################################################################################################################


# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    concept_type_id = fields.Many2one('product.concept.type', string='Concept Type')