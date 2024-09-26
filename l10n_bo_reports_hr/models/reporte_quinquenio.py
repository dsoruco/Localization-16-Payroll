from odoo import _, fields, models, api
from ..hooks.fetch import useFetch
import base64
import json

meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


class HrQuinquenio(models.Model):
    _inherit = "hr.payslip"

    is_quinquenio = fields.Boolean(compute="_compute_is_quinquenio", default=False)
    report_file = fields.Binary(readonly=True)
    file_name = fields.Char()

    @api.depends("struct_id")
    def _compute_is_quinquenio(self):
        for rec in self:
            if rec.state == "paid" and rec.struct_id.name == "Quinquenal":
                rec.is_quinquenio = True
            else:
                rec.is_quinquenio = False

    def get_data(self):
        employee = self.employee_id
        data = {
            "extension": "pdf",
            "report": "quinquenio",
            "company": employee.company_id.display_name,
            "company_address": employee.address_id.contact_address_complete,
            "employee_name": employee.display_name,
            "employee_age": employee.afp_age,
            "employee_address": employee.address_home_id.contact_address_complete,
            "job_title": employee.job_title,
            "contract_date_start": f"{employee.contract_id.date_start.day} de {meses[employee.contract_id.date_start.month]} {employee.contract_id.date_start.year}",
            "contract_date_end": (
                f"{employee.contract_id.date_end.day} de {meses[employee.contract_id.date_end.month]} {employee.contract_id.date_end.year}"
                if employee.contract_id.date_end
                else ""
            ),
            "reason_measurement": (
                employee.contract_id.reason_measurement_id.display_name
                if employee.contract_id.measurement_staff == "baja"
                else ""
            ),
            "years_of_service":employee.years_of_service,
            
        }
        for i in self.line_ids:
            data[i.code] = i.total

        return json.dumps(data, ensure_ascii=False)

    def action_generate_report(self):
        data = self.get_data()
        resp = useFetch(self.employee_id.company_id.url_report_service, data)
        try:
            self.file_name = self.employee_id.display_name
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
