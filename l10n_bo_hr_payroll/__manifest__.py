{
    'name': "Datec: Nómina Bolivia",
    'version': '16.0.0.0.1',
    'depends': ['hr_payroll', 'l10n_bo_hr', 'l10n_bo_hr_holidays', 'hr_bo_employee_lastnames'],
    'author': "Datec",
    'license': 'OPL-1',
    'category': 'Payroll Localization',
    'description': """
    Bolivia Payroll Localization
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_view.xml',
        'views/hr_payroll_closing_table_view.xml',
        # 'report/hr_employee_payroll_report_views.xml',

    ],
}
