# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class HrPayrollFiniquito(models.Model):
    _name = "hr.payroll.finiquito"
    _description = "Calculo del finiquito"

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,
                                  domain="[('active', '=', False)]")
    contract_id = fields.Many2one(related='employee_id.contract_id', string="Contrato", store=True)
    date_hire = fields.Date(related='employee_id.date_hired', string='Fecha contratación', required=True)
    date_end = fields.Date(related='employee_id.departure_date', string='Fecha fin del contrato', required=True)
    report_date = fields.Date(string='Fecha de reporte', required=True)

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('open', 'Abierto'),
        ('paid', 'Pagado'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')

    monthly_compensation1 = fields.Float(string="Remuneración Mensual mes 1", required=True)
    monthly_compensation2 = fields.Float(string="Remuneración Mensual mes 2", required=True)
    monthly_compensation3 = fields.Float(string="Remuneración Mensual mes 3", required=True)
    monthly_compensation_total = fields.Float(string="Remuneración Mensual total", compute='_compensation_total',
                                              store=True)

    seniority_bonus1 = fields.Float(string="Bono Antiguedad mes 1", required=True)
    seniority_bonus2 = fields.Float(string="Bono Antiguedad mes 2", required=True)
    seniority_bonus3 = fields.Float(string="Bono Antiguedad mes 3", required=True)
    seniority_bonus_total = fields.Float(string="Bono Antiguedad Total", compute='_seniority_bonus', store=True)

    border_bonus1 = fields.Float(string="Bono Frontera mes 1", required=True)
    border_bonus2 = fields.Float(string="Bono Frontera mes 2", required=True)
    border_bonus3 = fields.Float(string="Bono Frontera mes 3", required=True)
    border_bonus_total = fields.Float(string="Bono Frontera Total", compute='_border_bonus', store=True)

    commissions1 = fields.Float(string="Comisiones mes 1", required=True)
    commissions2 = fields.Float(string="Comisiones mes 2", required=True)
    commissions3 = fields.Float(string="Comisiones mes 3", required=True)
    commissions_total = fields.Float(string="Comisiones Total", compute='_commissions', store=True)

    overtime1 = fields.Float(string="Horas Extras mes 1", required=True)
    overtime2 = fields.Float(string="Horas Extras mes 2", required=True)
    overtime3 = fields.Float(string="Horas Extras mes 3", required=True)
    overtime_total = fields.Float(string="Horas Extras Total", compute='_overtime', store=True)

    other_bonuses1 = fields.Float(string="Otros bonos 1", required=True)
    other_bonuses2 = fields.Float(string="Otros bonos 2", required=True)
    other_bonuses3 = fields.Float(string="Otros bonos 3", required=True)
    other_bonuses_total = fields.Float(string="Otros bonos total", compute='_other_bonuses', store=True)

    total1 = fields.Float(string="Total 1", compute='_get_total_colum1', store=True)
    total2 = fields.Float(string="Total 2", compute='_get_total_colum2', store=True)
    total3 = fields.Float(string="Total 3", compute='_get_total_colum3', store=True)
    total_total = fields.Float(string="Total", compute='_get_total', store=True)

    average = fields.Float(string="Promedio", compute='_get_average', store=True)

    has_eviction = fields.Boolean(string="Tiene Desahucio", required=True)
    eviction = fields.Float(string="Desahucio", compute='_get_eviction', store=True)

    indemnity_year = fields.Integer(string="Cantidad de Años", required=True)
    indemnity_year_amount = fields.Float(string="Años Importe", compute='_get_indemnity_year_amount', store=True)
    indemnity_month = fields.Integer(string="Cantidad de Meses", required=True)
    indemnity_month_amount = fields.Float(string="Meses Importe", compute='_get_indemnity_month_amount', store=True)
    indemnity_day = fields.Integer(string="Cantidad de días", required=True)
    indemnity_day_amount = fields.Float(string="Días Importe", compute='_get_indemnity_day_amount', store=True)

    christmas_bonus_month = fields.Integer(string="Aguinaldo meses", required=True)
    christmas_bonus_month_amount = fields.Float(string="Importe de Aguinaldo",
                                                compute='_get_christmas_bonus_month_amount', store=True)

    christmas_bonus_day = fields.Integer(string="Aguinaldo dias", required=True)
    christmas_bonus_day_amount = fields.Float(string="Importe de Aguinaldo en días",
                                              compute='_get_christmas_bonus_day_amount', store=True)

    holidays_days = fields.Integer(string="Días de vacaciones", required=True)
    holidays_amount = fields.Float(string="Importe de vacaciones", compute='_get_holidays_amount_amount', store=True)

    other_extraordinary_bonuses = fields.Float(string="Otros Bonos extraordinarios", required=True)

    has_penalties = fields.Boolean(string="Tiene Multa", required=True)
    penalties = fields.Float(string="Multas", compute='_get_penalties', store=True)

    finiquito = fields.Float(string="Finiquito", compute='_get_finiquito', store=True)

    def action_period_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_period_open(self):
        self.write({'state': 'open'})
        return True

    def action_period_closed(self):
        self.write({'state': 'closed'})
        return True

    @api.depends('monthly_compensation1', 'monthly_compensation2', 'monthly_compensation3')
    def _compensation_total(self):
        for record in self:
            record.monthly_compensation_total = record.monthly_compensation1 + record.monthly_compensation2 + record.monthly_compensation3

    @api.depends('seniority_bonus1', 'seniority_bonus2', 'seniority_bonus3')
    def _seniority_bonus(self):
        for record in self:
            record.seniority_bonus_total = record.seniority_bonus1 + record.seniority_bonus2 + record.seniority_bonus3

    @api.depends('border_bonus1', 'border_bonus2', 'border_bonus3')
    def _border_bonus(self):
        for record in self:
            record.border_bonus_total = record.border_bonus1 + record.border_bonus2 + record.border_bonus3

    @api.depends('commissions1', 'commissions2', 'commissions3')
    def _commissions(self):
        for record in self:
            record.commissions_total = record.commissions1 + record.commissions2 + record.commissions3

    @api.depends('overtime1', 'overtime2', 'overtime3')
    def _overtime(self):
        for record in self:
            record.overtime_total = record.overtime1 + record.overtime2 + record.overtime3

    @api.depends('other_bonuses1', 'other_bonuses2', 'other_bonuses3')
    def _other_bonuses(self):
        for record in self:
            record.other_bonuses_total = record.other_bonuses1 + record.other_bonuses2 + record.other_bonuses3

    @api.depends('monthly_compensation1', 'seniority_bonus1', 'border_bonus1', 'commissions1', 'overtime1',
                 'other_bonuses1')
    def _get_total_colum1(self):
        for record in self:
            record.total1 = record.monthly_compensation1 + record.seniority_bonus1 + record.border_bonus1 + record.commissions1 + record.overtime1 + record.other_bonuses1

    @api.depends('monthly_compensation2', 'seniority_bonus2', 'border_bonus2', 'commissions2', 'overtime2',
                 'other_bonuses2')
    def _get_total_colum2(self):
        for record in self:
            record.total2 = record.monthly_compensation2 + record.seniority_bonus2 + record.border_bonus2 + record.commissions2 + record.overtime2 + record.other_bonuses2

    @api.depends('monthly_compensation3', 'seniority_bonus3', 'border_bonus3', 'commissions3', 'overtime3',
                 'other_bonuses3')
    def _get_total_colum3(self):
        for record in self:
            record.total3 = record.monthly_compensation3 + record.seniority_bonus3 + record.border_bonus3 + record.commissions3 + record.overtime3 + record.other_bonuses3

    @api.depends('total1', 'total2', 'total3')
    def _get_total(self):
        for record in self:
            record.total_total = record.total1 + record.total2 + record.total3

    @api.depends('total_total')
    def _get_average(self):
        for record in self:
            record.average = record.total_total / 3

    @api.depends('average', 'has_eviction')
    def _get_eviction(self):
        for record in self:
            if record.has_eviction:
                record.eviction = record.average * 3
            else:
                record.eviction = 0

    @api.depends('average', 'indemnity_year')
    def _get_indemnity_year_amount(self):
        for record in self:
            record.indemnity_year_amount = record.average * record.indemnity_year

    @api.depends('average', 'indemnity_month')
    def _get_indemnity_month_amount(self):
        for record in self:
            record.indemnity_month_amount = record.average / 12 * record.indemnity_month

    @api.depends('average', 'indemnity_day')
    def _get_indemnity_day_amount(self):
        for record in self:
            record.indemnity_day_amount = record.average / 360 * record.indemnity_day

    @api.depends('average', 'christmas_bonus_month')
    def _get_christmas_bonus_month_amount(self):
        for record in self:
            record.christmas_bonus_month_amount = record.average / 12 * record.christmas_bonus_month

    @api.depends('average', 'christmas_bonus_day')
    def _get_christmas_bonus_day_amount(self):
        for record in self:
            record.christmas_bonus_day_amount = record.average / 360 * record.christmas_bonus_day

    @api.depends('average', 'holidays_days')
    def _get_holidays_amount_amount(self):
        for record in self:
            record.holidays_amount = record.average / 30 * record.holidays_days

    @api.depends('eviction', 'indemnity_year_amount', 'indemnity_month_amount', 'indemnity_day_amount',
                 'christmas_bonus_month_amount', 'christmas_bonus_day_amount', 'holidays_amount',
                 'other_extraordinary_bonuses', 'has_penalties')
    def _get_penalties(self):
        total = 0
        for record in self:
            if record.has_penalties:
                if record.has_eviction:
                    total += record.eviction
                total += record.indemnity_year_amount + record.indemnity_month_amount + record.indemnity_day_amount + \
                         record.christmas_bonus_month_amount + record.christmas_bonus_day_amount + record.holidays_amount + \
                         record.other_extraordinary_bonuses

                record.penalties = total * 0.30
            else:
                record = 0

    @api.depends('eviction', 'indemnity_year_amount', 'indemnity_month_amount', 'indemnity_day_amount',
                 'christmas_bonus_month_amount', 'christmas_bonus_day_amount', 'holidays_amount',
                 'other_extraordinary_bonuses', 'penalties')
    def _get_finiquito(self):
        total = 0
        for record in self:
            if record.has_eviction:
                total += record.eviction
            if record.has_penalties:
                total += record.penalties
            total += record.indemnity_year_amount + record.indemnity_month_amount + record.indemnity_day_amount + \
                     record.christmas_bonus_month_amount + record.christmas_bonus_day_amount + record.holidays_amount + \
                     record.other_extraordinary_bonuses

            record.finiquito = total

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.holidays_days = self.employee_id.remaining_leave_year
        self.indemnity_year = self.employee_id.balance
        self.indemnity_month = indemnity_accumulated_month(self.employee_id)
        self.indemnity_day = indemnity_accumulated_day(self.employee_id)
        self.christmas_bonus_month = christmas_bonus_accumulated_month(self.employee_id)
        self.christmas_bonus_day = christmas_bonus_accumulated_day(self.employee_id)
        values_basic = self.get_previous_month_rule('BASIC')
        if values_basic:
            self.monthly_compensation1 = values_basic['mes 1']
            self.monthly_compensation2 = values_basic['mes 2']
            self.monthly_compensation3 = values_basic['mes 3']
        values_basic = self.get_previous_month_rule('BONO_ANT')
        if values_basic:
            self.seniority_bonus1 = values_basic['mes 1']
            self.seniority_bonus2 = values_basic['mes 2']
            self.seniority_bonus3 = values_basic['mes 3']
        values_basic = self.get_previous_month_rule('SUBS_FRONTERA')
        if values_basic:
            self.border_bonus1 = values_basic['mes 1']
            self.border_bonus2 = values_basic['mes 2']
            self.border_bonus3 = values_basic['mes 3']
        # values_basic = self.get_previous_month_rule('SUBS_FRONTERA')
        # if values_basic:
            # self.commissions1 = values_basic['mes 1']
            # self.commissions2 = values_basic['mes 2']
            # self.commissions3 = values_basic['mes 3']
        values_basic = self.get_previous_month_rule('EXTRAS')
        if values_basic:
            self.overtime1 = values_basic['mes 1']
            self.overtime2 = values_basic['mes 2']
            self.overtime3 = values_basic['mes 3']
        values_basic = self.get_previous_month_rule('BONO_PROD')
        if values_basic:
            self.other_bonuses1 = values_basic['mes 1']
            self.other_bonuses2 = values_basic['mes 2']
            self.other_bonuses3 = values_basic['mes 3']


    @api.constrains('employee_id', 'contract_id')
    def _check_unique_employee_contract(self):
        for finiquito in self:
            existing_finiquitos = self.env['hr.payroll.finiquito'].search([
                ('employee_id', '=', finiquito.employee_id.id),
                ('contract_id', '=', finiquito.contract_id.id),
                ('id', '!=', finiquito.id)  # Exclude the current record
            ])
            if existing_finiquitos:
                raise ValidationError("Ya existe un registro de finiquito con el mismo empleado y contrato.")

    def get_previous_month_rule(self, ruler):
        domain = [('employee_id', '=', self.employee_id.id),
                  ('contract_id', '=', self.contract_id.id)]
        closing_table = self.env['hr.payroll.closing.table'].search(domain,  order='date_to desc', limit=3)
        values = {}
        amount = 0
        for idx, record in enumerate(reversed(closing_table), start=1):
            if ruler == 'BASIC':
                amount = record.basic
            if ruler == 'BONO_ANT':
                amount = record.antiquity_bonus
            if ruler == 'BONO_PROD':
                amount = record.production_bonus
            if ruler == 'SUBS_FRONTERA':
                amount = record.frontier_subsidy
            if ruler == 'EXTRAS':
                amount = record.overtime_amount
            if ruler == 'DOMINGO':
                amount = record.sunday_overtime_amount
            if ruler == 'RECARGO':
                amount = record.night_overtime_hours_amount
            if ruler == 'NET':
                amount = record.net_salary
            if ruler == 'PRIMA':
                amount = record.prima
            if ruler == 'GROSS':
                amount = record.gross
            values['mes {}'.format(idx)] = amount
        return values


def indemnity_accumulated_month(employee_id):
    if employee_id.date_hired:
        date_hired_this_year = date(date.today().year, employee_id.date_hired.month, employee_id.date_hired.day)
        db_today = datetime.now().date()
        diff = relativedelta(db_today, date_hired_this_year)
        return diff.months
    else:
        return 0


def indemnity_accumulated_day(employee_id):
    if employee_id.date_hired:
        date_hired_this_year = date(date.today().year, employee_id.date_hired.month, employee_id.date_hired.day)
        db_today = datetime.now().date()
        diff = relativedelta(db_today, date_hired_this_year)
        return diff.days
    else:
        return 0


def christmas_bonus_accumulated_month(employee_id):
    date_init = date(date.today().year, 1, 1)
    diff = relativedelta(employee_id.departure_date, date_init)
    return diff.months


def christmas_bonus_accumulated_day(employee_id):
    if employee_id.departure_date:
        date_init_month = date(date.today().year, employee_id.departure_date.month, 1)
        diff = relativedelta(employee_id.departure_date, date_init_month)
        return diff.days
    else:
        return 0

