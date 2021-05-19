# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json

class accout_payment(models.Model):
    _inherit = 'account.payment'

    account_balance = fields.Char(string='Acc Balance', default='0', compute='_compute_journal_balance', store=True)
    partner_balance = fields.Monetary(string='Partner Balance', default='0',compute='_compute_partner_balance', store=True)

    @api.one
    @api.depends('partner_id')
    def _compute_partner_balance(self):
        if self.partner_id:
            if self.partner_type == 'customer':
                self.partner_balance = self.partner_id.credit_new
            if self.partner_type == 'supplier':
                self.partner_balance = self.partner_id.debit_new

    @api.one
    @api.depends('journal_id')
    def _compute_journal_balance(self):
        if self.journal_id:
            account_balance = json.loads(self.journal_id.kanban_dashboard)
            self.account_balance = account_balance['account_balance']

class RegisterPaymentsInherit(models.TransientModel):
    _inherit = 'account.register.payments'

    account_balance = fields.Char(string='Acc Balance', default='0', compute='_compute_journal_balance', store=True)

    @api.one
    @api.depends('journal_id')
    def _compute_journal_balance(self):
        if self.journal_id:
            account_balance = json.loads(self.journal_id.kanban_dashboard)
            self.account_balance = account_balance['account_balance']
