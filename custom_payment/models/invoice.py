from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, QWebException
import datetime

class InheritInvoice(models.Model):
    _inherit = 'account.invoice'
    recording_rule = fields.Selection([('standard','Standard'),('jv_each_line','JV for each line with vendor')],default='standard')
    account_analytics = fields.Many2one('account.analytic.account')
    old_number = fields.Char()

    @api.model
    def create(self, vals):
        vals['old_number'] = None
        return super(InheritInvoice, self).create(vals)

    @api.multi
    def action_invoice_cancel(self):
        self.old_number = self.number
        res = super(InheritInvoice, self).action_invoice_cancel()
        return res

    @api.multi
    def action_invoice_open(self):
        if self.recording_rule != 'standard':
            self.create_jv_each_line()
        res = super(InheritInvoice, self).action_invoice_open()
        return res

    @api.multi
    def create_jv_each_line(self):

        line = []
        if self.recording_rule != 'standard':
            if self.tax_line_ids:
                tax_amount = 0
                for items in self.tax_line_ids:
                    tax_amount += items.amount_total

                    analytic_tag = 0
                    for recs in items.analytic_tag_ids:
                        analytic_tag = [(4, recs.id,)]

                    line.append(
                        (0, 0, {'account_id': items.account_id.id, 'name': items.name,
                                'partner_id': items.invoice_id.partner_id.id,
                                'debit': items.amount_total, 'credit': 0,
                                'employee_id': items.employee.id,
                                'analytic_account_id':items.account_analytic_id.id,
                                'analytic_tag_ids': analytic_tag if analytic_tag else False,
                                'date_maturity': items.invoice_id.date_invoice,
                                'tax_line_id': items.tax_id.id,
                                'date': items.invoice_id.date_invoice}))

                    line.append(
                        (0, 0, {'account_id': self.account_id.id, 'name': items.name,
                                'partner_id': items.invoice_id.partner_id.id,
                                'debit': 0, 'credit': items.amount_total,
                                'employee_id': items.employee.id,
                                'analytic_account_id': items.account_analytic_id.id,
                                'analytic_tag_ids': analytic_tag if analytic_tag else False,
                                'date_maturity': items.invoice_id.date_invoice,
                                'date': items.invoice_id.date_invoice}))

            sequence_code = self.journal_id.sequence_id.code
            for lines in self.invoice_line_ids:
                tax = 0
                for rec in lines.invoice_line_tax_ids:
                    tax = [(4, rec.id,)]
                tag = 0
                for rec in lines.analytic_tag_ids:
                    tag = [(4, rec.id,)]

                line.append(
                    (0, 0, {'account_id': self.account_id.id, 'name': lines.name,
                            'partner_id': lines.invoice_id.partner_id.id,
                            'analytic_account_id': lines.account_analytic_id.id,
                            'employee_id':lines.empl_name.id,
                            'analytic_tag_ids': tag if tag else False,
                            'debit': 0, 'credit': lines.price_subtotal,
                            'date_maturity': lines.invoice_id.date_invoice,
                            'date': lines.invoice_id.date_invoice}))

                line.append(
                    (0, 0, {'account_id': lines.account_id.id, 'name': lines.name,
                            'partner_id': lines.invoice_id.partner_id.id,
                            'analytic_account_id': lines.account_analytic_id.id,
                            'employee_id': lines.empl_name.id,
                            'tax_ids': tax if tax else False,
                            'analytic_tag_ids': tag if tag else False,
                            'debit': lines.price_subtotal, 'credit': 0,
                            'date_maturity': lines.invoice_id.date_invoice,
                            'date': lines.invoice_id.date_invoice}))
            account_move = self.env['account.move'].create({'name':self.old_number if self.old_number else self.env['ir.sequence'].next_by_code(sequence_code),
                                                            'ref': self.reference,
                                                            'journal_id': self.journal_id.id,
                                                            'date': self.date_invoice,
                                                            'line_ids': line})
            account_move.post()
            self.move_id = account_move
            self.old_number = self.number
            self.state = 'open'

class InvoiceTaxInherit(models.Model):
    _inherit = 'account.invoice.tax'
    employee = fields.Many2one('hr.employee')

    
class AccountInvoice(models.Model):
    _inherit = "account.invoice.line"
    
    @api.onchange('product_id')
    def set_account_analytics(self):
        for rec in self:
            if rec.product_id:
                self.account_analytic_id = self.invoice_id.account_analytics.id






