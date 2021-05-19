from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta
import datetime


class PaymentExpense(models.Model):
    _name = 'expense.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Payment Expense"
    _order = 'request_date desc, id desc'

    is_bill = fields.Boolean(default=False)

    def button_create_vendor_bill(self):
        if not self.partner_id:
            raise UserError(_('Select the partner before create the bill.'))
        inv = self.env['account.invoice'].create({'partner_id': self.partner_id.id,
                                                  'date_invoice': fields.date.today(),
                                                  'state':'draft',
                                                  'type':'in_invoice',
                                                  'ven_bill_id': self.id,
                                                  'name':self.reference if self.reference else '',
                                                 })
        for lines in self.invoice_lines:
            tax = [(4, lines.taxes_id.id,)]
            tags = [(4, lines.analytical_tags.id,)]
            inv.invoice_line_ids.create({'invoice_id': inv.id,
                                         'product_id': self.env['product.product'].search([('id','=',4)]).id,
                                         'account_id': self.env['product.product'].search([('id','=',4)]).property_account_expense_id.id,
                                         'account_analytic_id': lines.analytic_account.id,
                                         'invoice_line_tax_ids': tax if lines.taxes_id else False,
                                         'analytic_tag_ids': tags if lines.analytical_tags else False,
                                         'name': lines.name,
                                         'expense_nature':'normal',
                                         'quantity': lines.quantity,
                                         'price_unit': lines.unit_price,
                                         'empl_name':self.employee_id.id if self.employee_id else None,
                                         })
        self.is_bill = True

    def action_bill_payment_view(self):
        return {
            'name': _('Vendor Bill'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('ven_bill_id', '=', self.ids)],
        }

    @api.depends('invoice_lines.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.invoice_lines:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    name = fields.Char()
    request_type = fields.Selection([('custody','Custody'),('material','Material'),('adjustment','Adjustment')], required=True, default='custody')
    partner_id = fields.Many2one('res.partner')
    employee_id = fields.Many2one('hr.employee')
    request_date = fields.Date()
    reference = fields.Char()
    notes = fields.Text('Terms and Conditions')
    branch = fields.Many2one('hr.branch', string='Branch')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    state = fields.Selection([('draft','Draft'),('submit','Submit'),('management_approval','Management Approval'),('finance_approval','Finance Approval'),('approved','Approved'),('cancel','Cancel')],default='draft', index=True, copy=False, readonly=True, required=True, track_visibility='onchange')
    invoice_lines = fields.One2many('invoice.lines', 'invoice_line_ids')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    has_payment = fields.Boolean(default=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    is_task = fields.Boolean(default=False)
    task_id = fields.Many2one('project.task')

    @api.multi
    def unlink(self):
        for order in self:
            if not order.state == 'cancel':
                raise UserError(_('In order to delete, you must cancel it first.'))
        return super(PaymentExpense, self).unlink()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('payment.expense')
        result = super(PaymentExpense, self).create(vals)
        return result

    @api.multi
    def button_submit(self):
        if self.partner_id:
            mail_content = "Expense Request ( "+self.name+") has been created by " + str(self.env.user.name) + " of amount " + str(self.amount_total) + " for the " + self.partner_id.name + "<br> Kindly review it and proceed for further approvals"
        else:
            mail_content = "Expense Request ( "+self.name+") has been created by " + str(self.env.user.name) + " of amount " + str(self.amount_total) + " for the " + self.employee_id.name + "<br> Kindly review it and proceed for further approvals"
        main_content = {
            'subject': _('Expense Request Approval'),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': 'barrak@musaidalsayyarco.com',
        }
        self.env['mail.mail'].create(main_content).send()
        self.create_expense_task()
        return self.write({'state': 'management_approval'})

    def create_expense_task(self):
        if self.partner_id:
            task =self.env['project.task'].create({'name': 'Expense Payment- '+ self.partner_id.name +' of amount '+str(self.amount_total),
                                                    'project_id': self.env['project.project'].search([('name','like','Payment Tasks')],limit=1).id,
                                                    'stage_id': self.env['project.task.type'].search([('task_sequence', '=',10)]).id,
                                                    'user_id': self.env['res.users'].search([('id','=',2)]).id,
                                                    'date_deadline': fields.Date.today() + timedelta(days=2),
                                                    'payment_id':self.id,
                                                    'description': self.reference,
                                                    })
        else:
            task = self.env['project.task'].create({'name': 'Expense Payment- '+ self.employee_id.name +' of amount '+str(self.amount_total),
                                                    'project_id': self.env['project.project'].search([('name','like','Payment Tasks')],limit=1).id,
                                                    'stage_id': self.env['project.task.type'].search([('task_sequence', '=',10)]).id,
                                                    'user_id': self.env['res.users'].search([('id','=',2)]).id,
                                                    'date_deadline': fields.Date.today() + timedelta(days=2),
                                                    'payment_id': self.id,
                                                    'description': self.reference,
                                                     })
        self.task_id = task
        self.is_task = True

    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def button_management_approve(self):
        self.task_id.stage_id = self.env['project.task.type'].search([('task_sequence','=',12)]).id
        self.task_id.user_id = self.env['res.users'].search([('id', '=', 13)]).id
        return self.write({'state': 'finance_approval'})

    @api.multi
    def button_cancel(self):
        return self.write({'state': 'cancel'})

    def action_task_view_pay(self):
        return {
            'name': _('Tasks'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', '=', self.ids)],
        }


class InvoiceLines(models.Model):
    _name = 'invoice.lines'
    invoice_line_ids = fields.Many2one('expense.payment',index=True, required=True, ondelete='cascade')
    name = fields.Char('Description')
    invoice_no = fields.Char('Invoice No.')
    analytic_account = fields.Many2one('account.analytic.account')
    company_id = fields.Many2one('res.company', related='invoice_line_ids.company_id', string='Company', store=True, readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
    analytical_tags = fields.Many2many('account.analytic.tag')
    currency_id = fields.Many2one(related='invoice_line_ids.currency_id', store=True, string='Currency', readonly=True)
    quantity = fields.Float('Quantity', default=1.0)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    unit_price = fields.Float('Unit Price')
    remarks = fields.Char('Remarks')

    @api.depends('quantity','unit_price','taxes_id')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.quantity * line.unit_price
            if line.taxes_id:
                for rec in line.taxes_id:
                    line.price_tax = ((line.quantity * line.unit_price * rec.amount)/100)

class InheritInvoiceLines(models.Model):
    _inherit = 'account.invoice'
    ven_bill_id = fields.Integer()