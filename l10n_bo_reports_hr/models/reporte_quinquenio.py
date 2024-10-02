from odoo import _, fields, models, api
from ..hooks.fetch import useFetch
import base64
import json
import datetime
import calendar

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

    def restar_meses(self, fecha_inicial, meses_a_restar):
        """Resta un número específico de meses a una fecha dada.

        Args:
            fecha_inicial: Un objeto datetime.datetime representando la fecha inicial.
            meses_a_restar: Un entero representando el número de meses a restar.

        Returns:
            Un nuevo objeto datetime.datetime con los meses restados.
        """

        dias_a_restar = 0
        fecha_actual = fecha_inicial
        for _ in range(meses_a_restar):
            dias_a_restar += calendar.monthrange(fecha_actual.year, fecha_actual.month)[
                1
            ]
            fecha_actual -= datetime.timedelta(
                days=1
            )  # Avanzamos un día para el siguiente mes

        fecha_final = fecha_inicial - datetime.timedelta(days=dias_a_restar)
        return fecha_final

    def get_data(self):

        data = {
            "extension": "pdf",
            "report": "quinquenio",
            "company": self.employee_id.company_id.display_name,
            "company_address": self.employee_id.address_id.contact_address_complete,
            "employee_name": self.employee_id.display_name,
            "employee_age": self.employee_id.afp_age,
            "employee_address": self.employee_id.address_home_id.contact_address_complete,
            "job_title": self.employee_id.job_title,
            "contract_date_start": f"{self.employee_id.contract_id.date_start.day} de {meses[self.employee_id.contract_id.date_start.month]} {self.employee_id.contract_id.date_start.year}",
            "contract_date_end": (
                f"{self.employee_id.contract_id.date_end.day} de {meses[self.employee_id.contract_id.date_end.month]} {self.employee_id.contract_id.date_end.year}"
                if self.employee_id.contract_id.date_end
                else ""
            ),
            "reason_measurement": (
                self.employee_id.contract_id.reason_measurement_id.display_name
                if self.employee_id.contract_id.measurement_staff == "baja"
                else ""
            ),
            "years_of_service": self.employee_id.years_of_service,
            "details": [],
        }
        fechas = [
            self.restar_meses(self.date, 2),
            self.restar_meses(self.date, 1),
            self.date,
        ]
        for fecha in fechas:
            planilla = self.employee_id.slip_ids.filtered(
                lambda p: p.date_from.month == fecha.month
                and p.date_from.year == fecha.year
                and p.struct_id.name == "MENSUAL"
            )
            if planilla:
                data["details"].append({
                    "month":meses[planilla.date_from.month],
                    "basic_wage":planilla.basic_wage,
                    "extras": planilla.line_ids.filtered(lambda t: t.code == "EXTRAS").amount
                })

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
