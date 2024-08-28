# -*- coding: utf-8 -*-
{
    'name': "l10n_bo_reports_hr",
    'summary': "Modulo para generar reportes legales",
    'author': 'Datec LTDA - AMS',
    'website': "https://datec.com.bo",
    'category': 'Línea base Bolivia/Human Resources/Payroll',
    'version': '1.2',
    'depends': ['base','hr','l10n_bo_hr','l10n_bo_hr_holidays','l10n_bo_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/finiquito.xml',
        'views/sso.xml',
        'views/reportes.xml',
        'views/planilla_impositiva.xml',
        'views/reportes_menu.xml',
    ],
    'images':['static/description/icon.svg'],
}
