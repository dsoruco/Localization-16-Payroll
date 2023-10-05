import logging

from odoo import api, models

from odoo.addons.hr_employee_firstname.models.hr_employee import UPDATE_PARTNER_FIELDS

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"


