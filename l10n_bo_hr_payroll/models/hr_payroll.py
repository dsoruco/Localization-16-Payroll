# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import ValidationError
import time
from datetime import datetime, timedelta
from dateutil import relativedelta


class HrPayrollClosingTable(models.Model):
    _name = 'hr.payroll.closing.table'
    _description = 'Tabla Cierre de nómina'
    _rec_name = "employee_id"

    payslip_id = fields.Many2one('hr.payslip')
    contract_id = fields.Many2one('hr.contract', 'Contract', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee',required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
# Reglas --------------------------------------------------
    basic = fields.Float(string="Salario basico", required=True)
    antiquity_bonus = fields.Float(string="Bono de antigüedad", required=True)
    production_bonus = fields.Float(string="Bono de producción", required=True)
    frontier_subsidy = fields.Float(string="Subsidio de frontera", required=True)
    overtime_night_work = fields.Float(string="Trabajo extraordinario y nocturno", required=True)
    sunday_and_sun_work = fields.Float(string="Dominical y Domingo Trabajado", required=True)
    other_bonuses = fields.Float(string="Otros bonos", required=True)
    net_salary = fields.Float(string="Salario neto", required=True)
    credit_next_month = fields.Float(string="Saldo proximo mes", required=True)

# Categorias ----------------------------------------------
    gross = fields.Float(string="Salario devengado", required=True)
# Dias  ----------------------------------------------------
    worked_days = fields.Float(string="Días trabajados", required=True)

    @api.constrains('date_from', 'date_to', 'contract_id')
    def _check_leave(self):
        for closing_table in self:
            if closing_table.date_from and closing_table.date_to and closing_table.contract_id:
                register_leaves = self.search([('date_from', '=', closing_table.date_from),
                                               ('date_to', '=', closing_table.date_to),
                                               ('contract_id', '=', closing_table.contract_id.id)])
                if len(register_leaves) > 1:
                    raise ValidationError(_('No puedes crear dos registro para el trabajador en el mismo periodo de tiempo.'))


