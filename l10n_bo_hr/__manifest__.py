{
    'name': "Datec: Nómina Bolivia",
    'version': '16.0.0.0.0',
    'depends': ['hr_bo_employee_lastnames'],
    'author': "Datec",
    'license': 'OPL-1',
    'category': 'Payroll Localization',
    'description': """
    Bolivia Payroll Localization
    """,
    "depends": ["mail"],
    'data': [
        # 'data/',
        'security/ir.model.access.csv',
        'views/hr_job_views.xml',
        'views/hr_employee_view.xml',
        'wizard/hr_departure_wizard_views.xml',
        # 'report/hr_employee_payroll_report_views.xml',

    ],
}
