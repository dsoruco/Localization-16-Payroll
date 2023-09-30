# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.web_editor.controllers.main import handle_history_divergence


class HrJob(models.Model):
    _inherit = 'hr.job'

    ceco = fields.Char(string="CECO")
