from odoo import models,api,fields, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, UserError, ValidationError


class approval_sale(models.Model):
    _name = 'approval.lines'
    credit_range = fields.One2many('credit.limit', 'credit_range_id')
    
    @api.model
    def create(self, vals):
        self.env.cr.execute("""
        select count(*) from approval_lines;
        """)
        records = self.env.cr.fetchall()
        if records[0][0] > 0:
            raise Warning(_('Please edit the settings, creation not allowed.'))
        return super(approval_sale, self).create(vals)
              

class credit(models.Model):
    _name = 'credit.limit'
    credit_range_id = fields.Many2one('approval.lines', ondelete='cascade')
    amount_percent = fields.Float(string="% Over Credit Limit")
    group = fields.Many2one('res.groups', string="Allowed group")

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'

    amount_payable_percentage = fields.Float(compute='get_credit_amount')
    credit_limit_status = fields.Boolean(default=False)

    # Return current user record
    def get_current_uid(self):
        return self.env['res.users'].search([('id','=', self.env.uid)])
    
    def get_total_amount_payable(self):
        return self.partner_id.credit + self.amount_total + self.get_confirm_so_amount()
    
    # To return approval group record
    def get_approval(self, table):
        return self.env[table].search([('group', 'in', self.get_current_uid().groups_id.ids)])

    def get_credit_amount(self):
        
        # if the user has no credit limit set (to avoid division by zero)
        if self.partner_id.credit_limit > 0:
            self.amount_payable_percentage = (self.get_total_amount_payable() - self.partner_id.credit_limit)
        else:
            self.amount_payable_percentage = self.get_total_amount_payable()
    
    def get_confirm_so_amount(self):
        self.env.cr.execute("""
        select(
        (select sum(amount_total) as total from sale_order where state in ('sale','done') and partner_id= %s )-
        (select sum(amount_total) as total from account_invoice where state in ('open','paid') and partner_id= %s)
        ) as total
        """,(self.partner_id.id, self.partner_id.id))
        amount = self.env.cr.fetchall()
        if not amount[0][0]:
            return 0
        return amount[0][0]

    def check_credit_limit(self):     
        # Check if the user is within his credit limit 
        if self.amount_payable_percentage < 0:
            self.state = 'sale'
            return False
        approval_rec = self.get_approval('credit.limit')
        
        # If current user isn't in any approval group, don't allow
        if not approval_rec:
            raise Warning(_('You do not exist in any of the Approval Group'))
        if self.amount_payable_percentage <= max(approval_rec.mapped('amount_percent')):
            self.state = 'sale'
            return False           
        else:
            return True
           
    def call_credit_day_func(self):
        credit_bool = False
        if self.credit_limit_status:
            self.state = 'sale'
            return
        if not self.credit_limit_status:
            credit_bool = self.check_credit_limit()
        self.check_and_warn(credit_bool)

    def check_and_warn(self, credit_bool):
        if credit_bool:
            raise Warning(_('Credit Limit has been over, Approval Required'))

    @api.multi
    def action_confirm(self):
        self.call_credit_day_func()
        res = super(sale_order_inherit,self).action_confirm()
        return res

    @api.onchange('credit_limit_status')
    def approval_check(self):
        if self.partner_id:

            #check for credit limit check
            app_credit_rec = self.get_approval('credit.limit')
            if self.amount_payable_percentage > max(app_credit_rec.mapped('amount_percent')):
                self.credit_limit_status = False
            elif self.amount_payable_percentage <= max(app_credit_rec.mapped('amount_percent')):
                self.credit_limit_status = True
