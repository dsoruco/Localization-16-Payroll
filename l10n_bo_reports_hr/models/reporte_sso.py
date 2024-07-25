from odoo import _, models, fields
from odoo.exceptions import UserError
from ..hooks.fetch import useFetch
import base64
import json


gender = {
    "male":"Masculino",
    "female":"Femenino",
    "other":"Otro"
}
class ReporteFiniquito(models.TransientModel):
    _name = "hr.payroll.reporte.sso"
    _description = "Formulario para reporte de seguro social obligatorio"

    doc_type = fields.Selection(
        [("xlsx", "Excel"), ("csv", "CSV")],
        string="Formato de documento",
        default="xlsx",
    )
    month = fields.Selection(
        [
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        string="Mes",
        default="01",
    )
    year = fields.Char("Año", default="2021")
    file_name = fields.Char("Nombre de archivo")
    report_file = fields.Binary("Archivo de reporte", readonly=True)

    def get_employee_ids(self):
        return self.env["hr.employee"].search([("active", "=", True)])

    def employee_sso_data(self, employee, position=0):

        data = {
            "nro":position,
            "document_type":"",
            "document_value":"",
            "birthday": employee.birthday.strftime("%d/%m/%Y"),
            "date_hire":employee.contract_id.date_start.strftime("%d/%m/%Y"),
            "full_name":employee.display_name,
            "date_fire":employee.contract_id.date_end.strftime("%d/%m/%Y") if employee.contract_id.date_end.strftime("%d/%m/%Y") else "",
            "country_birth":employee.country_of_birth.name,
            "gender":gender[employee.gender],
            "job_title":employee.job_title,
            "paid_hour":"",
            "basic_days":"",
            "paid_days":"",
            "salary":"",
            "extra_time":"",
            "extra_time_amount":"",
            "senior_bonus":"",
            "other_bonuses":"",
            "total_payment":"",
        }

        return json.dumps(data)

    def generate_data(self):
        employee_ids = self.get_employee_ids()
        employee_data = []
        index = 1
        for employee in employee_ids:
            employee_data.append(self.employee_sso_data(employee, position=index))
            index += 1
        return json.dumps({"data": employee_data})

    def action_generate_report(self):
        if not self.doc_type:
            raise UserError("Selecciona el formato de documento")

        company = self.env.user.company_id
        data = self.generate_data()

        resp = useFetch(company.url_report_service, data)
        try:
            self.file_name = "reporte actualizado"
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
