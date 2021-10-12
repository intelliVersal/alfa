from odoo import models,api,fields, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, UserError, ValidationError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def check_discount_rate(self):
        for rec in self.order_line:
            if not self.env.user.has_group('sale_restrictions.allow_maximum_discount'):
                if rec.discount >= 5.0:
                    raise ValidationError(_('You are not allowed to give %s or more than %s discount')%(rec.discount,rec.discount))

    def get_confirm_so_amount(self):
        if not self.env.user.has_group('sale_restrictions.allow_credit_sale'):
            self.env.cr.execute("""
            select(
            (select sum(amount_total) as total from sale_order where state in ('sale','done') and partner_id= %s )-
            (select sum(amount_total) as total from account_invoice where state in ('open','paid') and partner_id= %s)
            ) as total
            """,(self.partner_id.id, self.partner_id.id))
            amount = self.env.cr.fetchall()
            if not amount[0][0]:
                return 0
            due_amount = amount[0][0] - self.amount_total
            if due_amount > self.partner_id.credit_limit:
                raise ValidationError(_('Sale Order confirmation is not possible, because outstanding balance of this customer is %s, and credit limit of this customer is %s') % (amount[0][0], self.partner_id.credit_limit))

    @api.multi
    def action_confirm(self):
        self.check_discount_rate()
        self.get_confirm_so_amount()
        res = super(SaleOrderInherit,self).action_confirm()
        return res
