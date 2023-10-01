# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models


class EmployeePayrollArea(models.Model):

    _name = "hr.employee.payroll.area"
    _description = "Área de nómina"


    code = fields.Char('Código', required=True)
    name = fields.Char(string="Área de nómina", translate=True, required=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "El código ya existe !"),
    ]
