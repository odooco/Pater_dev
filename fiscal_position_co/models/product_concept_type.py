# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class ProductConceptType(models.Model):
    _name = 'product.concept.type'

    name = fields.Char(string='Concept Type')
