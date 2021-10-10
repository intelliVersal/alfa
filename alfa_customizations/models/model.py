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


class InheritProduction(models.Model):
    _inherit = 'mrp.production'

    produced_quantity = fields.Float(compute='calculate_quantities', store=True)
    remain_quantity = fields.Float(compute='calculate_quantities', store=True)
    machine_number = fields.Char('Machine number')

    def calculate_quantities(self):
        for qty in self:
            produce_qty = 0.0
            for line in qty.finished_move_line_ids:
                produce_qty += line.qty_done
            qty.update({
                'produced_quantity': produce_qty,
                'remain_quantity': qty.product_qty - produce_qty,
            })

class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    request_user_id = fields.Many2one('res.user')


