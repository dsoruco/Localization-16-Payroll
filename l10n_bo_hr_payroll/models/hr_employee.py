import logging

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Datos quinquenio
    balance = fields.Float(string="Saldo", compute='_compute_balance', store=True)
    years_of_service = fields.Integer(string="Años de antigüedad", compute='_compute_years_of_service', store=True)
    quinquennial_ids = fields.One2many('hr.payroll.quinquennial.data', 'employee_id', string='Pago quinquenal')

    @api.depends('contract_ids.date_start')
    def _compute_years_of_service(self):
        for record in self:
            if record.contract_ids:
                date_hired = min(record.contract_ids.mapped('date_start'))
                current_date = fields.Date.today()
                delta_years = relativedelta(current_date, date_hired).years
                record.years_of_service = delta_years
            else:
                record.years_of_service = 0

    @api.depends('years_of_service', 'quinquennial_ids.amount_years')
    def _compute_balance(self):
        for record in self:
            total_amount_years = sum(record.quinquennial_ids.mapped('amount_years'))
            record.balance = record.years_of_service - total_amount_years


class HrPayrollQuinquennialData(models.Model):
    _name = 'hr.payroll.quinquennial.data'
    _description = 'Datos Quinquenio'
    _rec_name = "employee_id"

    payslip_id = fields.Many2one('hr.payslip')
    contract_id = fields.Many2one('hr.contract', 'Contract', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    # Campo calculado entre la fecha de consulta y la fecha de inicio de contrato menos la cantidad
    # de años pagados

    type_of_payment = fields.Selection([
        ('0001', 'Pago de Quinquenio'),
        ('0002', 'Adelanto de Quinquenio')],
        string='Clase de documento', default='0001')

    amount_years = fields.Integer(string = "Cantidad")
    date_from = fields.Date(string='Fecha de inicio', help="Fecha de inicio de formulario de pago de quinquenio", required=True)
    date_to = fields.Date(string='Fecha fin', help="Fecha fin de formulario de pago de quinquenio", required=True)
    date_pay = fields.Date(string='Fecha de pago',  help="Fecha de pago de quinquenio", required=True)
