from odoo import _, fields, models, api
from ..hooks.fetch import useFetch
import base64
import json


class HrReportSip(models.Model):
    _name = "hr.payroll.sip"
    _description = "Reporte de Sistema Integral de Pensiones"

    form_type = fields.Selection(
        [("xlsx", "Excel"), ("csv", "CSV")],
        string="Tipo de Archivo",
        default="xlsx",
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

    def generate_data(self):
        employees = self.get_employee_ids()
        data = {"extension": "pdf", "report": "gestora_sip", "data": []}
        for e in employees:
            detail = {
                "nua_cua": e.employee_id.afp_nua_cua,
            }
            for i in e.employee_id.identification_documents:
                if i.type_identification_document_id.code == "01":
                    detail["document_type"] = "CI"
                    detail["document_number"] = i.document_number
                    detail["document_extension"] = i.document_extension_id.code

            data["data"].append(detail)

        return json.dumps(data)

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
