# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    type_identification_document = fields.Selection([
        ('01', 'Cédula de identidad'),
        ('02', 'Licencia de Conducir'),
        ('03', 'Código de Dependiente')],
        string='Clase de documento', default='01')

    valid_date = fields.Date(string='Fecha de validez')

    document_number = fields.Char(string="Numero de documento")

    document_extension = fields.Selection([
        ('SC', 'SC Santa Cruz'),
        ('CB', 'CB Cochabamba ')],
        string='Extensión de documento', default='SC')

    # Datos de la AFP
    afp_subtype = fields.Selection([
        ('01', 'Previsión'),
        ('02', 'Futuro'),
        ('03', 'Gestora')],
        string='Subtipo')

    afp_nua_cua = fields.Char(string="NUA/CUA")

    aft_quotation_type = fields.Selection([
        ('1', 'Dependiente o asegurado con pensión del sip < 65 años que aporta'),
        ('8', 'Dependiente o asegurado con pensión del sip > 65 años que aporta'),
        ('C', 'Asegurado con pensión del sip < 65 años que no aporta'),
        ('D', 'Asegurado con pensión del sip > 65 años que no aporta')],
        string='Tipo de Cotización')

    afp_retired = fields.Boolean('Jubilado', help='Para identificar que el empleado esta jubilado', default=False)

    afp_retired_date = fields.Date(string='Retire date',
                                   help='Identifica la fecha en que se jubila el empleado')

    afp_age = fields.Char(string="Edad")

    # Asignación organizativa
    staff_division_id = fields.Many2one('hr.employee.staff.division', string='División de personal')
    staffing_subdivision_id = fields.Many2one('hr.employee.staffing.subdivision', string='SubDivisión de personal')
    personnel_area_id = fields.Many2one('hr.employee.personnel.area', string='Área de personal')
    personnel_group_id = fields.Many2one('hr.employee.personnel.group', string='Grupo de personal')
    payroll_area_id = fields.Many2one('hr.employee.payroll.area', string='Área de nómina')

    # Para mostrar el código de la plaza
    ceco = fields.Char(related='job_id.ceco', readonly=True, string="CECO")