import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Datos quinquenio
    balance = fields.Float(string="Saldo", compute='_compute_balance', store=True)
    quinquennial_ids = fields.One2many('hr.payroll.quinquennial.data', 'employee_id', string='Pago quinquenal')

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
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    contract_id = fields.Many2one(related='employee_id.contract_id', string="contract employee")
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

    @api.constrains('employee_id')
    def _check_employee_contract(self):
        for record in self:
            if not record.employee_id.contract_id:
                raise ValidationError("Error: No se puede adicionar pago quinquenal sin contrato asociado para el empleado.")


