from odoo import models, fields, api,_
from datetime import date
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import datetime
from datetime import timedelta


class InheritPaymentCustom(models.Model):
    _inherit = 'account.payment'
    state = fields.Selection([('draft', 'Draft'),('submit','Submitted'),('to_approve','To Approve'),('approved','Approved'),('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")
    is_task = fields.Boolean(default=False)
    task_id = fields.Many2one('project.task')
    sadad_num = fields.Char('Sadad / Cheque No.')
    payment_status = fields.Selection([('in_bank','In Bank'),('in_cheque','In Cheque')], default='')\

    @api.multi
    def action_set_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def proceed_to_submit(self):
        if self.env.user.has_group('task_creator_on_approval.group_direct_payment') or self.partner_id.id == 2727:
            self.write({'state': 'approved'})
            return False
        if self.payment_type == 'transfer':
            mail_content = "Payment has been created by " + str(self.env.user.name) + "of amount " + str(
                self.amount) + "(Internal transfer)" + "<br> Kindly review it and proceed for further approvals"
        else:
            mail_content = "Payment has been created by " + str(self.env.user.name) + "of amount " + str(self.amount) + " for the " + self.partner_id.name + "<br> Kindly review it and proceed for further approvals"
        main_content = {
            'subject': _('Payment'),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': 'm.gad@musaidalsayyarco.com',
        }
        self.env['mail.mail'].create(main_content).send()
        self.action_create_payment_task()
        return self.write({'state': 'submit'})

    def action_create_payment_task(self):
        task = self.env['project.task'].create({'name': 'Payment- '+ str(self.partner_id.name) +' of amount '+str(self.amount),
                                                'project_id': self.env['project.project'].search([('name','like','Payment Task')]).id,
                                                'stage_id': self.env['project.task.type'].search([('task_sequence','=',10)]).id,
                                                'user_id': self.env['res.users'].search([('id','=',13)]).id,
                                                'date_deadline': fields.Date.today() + timedelta(days=2),
                                                'amount_payment': self.amount,
                                                'description': self.communication,
                                                'partner_id': self.partner_id.id,
                                                'sadad_no': self.sadad_num,
                                                'payment_id': self.id,
                                                'is_payment': True})
        self.is_task = True
        self.task_id = task

    @api.multi
    def proceed_to_approve(self):
        self.task_id.stage_id = self.env['project.task.type'].search([('task_sequence','=',11)]).id
        self.task_id.user_id = self.env['res.users'].search([('id', '=', 2)]).id
        return self.write({'state': 'to_approve'})

    @api.multi
    def action_approve_pay(self):
        if self.env.uid != 2:
            raise UserError("Sorry, you are not allowed to approve the payment.")
        else:
            self.task_id.stage_id = self.env['project.task.type'].search([('task_sequence','=',12)]).id
            self.task_id.user_id = self.env['res.users'].search([('id', '=', 13)]).id
            return self.write({'state': 'approved'})

    @api.multi
    def action_task_view(self):
        return {
            'name': _('Tasks'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', '=', self.ids)],
        }


class InheritHREmployeeCustom(models.Model):
    _inherit = 'hr.employee'

    def create_hr_projects_task(self):
        date_now = datetime.date.today() + timedelta(days=7)

        ## for the iqama expiry task
        iqama_expiry_records = self.env['hr.employee'].search([('iqama_expiry_date', '<=', date_now), ('iqama_expiry_date', '>=', datetime.date.today())])
        if iqama_expiry_records:
            for rec in iqama_expiry_records:
                self.env['project.task'].create({
                        'name': 'Iqama Expiry of ' + rec.name + ' on ' + str(rec.iqama_expiry_date),
                        'project_id': self.env['project.project'].search([('name', 'like','HR Task')]).id,
                        'stage_id': self.env['project.task.type'].search([('task_sequence','=',14)]).id,
                        'user_id': self.env['res.users'].search([('id', '=', 15)]).id,
                        'date_deadline': fields.Date.today() + timedelta(days=2),
                        'is_hr_task': True,
                        'description': 'This is the reminder, for the iqama expiry of ' + rec.name +'['+ str(rec.identification_id)+'] on ' + str(rec.iqama_expiry_date) + ' please do the best possible action.<br />Thanks'
                        })

        ## for the passport expiry task
        passport_expiry_records = self.env['hr.employee'].search([('passport_expiry_date', '<=', date_now), ('passport_expiry_date', '>=', datetime.date.today())])
        if passport_expiry_records:
            for rec in passport_expiry_records:
                self.env['project.task'].create({
                        'name': 'Passport Expiry of ' + rec.name + ' on ' + str(rec.passport_expiry_date),
                        'project_id': self.env['project.project'].search([('name', 'like','HR Task')]).id,
                        'stage_id': self.env['project.task.type'].search([('task_sequence', '=', 14)]).id,
                        'user_id': self.env['res.users'].search([('id', '=', 15)]).id,
                        'date_deadline': fields.Date.today() + timedelta(days=2),
                        'is_hr_task': True,
                        'description': 'This is the reminder, for the passport expiry of ' + rec.name + '['+ str(rec.identification_id)+'] on ' + str(rec.passport_expiry_date) + ' please do the best possible action.<br />Thanks'
                        })

        ## for the health certificate expiry task
        health_expiry_records = self.env['hr.employee'].search([('health_expiry_date', '<=', date_now), ('health_expiry_date', '>=', datetime.date.today())])
        if health_expiry_records:
            for rec in health_expiry_records:
                self.env['project.task'].create({
                        'name': 'Health Certificate Expiry of ' + rec.name + ' on ' + str(rec.health_expiry_date),
                        'project_id': self.env['project.project'].search([('name', 'like','HR Task')]).id,
                        'stage_id': self.env['project.task.type'].search([('task_sequence', '=', 14)]).id,
                        'user_id': self.env['res.users'].search([('id', '=', 15)]).id,
                        'date_deadline': fields.Date.today() + timedelta(days=2),
                        'is_hr_task': True,
                        'description': 'This is the reminder, for the health expiry of ' + rec.name + '['+ str(rec.identification_id)+'] on '+ str(rec.health_expiry_date) + ' please do the best possible action.<br />Thanks'
                        })

        ## for the insurance expiry task
        insurance_expiry_records = self.env['hr.employee'].search([('med_ins_expiry_date', '<=', date_now), ('med_ins_expiry_date', '>=', datetime.date.today())])
        if insurance_expiry_records:
            for rec in insurance_expiry_records:
                self.env['project.task'].create({
                        'name': 'Insurance Expiry of ' + rec.name + ' on ' + str(rec.med_ins_expiry_date),
                        'project_id': self.env['project.project'].search([('name', 'like','HR Task')]).id,
                        'stage_id': self.env['project.task.type'].search([('task_sequence', '=', 14)]).id,
                        'user_id': self.env['res.users'].search([('id', '=', 15)]).id,
                        'date_deadline': fields.Date.today() + timedelta(days=2),
                        'is_hr_task': True,
                        'description': 'This is the reminder, for the insurance expiry of ' + rec.name +'['+ str(rec.identification_id)+'] on ' + str(rec.med_ins_expiry_date) + ' please do the best possible action.<br />Thanks'
                        })


class InheritSubscriptionCustom(models.Model):
    _inherit = 'sale.subscription'

    def create_subscription_task(self):
        date_now = datetime.date.today() + timedelta(days=15)
        stages = self.env['sale.subscription.stage'].search([('name', '=', 'In Progress')])
        subs_record = self.env['sale.subscription'].search(
            [('recurring_next_date', '<=', date_now), ('recurring_next_date', '>=', datetime.date.today()),
             ('stage_id', '=', stages.id)])
        for rec in subs_record:
            self.env['project.task'].create({
                'name': 'Subscription Expiry- ' + rec.display_name + ' on ' + str(rec.recurring_next_date),
                'project_id': self.env['project.project'].search([('name', 'like','Rental Tasks')]).id,
                'stage_id': self.env['project.task.type'].search([('task_sequence','=',18)]).id,
                'user_id': self.env['res.users'].search([('id', '=', 13)]).id,
                'date_deadline': fields.Date.today() + timedelta(days=2),
                'is_rental_task': True,
                'description': 'This is the reminder, for the subscription expiry of ' + rec.display_name + ' on ' + str(rec.recurring_next_date) + ' please do the best possible action.<br />Thanks'
            })

class InheritContractCustom(models.Model):
    _inherit = 'hr.contract'

    ## Schedular function for creation of task when contract going to expiry ##
    ## Before two months of actual Contract ##
    def create_contract_task(self):
        date_now = datetime.date.today() + timedelta(days=60)
        contract_records = self.env['hr.contract'].search([('date_end', '<=', date_now), ('date_end', '>=', datetime.date.today()),('state', '=', 'open')])
        for rec in contract_records:
            if rec.date_end:
                if rec.date_end <= date_now and rec.date_end >= datetime.date.today():
                    self.env['project.task'].create({
                                            'name': 'Contract Expiry- ' + rec.name + ' on ' + str(rec.date_end),
                                            'project_id': self.env['project.project'].search([('name', 'like','HR Tasks')]).id,
                                            'stage_id': self.env['project.task.type'].search([('task_sequence', '=', 14)]).id,
                                            'user_id': self.env['res.users'].search([('id', '=', 15)]).id,
                                            'date_deadline': fields.Date.today() + timedelta(days=2),
                                            'is_hr_task': True,
                                            'description': 'This is the reminder, for the contract expiry of '+rec.name +'['+ str(rec.employee_id.identification_id)+'] on '+str(rec.date_end) + ' ,Please do the best possible action.<br />Thanks'
                                                })

    ## Before seven days of trial period expiry ##
    def create_trial_period_task(self):
        date_after_seven = datetime.date.today() + timedelta(days=7)
        contract_record_trial = self.env['hr.contract'].search([('trial_date_end', '<=', date_after_seven),('trial_date_end', '>=',datetime.date.today()),('state', '=', 'open')])
        for rec in contract_record_trial:
            if rec.trial_date_end:
                if date_after_seven == rec.trial_date_end - timedelta(days=7):
                    self.env['project.task'].create({
                        'name': 'Contract Expiry- ' + rec.name + ' on ' + str(rec.date_end),
                        'project_id': self.env['project.project'].search([('name', 'like','HR Tasks')]).id,
                        'stage_id': self.env['project.task.type'].search([('task_sequence', '=', 14)]).id,
                        'user_id': self.env['res.users'].search([('id', '=', 15)]).id,
                        'date_deadline': fields.Date.today() + timedelta(days=2),
                        'is_hr_task': True,
                        'description': 'This is the reminder, for the trial period expiry of ' + rec.name +'['+ str(rec.employee_id.identification_id)+'] on '+ str(rec.trial_date_end) + ' ,Please do the best possible action.<br />Thanks'
                    })


class InheritProjectCustom(models.Model):
    _inherit = 'project.task'
    payment_id = fields.Integer()
    is_payment = fields.Boolean(default=False)
    is_hr_task = fields.Boolean(default=False)
    is_rental_task = fields.Boolean(default=False)
    go_payment = fields.Boolean(default=False)
    sadad_no = fields.Char('Sadad/Cheque No')
    amount_payment = fields.Float()

    @api.multi
    def action_proceed_to_pay_rental(self):
        self.user_id = self.env['res.users'].search([('id', '=', 13)]).id
        self.stage_id = self.env['project.task.type'].search([('task_sequence', '=', 19)]).id
        self.is_rental_task = False
        self.go_payment = True

    @api.multi
    def action_proceed_to_pay(self):
        self.user_id = self.env['res.users'].search([('id', '=', 13)]).id
        self.stage_id = self.env['project.task.type'].search([('task_sequence', '=', 16)]).id
        self.is_hr_task = False
        self.go_payment = True

    @api.multi
    def action_create_payment(self):
        if not self.partner_id:
            raise UserError(_("Please select the Partner first."))
        if self.amount_payment == 0.0:
            raise UserError(_("Payment could not suppose to be zero amount, please Enter the Amount."))
        payment = self.env['account.payment'].create({
                                            'payment_type': 'outbound',
                                            'payment_method_id': 2,
                                            'partner_id': self.partner_id.id,
                                            'partner_type': 'supplier',
                                            'amount': self.amount_payment,
                                            'journal_id': 9,
                                            'payment_date': fields.Date.today(),
                                            'state': 'draft',
                                            'sadad_num': self.sadad_no
                                            })
        self.stage_id = self.env['project.task.type'].search([('task_sequence','=',17)]).id
        self.payment_id = payment.id
        self.is_payment = True
        self.go_payment = False


    @api.multi
    def action_payment_view(self):
        return {
            'name': _('Payment'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', '=',self.payment_id)],
        }


class InheritProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    task_sequence = fields.Char()


