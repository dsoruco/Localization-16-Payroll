# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date



class HrEmployeeDocs(models.Model):
    _name = 'l10n_bo_hr.employee_docs'
    _description = 'Documentos adjuntos del empleado'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        copy=False
    )
    attachment = fields.Binary(
        string='Doc',
        attachment=True
    )
    
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
    )
    
    

    

    


