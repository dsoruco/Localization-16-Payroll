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

    def get_salary(self):
        basic_salary = self.env["hr.rule.parameter.value"].search(
            [("code", "=", "SMN")]
        )
        for record in basic_salary:
            if record.date_from.year == int(self.year):
                basic_salary = int(record.parameter_value)
        return basic_salary

    def get_rpi_data(self, index, employee):
        basic_salary = self.get_salary()
        basic_tax = basic_salary / 13
        data = {
            "nro": index,
            "year": self.year,
            "month": self.month,
            "tax_code": "",
            "name": (
                f"{employee.employee_id.firstname} {employee.employee_id.firstname2}"
                if employee.employee_id.firstname2
                else employee.employee_id.firstname
            ),
            "last_name1": (
                employee.employee_id.lastname if employee.employee_id.lastname else ""
            ),
            "last_name2": (
                employee.employee_id.lastname2 if employee.employee_id.lastname2 else ""
            ),
            "document_value": "",
            "document_type": "",
            "employee_status": employee.contract_id.active,
            "contract_wage": employee.contract_id.contract_wage,
            "salary_afp": round(
                employee.contract_id.contract_wage
                - (employee.contract_id.contract_wage / 12.71),
                2,
            ),
            "tax_base": (
                basic_salary * 2
                if employee.contract_id.contract_wage > basic_salary * 2
                else employee.contract_id.contract_wage
            ),
            "taxable_amount": "13",
            "rc_iva": "14",
            "tax_2smn": "15",
            "net_tax": "16",
            "f110": "17",
            "tax_to_pay": "18",
            "dependent_balance": "19",
            "last_dependent_balance": "20",
            "last_ufv_dependent_balance": "21",
            "updated_dependent_balance": "22",
            "balance_used": "23",
            "withheld_tax": "24",
            "updated_balance_credit": "25",
        }
        if employee.employee_id.identification_documents:
            for document in employee.employee_id.identification_documents:
                if document.type_identification_document_id.code == "01":
                    data["document_value"] = document.document_number
                    data["document_type"] = "CI"
            for document in employee.employee_id.identification_documents:
                if document.type_identification_document_id.code == "03":
                    data["tax_code"] = document.document_number
        if employee.contract_id.contract_wage > basic_salary * 2:
            data["taxable_amount"] = (
                employee.contract_id.contract_wage - basic_salary * 2
            )
        data["rc_iva"] = round(data["taxable_amount"] / 13, 2)
        data["tax_2smn"] = round(
            (basic_tax * 2 if data["rc_iva"] < basic_tax * 2 else data["rc_iva"]), 2
        )
        data["net_tax"]= round(data["rc_iva"] - basic_tax*2,2) if data["rc_iva"] > basic_tax*2 else 0
        #TODO: HACER DEL PUNTO 17 EN ADELANTE
        
        return data

    def generate_data(self):
        employee_ids = self.get_employee_ids()
        index = 1
        employee_data = []

        for employee in employee_ids:
            employee_data.append(self.get_rpi_data(index, employee))
            index += 1
        return json.dumps(
            {
                "report": f"rpi_{self.form_type}",
                "extension": "csv",
                "data": employee_data,
            }
        )

    def action_generate_report(self):
        data = self.generate_data()
        self.file_name = f"PLA_NIT_{self.year}_{self.month}"
        return True
