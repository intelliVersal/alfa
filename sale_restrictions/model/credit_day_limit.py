from odoo import models,api,fields, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, UserError, ValidationError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

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
            due_amount = amount[0][0]
            if due_amount > self.partner_id.credit_limit:
                raise ValidationError(_('Sale Order confirmation is not possible, because outstanding balance of this customer is %s, and credit limit of this customer is %s or sale orders of this customer are confirmed but not invoiced yet.') % (amount[0][0], self.partner_id.credit_limit))

    def get_payment_current_so(self):
        if not self.env.user.has_group('sale_restrictions.allow_credit_sale'):
            if self.partner_id.allow_credit_sale == False:
                payment_obj = self.env['account.payment'].sudo().search([('partner_id','=',self.partner_id.id),('state','=','posted'),('so_reference_ids','=',self.id)])
                if not payment_obj:
                    raise ValidationError(_('Kindly, Enter the payment against this sale order, credit sale is not allowed to this customer'))
                else:
                    payment_amount = 0.0
                    for rec in payment_obj:
                        payment_amount += rec.amount
                    if payment_amount < ((self.amount_total * 50)/100):
                        raise ValidationError(_('Payment amount should must be 50% of the total amount, kindly check the payment against this sale order'))
            else:
                self.get_confirm_so_amount()

    def check_discount_rate(self):
        for rec in self.order_line:
            if not self.env.user.has_group('sale_restrictions.allow_maximum_discount'):
                if rec.discount >= 5.0:
                    raise ValidationError(_('You are not allowed to give %s or more than %s discount')%(rec.discount,rec.discount))

    @api.multi
    def action_confirm(self):
        self.check_discount_rate()
        self.get_payment_current_so()
        res = super(SaleOrderInherit, self).action_confirm()
        return res


class PickingInherit(models.Model):
    _inherit = 'stock.picking'

    def check_so_payment(self):
        if self.picking_type_id.code == 'outgoing':
            if self.sale_id:
                if self.partner_id.allow_credit_sale == False:
                    pay_obj = self.env['account.payment'].sudo().search([('partner_id', '=', self.partner_id.id), ('state', '=', 'posted'),('so_reference_ids', '=', self.sale_id.id)])
                    amount_payment = 0.0
                    for records in pay_obj:
                        amount_payment += records.amount
                    if amount_payment < self.sale_id.amount_total:
                        raise ValidationError(_('You are not allowed to validate this delivery, as the payment is not fully received'))

    @api.multi
    def button_validate(self):
        self.check_so_payment()
        res = super(PickingInherit, self).button_validate()
        return res

