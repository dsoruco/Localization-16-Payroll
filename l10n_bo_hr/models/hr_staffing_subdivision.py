# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models


class EmployeeStaffingSubdivision(models.Model):

    _name = "hr.employee.staffing.subdivision"
    _description = "SubDivisión de personal"


    code = fields.Char('Código', required=True)
    name = fields.Char(string="SubDivisión de personal", translate=True, required=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "El código ya existe !"),
    ]
