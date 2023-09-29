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

    # eps_id = fields.Many2one('res.partner', string='Entidad promotora de salud', domain=[('l10n_co_eps', '=', True)])
    #
    # afp_id = fields.Many2one('res.partner', string='Administradora de fondo de penciones', domain=[('l10n_co_afp', '=', True)])
    #
    # arl_id = fields.Many2one('res.partner', string='Administradora de riesgos laborales', domain=[('l10n_co_arl', '=', True)])
    #
    # caja_id = fields.Many2one('res.partner', string='Caja de compensación familiar', domain=[('l10n_co_caja', '=', True)])

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