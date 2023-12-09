# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models


class EmployeeStaffDivision(models.Model):

    _name = "hr.payroll.finiquito"
    _description = "Calculo del finiquito"

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True)
    date_hire = fields.Date(string='Fecha contratación', required=True)
    date_end = fields.Date(string='Fecha fin del contrato', required=True)
    report_date = fields.Date(string='Fecha de reporte', required=True)

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('open', 'Abierto'),
        ('paid', 'Pagado'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')

    monthly_compensation1 = fields.Float(string="Remuneración Mensual mes 1", required=True)
    monthly_compensation2 = fields.Float(string="Remuneración Mensual mes 2", required=True)
    monthly_compensation3 = fields.Float(string="Remuneración Mensual mes 3", required=True)
    monthly_compensation_total = fields.Float(string="Remuneración Mensual total", required=True)

    seniority_bonus1 = fields.Float(string="Bono Antiguedad mes 1", required=True)
    seniority_bonus2 = fields.Float(string="Bono Antiguedad mes 2", required=True)
    seniority_bonus3 = fields.Float(string="Bono Antiguedad mes 3", required=True)
    seniority_bonus_total = fields.Float(string="Bono Antiguedad Total", required=True)

    commissions1 = fields.Float(string="Comisiones mes 1", required=True)
    commissions2 = fields.Float(string="Comisiones mes 2", required=True)
    commissions3 = fields.Float(string="Comisiones mes 3", required=True)
    commissions_total = fields.Float(string="Comisiones Total", required=True)

    overtime1 = fields.Float(string="Horas Extras mes 1", required=True)
    overtime2 = fields.Float(string="Horas Extras mes 2", required=True)
    overtime3 = fields.Float(string="Horas Extras mes 3", required=True)
    overtime_total = fields.Float(string="Horas Extras Total", required=True)

    other_bonuses1 = fields.Float(string="Otros bonos 1", required=True)
    other_bonuses2 = fields.Float(string="Otros bonos 2", required=True)
    other_bonuses3 = fields.Float(string="Otros bonos 3", required=True)
    other_bonuses_total = fields.Float(string="Otros bonos total", required=True)

    total1 = fields.Float(string="Total 1", required=True)
    total2 = fields.Float(string="Total 2", required=True)
    total3 = fields.Float(string="Total 3", required=True)

    average = fields.Float(string="Promedio", required=True)

    has_eviction = fields.Boolean(string="Tiene Desahucio", required=True)
    eviction = fields.Float(string="Desahucio", required=True)

    indemnity = fields.Float(string="Indemnización", required=True)
    indemnity_year = fields.Integer(string="Cantidad de Años", required=True)
    indemnity_year_amount = fields.Float(string="Años Importe", required=True)
    indemnity_month = fields.Integer(string="Cantidad de Meses", required=True)
    indemnity_month_amount = fields.Float(string="Meses Importe", required=True)
    indemnity_day = fields.Integer(string="Cantidad de días", required=True)
    indemnity_day_amount = fields.Float(string="Días Importe", required=True)

    christmas_bonus_month = fields.Integer(string="Aguinaldo meses", required=True)
    christmas_bonus_amount = fields.Float(string="Importe de Aguinaldo", required=True)

    holidays_days = fields.Integer(string="Días de vacaciones", required=True)
    holidays_amount = fields.Float(string="Importe de vacaciones", required=True)

    other_extraordinary_bonuses = fields.Float(string="Otros Bonos extraordinarios", required=True)

    has_penalties = fields.Boolean(string="Tiene Multa", required=True)

    tota_finiquito = fields.Boolean(string="Finiquito", required=True)

    def action_period_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_period_open(self):
        self.write({'state': 'open'})
        return True

    def action_period_closed(self):
        self.write({'state': 'closed'})
        return True







