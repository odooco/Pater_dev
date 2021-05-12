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

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def _compute_comparation(self, ids, tax_type):
        lists = []
        for line in self.tax_ids.filtered(lambda x: x.tax_src_id.type_tax_use == tax_type):
            if line.tax_comparation and line.tax_comparation_value>=0 and line.tax_src_id.id in ids:
                dic = {
                    'src': line.tax_src_id.id,
                    'comparation': line.tax_comparation,
                    'value': line.tax_comparation_value,
                    'dest': line.tax_dest_id.id,
                    'type': line.product_type
                }
                lists.append(dic)
        return lists
    
    def _compute_operator(self, dic):
        amount = dic['amount']
        operator = dic['operator']
        value = dic['value']
        if operator == '==': 
            if amount == value: 
                return True 
            else: 
                return False
        elif operator == '!=':
            if amount != value:
                return True
            else: 
                return False
        elif operator == '>':
            if amount > value:
                return True
            else: 
                return False
        elif operator == '<':
            if amount < value:
                return True
            else: 
                return False    
        elif operator == '>=':
            if amount >= value:
                return True
            else: 
                return False
        elif operator == '<=':
            if amount <= value:
                return True
            else: 
                return False
        else:
            return False


class AccountFiscalPositionTax(models.Model):
    _inherit = 'account.fiscal.position.tax'

    tax_comparation = fields.Selection([('==', '=='), ('!=', '!='), ('>', '>'), ('<','<'), ('>=','>='), ('<=','<=')], 'Comparation', default='==')
    tax_comparation_value = fields.Float('Value', digits='Account')
    product_type = fields.Many2one('product.concept.type', string='Concept Type')

    @api.onchange("tax_dest_id")
    def _onchange_tax_dest_id(self):
        for record in self:
            if record.tax_src_id and record.tax_dest_id:
                if record.tax_dest_id.type_tax_use != record.tax_src_id.type_tax_use:
                    raise UserError(_('The tax to be applied and the tax on the product must be of the same type.'))

    @api.onchange("tax_src_id")
    def _onchange_tax_src_id(self):
        for record in self:
            if record.tax_dest_id and record.tax_src_id:
                if record.tax_dest_id.type_tax_use != record.tax_src_id.type_tax_use:
                    raise UserError(_('The tax to be applied and the tax on the product must be of the same type.'))
 