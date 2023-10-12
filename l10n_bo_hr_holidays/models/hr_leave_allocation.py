# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)

from collections import defaultdict
import logging

from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.addons.hr_holidays.models.hr_leave import get_employee_from_context
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_round
from odoo.tools.date_utils import get_timedelta
from odoo.osv import expression


_logger = logging.getLogger(__name__)

class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'


