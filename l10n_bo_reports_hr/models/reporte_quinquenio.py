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
estado_civil = {
    "single": "Soltero(a)",
    "married": "Casado(a)",
    "cohabitant": "Cohabitante legal",
    "widower": "Viudo(a)",
    "divorced": "Divorciado(a)",
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
        index = 1
        data = {
            "extension": "pdf",
            "report": "quinquenio",
            "date_day": self.create_date.day,
            "date_month": meses[self.create_date.month],
            "date_year": self.create_date.year,
            "city": self.employee_id.staff_division_id.display_name,
            "company": self.employee_id.company_id.display_name,
            "company_address": self.employee_id.address_id.contact_address_complete,
            "employee_name": self.employee_id.display_name,
            "employee_age": self.employee_id.afp_age,
            "document_number": self.employee_id.identification_documents.filtered(
                lambda d: d.type_identification_document_id.code == "01"
            ).document_number,
            "document_name": self.employee_id.identification_documents.filtered(
                lambda d: d.type_identification_document_id.code == "01"
            ).type_identification_document_id.display_name,
            "marital": estado_civil[self.employee_id.marital],
            "employee_address": self.employee_id.address_home_id.contact_address_complete,
            "job_title": self.employee_id.job_title,
            "contract_date_start": f"{self.employee_id.contract_id.date_start.day} de {meses[self.employee_id.contract_id.date_start.month]} {self.employee_id.contract_id.date_start.year}",
            "contract_date_end": f"{self.employee_id.contract_id.date_end.day}/{self.employee_id.contract_id.date_end.month}/{self.employee_id.contract_id.date_end.year}",
            "reason_measurement": (
                self.employee_id.contract_id.reason_measurement_id.display_name
                if self.employee_id.contract_id.measurement_staff == "baja"
                else ""
            ),
            "years_of_service": self.employee_id.years_of_service,
            "details": [],
        }
        fechas = [
            self.restar_meses(self.date, 3),
            self.restar_meses(self.date, 2),
            self.restar_meses(self.date, 1),
        ]
        for fecha in fechas:
            planilla = self.employee_id.slip_ids.filtered(
                lambda p: p.date_from.month == fecha.month
                and p.date_from.year == fecha.year
                and p.struct_id.name == "MENSUAL"
            )
            if planilla:
                data["details"].append(
                    {
                        f"month{index}": meses[planilla.date_from.month],
                        f"BASIC{index}": planilla.line_ids.filtered(
                            lambda t: t.code == "BASIC"
                        ).amount,
                        f"BONO_ANT{index}": planilla.line_ids.filtered(
                            lambda t: t.code == "BONO_ANT"
                        ).amount,
                        f"BONO_PROD{index}": planilla.line_ids.filtered(
                            lambda t: t.code == "BONO_PROD"
                        ).amount,
                        f"EXTRAS{index}": planilla.line_ids.filtered(
                            lambda t: t.code == "EXTRAS"
                        ).amount,
                        f"SUBS_FRONTERA{index}": planilla.line_ids.filtered(
                            lambda t: t.code == "SUBS_FRONTERA"
                        ).amount,
                        f"RECARGO{index}": planilla.line_ids.filtered(
                            lambda t: t.code == "RECARGO"
                        ).amount,
                        f"DOMINGO{index}": planilla.line_ids.filtered(
                            lambda t: t.code == "DOMINGO"
                        ).amount
                        + planilla.line_ids.filtered(lambda t: t.code == "DT").amount,
                    }
                )
            index += 1

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
