# -*- coding: utf-8 -*-
from odoo import http

# class AccountBalances(http.Controller):
#     @http.route('/account_balances/account_balances/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_balances/account_balances/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_balances.listing', {
#             'root': '/account_balances/account_balances',
#             'objects': http.request.env['account_balances.account_balances'].search([]),
#         })

#     @http.route('/account_balances/account_balances/objects/<model("account_balances.account_balances"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_balances.object', {
#             'object': obj
#         })