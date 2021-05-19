from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import xlwt
import io
import base64
from io import StringIO
from datetime import datetime

class SalesTax_report(models.Model):
    _name = 'payslip.bank.report'

    name = fields.Char('name')
    date_from = fields.Date(string='Date From', required=1)
    date_to = fields.Date(string='Date To', required=1)
    sponsor = fields.Many2many('hr.sponsors',string='Sponsors')
    structure_salary = fields.Many2many('hr.payroll.structure', string='Salary Structure')
    payslip_report_line_id = fields.One2many('payslip.bank.report.line', 'payslip_report_id', string='Payslip Report Lines')
    report = fields.Binary('Excel File', filters='.xls', readonly=True)
    name_r = fields.Char('File Name', size=32)

    @api.multi
    def generate_report_lines(self):
        sponsors = []
        structure = []
        line = 0
        document_name = ''
        self.payslip_report_line_id = False
        self.name = 'Payslip Bank Report ' + str(self.id)
        payslips_record = self.env['hr.payslip'].search(
            [('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),('state','in',['Final Reviewed','done']),('company_id','=',self.env.user.company_id.id)])

        for records in self.sponsor:
            sponsors.append(records.id)

        for record in self.structure_salary:
            structure.append(record.id)

        for rec in payslips_record:
            for items in structure:
                if rec.struct_id.id == items:
                    line +=1
                    total_allowance = ((rec.rule_other_llowance)+(rec.rule_transportation_allowance)+(rec.rule_food_allowance)+(rec.rule_phone_allowance)+(rec.rule_employee_rewards)+(rec.rule_overtime))
                    total_deduction = ((abs(rec.rule_loan_deducted))+(abs(rec.rule_deductions_violations))+(abs(rec.rule_absence_deducted))+(abs(rec.rule_gosi_employee_share)))
                    self.env['payslip.bank.report.line'].create({'payslip_report_id': self.id,
                                                                 'sno': line,
                                                                 'employee_no': rec.employee_id.employee_number,
                                                                 'employee_id': rec.employee_id.id,
                                                                 'basic_sal': rec.rule_basic,
                                                                 'house_allowance': rec.rule_house_allowance,
                                                                 'other_allowance': total_allowance,
                                                                 'deductions': total_deduction,
                                                                 'total_amount': (((rec.rule_basic)+(rec.rule_house_allowance) + total_allowance) - (total_deduction)),
                                                                 'narration': 'Salary ' + str(rec.year)})

    @api.multi
    def generate_xls_report(self):
        if len(self.payslip_report_line_id) < 1:
            raise UserError(_("Please Generate Report Lines."))
        self.ensure_one()
        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Payslip Detail')
        fp = io.BytesIO()
        sub_header_style = xlwt.easyxf("font: name Helvetica size 11 px, bold 1, height 200; align: horiz center")
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170;align: horiz center")
        row = 1
        col = 0
        ws1.write(0, 0, 'Employee ID', sub_header_style)
        ws1.write(0, 1, 'Employee Resident ID', sub_header_style)
        ws1.write(0, 2, 'Employee Bank ID', sub_header_style)
        ws1.write(0, 3, 'Employee Account Number', sub_header_style)
        ws1.write(0, 4, 'Employee Name', sub_header_style)
        ws1.write(0, 5, 'Payment Amount', sub_header_style)
        ws1.write(0, 6, 'Employee Basic Salary', sub_header_style)
        ws1.write(0, 7, 'Housing Allowance', sub_header_style)
        ws1.write(0, 8, 'Other Earnings', sub_header_style)
        ws1.write(0, 9, 'Deductions', sub_header_style)
        ws1.write(0, 10, 'Beneficiary Narration', sub_header_style)

        for rec in self.payslip_report_line_id:
            ws1.write(row, col, rec.sno, line_content_style)
            ws1.write(row, col + 1, rec.employee_iqama, line_content_style)
            ws1.write(row, col + 2, rec.bank_code, line_content_style)
            ws1.write(row, col + 3, rec.employee_account_no, line_content_style)
            ws1.write(row, col + 4, rec.employee_id.name, line_content_style)
            ws1.write(row, col + 5, rec.total_amount, line_content_style)
            ws1.write(row, col + 6, rec.basic_sal, line_content_style)
            ws1.write(row, col + 7, rec.house_allowance, line_content_style)
            ws1.write(row, col + 8, rec.other_allowance, line_content_style)
            ws1.write(row, col + 9, rec.deductions, line_content_style)
            ws1.write(row, col + 10, rec.narration, line_content_style)
            row += 1

        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'report': out, 'name_r': 'payslip_report.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payslip.bank.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
        }


class SalesTax_report_line(models.Model):
    _name = 'payslip.bank.report.line'

    sno = fields.Integer('Sr')
    payslip_report_id = fields.Many2one('payslip.bank.report', string='Report Line')
    employee_id = fields.Many2one('hr.employee')
    employee_no = fields.Char(related='employee_id.employee_number')
    employee_iqama = fields.Char(related='employee_id.identification_id')
    employee_account_no = fields.Char(related='employee_id.iban_number')
    bank_code = fields.Char(related='employee_id.Bank_name_id.bic')
    basic_sal = fields.Float()
    house_allowance = fields.Float()
    other_allowance = fields.Float()
    deductions = fields.Float()
    total_amount = fields.Float()
    narration = fields.Char()


