# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Company(models.Model):
    _inherit = 'res.company'
    # ---------   Contingente de vacaciones    ---------------------------------------
    vacation_quota_table_ids = fields.One2many('hr.vacation.quota.table', 'company_id', string='Contingente de Vacaciones')


class HrVacationQuotaTable(models.Model):
    _name = 'hr.vacation.quota.table'
    _description = 'Contingente de Vacaciones'
    _rec_name = 'description'

    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    years_of_service_start = fields.Integer(string="Años de antiguedad comienzo")
    years_of_service_end = fields.Integer(string="Años de antiguedad fin")
    vacation_days = fields.Integer(string="Días de vacaciones")
    description = fields.Char(string="Descripción", readonly=True, compute='_compute_description', store=True)

    @api.depends('years_of_service_start', 'years_of_service_end', 'vacation_days')
    def _compute_description(self):
        years_of_service_start = 0
        years_of_service_end = 0
        vacation_days = 0
        for rec in self:
            if rec.years_of_service_start:
                years_of_service_start = rec.years_of_service_start
            if rec.years_of_service_end:
                years_of_service_end = rec.years_of_service_end
            if rec.vacation_days:
                vacation_days = rec.vacation_days
            rec.description = 'De ' + str(years_of_service_start) + ' a ' + str(years_of_service_end) + ' años de antigüedad ' + str(vacation_days) + ' días de vacaciones'

