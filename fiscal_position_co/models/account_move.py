# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(AccountMoveLine,self)._onchange_product_id()
        if self.move_id.fiscal_position_id:
            self.move_id.action_comparation()
        self.move_id._onchange_invoice_line_ids()
        

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('fiscal_position_id')
    def _onchange_fiscal_position_id(self):
        if self.fiscal_position_id:
            self.action_comparation()
        for line in self.invoice_line_ids:
            line._onchange_mark_recompute_taxes()
        self._onchange_invoice_line_ids()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        if self.fiscal_position_id:
            self.action_comparation()
            # self._compute_amount()
        super(AccountMove, self)._onchange_invoice_line_ids()



    def action_comparation(self):
        concept_types = {}
        types = self.env['product.concept.type'].search([])
        for cons_type in types:
            concept_types[cons_type.name]=0
        concept_types['False']=0
        for record in self:
            if record.invoice_filter_type_domain not in ('sale','purchase'):
                continue
            for line in record.invoice_line_ids:
                concept = str(line.product_id.concept_type_id.name)
                concept_types[concept] += line.price_subtotal
                lists = record._compute_comparation(line)
                final_ids, remove_ids = [], []
                # if record.invoice_filter_type_domain == 'sale':
                #     product_taxes_ids = line.product_id.taxes_id.ids
                # elif record.invoice_filter_type_domain == 'purchase':
                #     product_taxes_ids = line.product_id.supplier_taxes_id.ids
                product_taxes_ids = line.tax_ids.ids
                for comparation in lists:
                    dic = {
                        'amount': line.price_subtotal,
                        'operator': comparation['comparation'],
                        'value': comparation['value']
                    }
                     
                    if record.fiscal_position_id._compute_operator(dic) and line.product_id.concept_type_id == comparation['type']:
                        if not comparation['dest']:
                            if comparation['src'] not in remove_ids: remove_ids.append(comparation['src'])
                        else:
                            if comparation['dest'] not in final_ids: final_ids.append(comparation['dest'])
                    else:
                        if comparation['src'] in line.product_id.taxes_id.ids and comparation['dest'] in product_taxes_ids:
                            if comparation['dest'] not in remove_ids: remove_ids.append(comparation['dest'])

                for remove_id in remove_ids:
                    if remove_id in product_taxes_ids: product_taxes_ids.remove(remove_id)
                for tax_id in product_taxes_ids:
                    if tax_id not in final_ids: final_ids.append(tax_id)
                if final_ids:
                    result = self.env['account.tax'].browse(final_ids)
                    line.tax_ids = result

            # se vuelve a hacer la validacion por todas las lineas pero teniendo en cuenta el total de cada tipo de producto
            concept_types['False'] = 0
            for line in record.invoice_line_ids:
                total_taxes, remove_ids = [], []
                # if record.invoice_filter_type_domain == 'sale':
                #     product_taxes_ids = line.product_id.taxes_id.ids
                # elif record.invoice_filter_type_domain == 'purchase':
                #     product_taxes_ids = line.product_id.supplier_taxes_id.ids
                product_taxes_ids = line.tax_ids.ids
                for comparation in lists:
                    dic = {
                        'amount': concept_types.get(str(line.product_id.concept_type_id.name)),
                        'operator': comparation['comparation'],
                        'value': comparation['value']
                    }
                    if record.fiscal_position_id._compute_operator(dic) and line.product_id.concept_type_id == comparation['type']:
                        if not comparation['dest']:
                            if comparation['src'] not in remove_ids: remove_ids.append(comparation['src'])
                        else:
                            if comparation['dest'] not in total_taxes: total_taxes.append(comparation['dest'])
                    else:
                        if comparation['src'] in line.product_id.taxes_id.ids and comparation['dest'] in product_taxes_ids:
                            if comparation['dest'] not in remove_ids: remove_ids.append(comparation['dest'])

              


    def _compute_comparation(self, line):
        lists = []
        if self.fiscal_position_id:
            products = line.product_id
            ids = products.taxes_id.ids if self.invoice_filter_type_domain == 'sale' else products.supplier_taxes_id.ids
            lists = self.fiscal_position_id._compute_comparation(tuple(ids), self.invoice_filter_type_domain)
        return lists

