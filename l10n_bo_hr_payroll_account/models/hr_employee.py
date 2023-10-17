# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Para mostrar el código de la plaza
    ceco = fields.Many2one(related='job_id.ceco', readonly=True, string="CECO")



