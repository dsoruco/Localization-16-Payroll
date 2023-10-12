# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models


class EmployeePersonnelArea(models.Model):

    _name = "hr.employee.personnel.area"
    _description = "Área de personal"

    code = fields.Char('Código', required=True)
    name = fields.Char(string="Área de personal", translate=True, required=True)
    personnel_group_id = fields.Many2one('hr.employee.personnel.group', string="Grupo de personal", required=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "El código ya existe !"),
    ]
