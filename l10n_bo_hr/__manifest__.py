{
    'name': "Datec: Nómina Bolivia empleado",
    'version': '16.0.0.0.2',
    'depends': ['hr_bo_employee_lastnames'],
    'author': "Datec",
    'license': 'OPL-1',
    'category': 'Payroll Localization',
    'description': """
    Bolivia Payroll Localization
    """,
    'data': [
        'data/res_partner_afp.xml',
        'data/res_partner_health_box.xml',
        'data/afp_quotation_type.xml',
        'data/afp_quotation_type_details.xml',
        'security/ir.model.access.csv',
        'views/hr_job_views.xml',
        'views/hr_employee_view.xml',
        'views/hr_staff_division_view.xml',
        'views/hr_staffing_subdivision_view.xml',
        'views/hr_payroll_area_view.xml',
        'views/hr_personnel_group_view.xml',
        'views/hr_personnel_area_view.xml',
        'views/res_partner_view.xml',
        'views/hr_afp_quotation_type_view.xml',
        # 'report/hr_employee_payroll_report_views.xml',

    ],
}
