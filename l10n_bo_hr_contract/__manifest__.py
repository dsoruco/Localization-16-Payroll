{
    'name': "Datec: Nómina Bolivia",
    'version': '16.0.0.0.2',
    'depends': ['l10n_bo_hr', 'hr_contract'],
    'author': "Datec",
    'license': 'OPL-1',
    'category': 'Payroll Localization',
    'description': """
    Bolivia Payroll Localization
    """,
    'data': [
        'data/hr_contract_reason_measurement.xml',
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'views/contract_reason_measurement_view.xml',
        'views/bi_organizational_structure_reports_view.xml',
        # 'report/hr_employee_payroll_report_views.xml',

    ],
}
