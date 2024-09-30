from odoo import _, fields, models
from ..hooks.fetch import useFetch
import base64
import json


class HrDisabilityReport(models.Model):
    _name = "hr.payroll.disability"
    _description = "Reporte de incapacidad"

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
        employees_data = []
        data = {
            "extension": self.form_type,
            "report": "incapacidad",
            "data": employees_data,
        }
        for e in employees:
            i_data = {
                "insured_number": e.employee_id.insured_number,
                "lastname": e.employee_id.lastname,
                "lastname2": e.employee_id.lastname2,
                "names": (
                    e.employee_id.firstname
                    if not e.employee_id.firstname2
                    else f"{e.employee_id.firstname} {e.employee_id.firstname2}"
                ),
                "married_name": (
                    e.employee_id.married_name if e.employee_id.married_name else ""
                ),
                "birthday": (
                    ""
                    if not e.employee_id.birthday
                    else f"{e.employee_id.birthday.day}/{e.employee_id.birthday.month}/{e.employee_id.birthday.year}"
                ),
                "date_end": (
                    ""
                    if not e.employee_id.contract_id.date_end
                    else f"{e.employee_id.contract_id.date_end.day}/{e.employee_id.contract_id.date_end.month}/{e.employee_id.contract_id.date_end.year}"
                ),
                "date_start": (
                    ""
                    if not e.employee_id.contract_id.date_start
                    else f"{e.employee_id.contract_id.date_start.day}/{e.employee_id.contract_id.date_start.month}/{e.employee_id.contract_id.date_start.year}"
                ),
                "GROSS": 0,
                "BC_DIARIA": 0,
                "SUB_DIARIO": 0,
                "BMEC_DAYS": 0,
                "BMEC": 0,
                "BM_ACC_LAB_DAY": 0,
                "BM_ACC_LAB": 0,
                "BM_RIESG_EXT_DAY": 0,
                "BM_RIESG_EXT": 0,
            }
            for i in e.line_ids:
                if i.code in i_data.keys():
                    i_data[i.code] = i.total

                # maternidad prenatal
                if i.code == "BM_PRENATAL_DAYS" and i.total > 0:
                    i_data[i.code] = i.total
                elif i.code == "BM_PRENATAL" and i.total > 0:
                    i_data[i.code] = i.total
                    i_data["SUB_DIARIO"] = i_data[i.code] * (i_data["GROSS"] / 30)
                # maternidad postnatal
                elif i.code == "BM_POSTNATAL_DAYS" and i.total > 0:
                    i_data[i.code] = i.total
                elif i.code == "BM_POSTNATAL" and i.total > 0:
                    i_data[i.code] = i.total
                    i_data["SUB_DIARIO"] = i_data[i.code] * (i_data["GROSS"] / 30)
                elif i.code == "BM_ACC_LAB" and i.total > 0:
                    i_data[i.code] = i.total
                    i_data["SUB_DIARIO"] = i_data[i.code] * (i_data["GROSS"] / 30)
            employees_data.append(i_data)

        return json.dumps(data, ensure_ascii=False)

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
