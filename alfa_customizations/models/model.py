from odoo import models, fields, api,_
from datetime import date, datetime
from odoo.exceptions import ValidationError


class InheritWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_raw_location = fields.Boolean(default=False)
