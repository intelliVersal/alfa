from odoo import models, fields, api,_
from datetime import date, datetime
from odoo.exceptions import ValidationError


class InheritWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_raw_location = fields.Boolean(default=False)


class SaleInherit(models.Model):
    _inherit = 'sale.order'

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, domain="[('is_raw_location','=',False)]", states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

