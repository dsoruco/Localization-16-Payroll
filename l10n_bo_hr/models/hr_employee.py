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

    # severance  = fields.Selection([
    #     ('PV', 'Porvenir'),
    #     ('PT', 'Proteccion'),
    #     ('C', 'Colfondos')],
    #     string='Cesantia')
