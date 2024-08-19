from odoo import models, fields
import json


class HrPayrollRpi(models.Model):
    _name = "hr.payroll.rpi"
    _description = "Reporte de Planilla Impositiva"

    form_type = fields.Selection(
        [("planilla", "Planilla Impositiva"), ("form608", "Formulario 608")],
        string="Tipo de Reporte",
        default="planilla",
    )
    month = fields.Selection(
        [
            ("1", "Enero"),
            ("2", "Febrero"),
            ("3", "Marzo"),
            ("4", "Abril"),
            ("5", "Mayo"),
            ("6", "Junio"),
            ("7", "Julio"),
            ("8", "Agosto"),
            ("9", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        string="Mes",
        default="4",
    )
    year = fields.Char("Año", default="2023")
    report_file = fields.Binary("Archivo de reporte", readonly=True)
    file_name = fields.Char("Nombre de archivo")

    def get_employee_ids(self):
        employees = self.env["hr.payslip"].search([("state", "=", "paid")])
        data = []
        for pay in employees:
            if pay.date_from.year == int(self.year) and pay.date_from.month == int(
                self.month
            ):
                data.append(pay)
        return data

    def get_rpi_data(self, index, employee):
        data = {
            "nro": index,
            "year": self.year,
            "month": self.month,
            "tax_code":"",
            "name":"",
            "last_name1":"",
            "last_name2":"",
            "document_value":"",
            "document_type":"",
            "employee_status":"",
            "contract_wage":employee.contract_id.contract_wage,
            "tax_free":"",
            "tax_base":"",
            "tax_iva":"",
            "tax_2smn":"",
            "net_tax":"",
            "f110":"",
            "tax_to_pay":"",
            "dependent_balance":"",
            "last_dependent_balance":"20",
            "last_ufv_dependent_balance":"",
            "updated_dependent_balance":"",
            "balance_used":"",
            "withheld_tax":"",
            "updated_balance_credit":""
            
        }
        return data

    def generate_data(self):
        employee_ids = self.get_employee_ids()
        index = 1
        employee_data = []

        for employee in employee_ids:
            employee_data.append(self.get_rpi_data(index, employee))
            index += 1
        return json.dumps(
            {"report": f'rpi_{self.form_type}', "extension": "csv", "data": employee_data}
        )

    def action_generate_report(self):
        data = self.generate_data()
        self.file_name = f"PLA_NIT_{self.year}_{self.month}"
        return True
