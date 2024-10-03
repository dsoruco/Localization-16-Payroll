from odoo import _,models, fields
from ..hooks.fetch import useFetch
import json
import base64

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
            if (
                pay.date_from.year == int(self.year)
                and pay.date_from.month == int(self.month)
                and pay.payslip_run_id
            ):
                data.append(pay)
        return data

    def get_form608_data(self):
        employee_ids = self.get_employee_ids()
        data = {
            "GROSS":0,
            "TWO_SMN":0,
            "BASE_IMPONIBLE":0,
            "IMPUESTO":0,
            "TAX_2_SMN":0,
            "IMP_NETO_RC_IVA":0,
            "IVA_FORM_110":0,
            "SALDO_A_FAVOR_FISCO":0,
            "SALDO_A_FAVOR_DEPEND":0,
            "SALDO_A_FAVOR_MES_ANT":0,
            "CURRENT_UFV":0,
            "SAL_ANT_ACT":0,
            "SALDO_UTILIZADO":0,
            "IMP_RET_PAGAR":0,
            "SAL_PROX_MES":0,
            "TOTAL_DEPEN":len(employee_ids),
            "TOTAL_FORM110":len(employee_ids),
        }
        # Datos extraibles
        for employee in employee_ids:
            for item in employee.line_ids:
                if item.code in data.keys():
                    data[item.code] += item.amount

        return data

    def get_rpi_data(self, index, employee):
        data = {
            "nro": index,
            "year": int(self.year),
            "month": int(self.month),
            "tax_code": "" if not employee.employee_id.afp_nua_cua else str(employee.employee_id.afp_nua_cua),
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
            "employee_status": "V" if employee.contract_id.active else "D",
            "GROSS":0,
            "NETO_IMPONIBLE":0,
            "TWO_SMN":0,
            "BASE_IMPONIBLE":0,
            "IMPUESTO":0,
            "TAX_2_SMN":0,
            "IMP_NETO_RC_IVA":0,
            "IVA_FORM_110":0,
            "SALDO_A_FAVOR_FISCO":0,
            "SALDO_A_FAVOR_DEPEND":0,
            "SALDO_A_FAVOR_MES_ANT":0,
            "LAST_UFV":0,
            "SAL_ANT_ACT":0,
            "SALDO_UTILIZADO":0,
            "IMP_RET_PAGAR":0,
            "SAL_PROX_MES":0,
        }
        if employee.employee_id.identification_documents:
            for document in employee.employee_id.identification_documents:
                if document.type_identification_document_id.code == "01":
                    data["document_value"] = document.document_number
                    data["document_type"] = "CI"
                if document.type_identification_document_id.code == "03":
                    data["tax_code"] = document.document_number

        for item in employee.line_ids:
            if item.code in data.keys():
                data[item.code] = item.amount

        return data

    def generate_data(self):
        employee_ids = self.get_employee_ids()
        index = 1
        if self.form_type == "planilla":
            employee_data=[]
            for employee in employee_ids:
                employee_data.append(self.get_rpi_data(index, employee))
                index += 1
        elif self.form_type == "form608":
            employee_data = self.get_form608_data()

        return json.dumps(
            {
                "report": f"rpi_{self.form_type}",
                "extension": "csv",
                "data": employee_data,
            }
        )

    def action_generate_report(self):
        data = self.generate_data()
        resp = useFetch(self.env.company.url_report_service, data)
        try:
            self.file_name = f"PLA_{self.env.company.vat}_{self.year}_{self.month}.csv"
            file = base64.b64decode(resp["data"]["document"])
            self.report_file = base64.b64encode(file).decode("utf-8")
            return {
                "type": "ir.actions.act_url",
                "url": f"/web/content?model={self._name}&id={self.id}&field=report_file&filename_field=file_name&download=true",
                "target": "new",
            }
        except:
            notification = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Advertencia"),
                    "type": "warning",
                    "message": "Error al realizar petición, por favor intenta de nuevo!",
                    "sticky": True,
                },
            }
            return notification