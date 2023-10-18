# -*- coding:utf-8 -*-

from odoo import api, fields, models, tools, _


# This will generate 16th of days
ROUNDING_FACTOR = 16


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
            'leave_antiquity_bonus': leave_antiquity_bonus,
        })
        return res

    def _get_antiquity_bonus(self, employee):

        percent = 0
        years_of_service = employee.years_of_service
        domain = [('years_of_antiquity_bonus_start', '<', years_of_service)]
        leave_antiquity = self.env['hr.antiquity.bonus.table'].search(domain, limit=1, order="years_of_antiquity_bonus_start desc")
        if leave_antiquity:
            percent = leave_antiquity.percentage

        return percent


def leave_antiquity_bonus(payslip, employee):
    leave_leave_antiquity_bonus_percen = 0
    if payslip:
        leave_leave_antiquity_bonus_percen = payslip.dict._get_antiquity_bonus(employee)

    return leave_leave_antiquity_bonus_percen





