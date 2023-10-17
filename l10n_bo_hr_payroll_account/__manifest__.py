#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Datec: Nómina y contabilidad Bolivia',
    'version': '16.0.0.0.2',
    'depends': ['l10n_bo_hr_payroll', 'hr_payroll_account', 'analytic', 'hr_recruitment'],
    'author': "Datec",
    'license': 'OPL-1',
    'category': 'Payroll Localization',
    'website': "",
    'description': """
        Bolivia Payroll Account Localization
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/hr_job_views.xml',
        'views/hr_employee_view.xml',
    ],
    "development_status": "Beta",
    "application": True,
    "installable": True,
}
