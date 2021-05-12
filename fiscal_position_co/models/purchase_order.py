# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine,self).onchange_product_id()
        if self.order_id.fiscal_position_id:
            self.order_id.action_comparation()
    
    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     super(PurchaseOrderLine, self)._compute_amount()
    #     if self.order_id.fiscal_position_id:
    #         self.order_id.action_comparation()
    

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('fiscal_position_id')
    def _onchange_fiscal_position_id(self):
        if self.fiscal_position_id:
            self.action_comparation()


    @api.onchange('order_line')
    def _onchange_order_line(self):
        if self.fiscal_position_id:
            self.action_comparation()
        

    def action_comparation(self):

        concept_types = {}
        types = self.env['product.concept.type'].search([])
        for cons_type in types:
            concept_types[cons_type.name]=0
        concept_types['False']=0
        for record in self:
            for line in record.order_line:
                concept = str(line.product_id.concept_type_id.name)
                concept_types[concept] += line.price_subtotal
                lists = record._compute_comparation(line)
                final_ids, remove_ids = [], []
                product_taxes_ids = line.taxes_id.ids
                
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
                    line.taxes_id = result

            # se vuelve a hacer la validacion por todas las lineas pero teniendo en cuenta el total de cada tipo de producto
            concept_types['False']=0
            for line in record.order_line:
                total_taxes, remove_ids = [], []
                product_taxes_ids = line.taxes_id.ids
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

                for remove_id in remove_ids:
                    if remove_id in product_taxes_ids: product_taxes_ids.remove(remove_id)
                for tax in product_taxes_ids:
                    if tax not in total_taxes: total_taxes.append(tax)
                if total_taxes:
                    result = self.env['account.tax'].browse(total_taxes)
                    line.taxes_id = result


    def _compute_comparation(self, line):
        lists = []
        if self.fiscal_position_id:
            product_taxes_ids = line.product_id.supplier_taxes_id.ids
            lists = self.fiscal_position_id._compute_comparation(tuple(product_taxes_ids), 'purchase')
        return lists

    
