#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Datec: Nómina y contabilidad Bolivia',
    'version': '16.0.0.0.0',
    'depends': ['l10n_bo_hr_payroll', 'hr_payroll_account'],
    'author': "Datec",
    'license': 'OPL-1',
    'category': 'Payroll Localization',
    'website': "",
    'description': """
        Bolivia Payroll Account Localization
    """,
    'data': [
        'security/ir.model.access.csv',
        # 'views/hr_payroll_account_views.xml',
    ],
}
