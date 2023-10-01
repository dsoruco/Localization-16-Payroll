# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import fields, models


class EmployeePersonnelGroup(models.Model):

    _name = "hr.employee.personnel.group"
    _description = "Grupo de personal"


    code = fields.Char('Código', required=True)
    name = fields.Char(string="Grupo de personal", translate=True, required=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "El código ya existe !"),
    ]
