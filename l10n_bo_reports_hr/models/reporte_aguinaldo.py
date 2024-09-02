from odoo import _, models, fields, api
from odoo.exceptions import UserError
import requests
import logging
import json
import base64

_logger = logging.getLogger(__name__)


class HrPayrollAguinaldoWizard(models.TransientModel):
    _name = "hr.payroll.aguinaldo.wizard"

    name = fields.Char("Nombre", default="Reporte aguinaldo")
    doc_type = fields.Selection([("xlsx", "Excel"), ("csv", "CSV")])
    month = fields.Selection(
        [
            ("01", "Enero"), ("02", "Febrero"), ("03", "Marzo"),
            ("04", "Abril"), ("05", "Mayo"), ("06", "Junio"),
            ("07", "Julio"), ("08", "Agosto"), ("09", "Septiembre"),
            ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre"),
        ],
        string="Mes", default="01"
    )
    year = fields.Char("Año", default=lambda self: str(
        fields.Date.today().year))

    @api.onchange("month", "year")
    def _onchange_month_year(self):
        if self.year and self.month:
            self.name = f"Reporte aguinaldo {self.month}/{self.year}"

    @api.onchange("year")
    def _onchange_year(self):
        if self.year and not self.year.isdigit():
            raise UserError(_("El año debe ser un número"))

    def action_generate_aguinaldo(self):
        data = self.generate_data()
        url = f"{self.env.user.company_id.url_report_service}/process"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            try:
                json_response = response.json()
                base64_doc = json_response.get(
                    'data', {}).get('document', None)

                if not base64_doc:
                    raise UserError(
                        _("El documento no se generó correctamente."))

                # Crear un attachment en Odoo
                file_name = f"Reporte_Aguinaldo_{self.month}_{self.year}.{self.doc_type or 'xlsx'}"
                attachment = self.env['ir.attachment'].create({
                    'name': file_name,
                    'type': 'binary',
                    'datas': base64_doc,
                    'store_fname': file_name,
                    'res_model': 'ir.ui.view',
                    'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if self.doc_type == 'xlsx' else 'text/csv',
                })

                # Devolver la URL de descarga
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}?download=true',
                    'target': 'self',
                }

            except (ValueError, KeyError) as e:
                raise UserError(
                    _("Error procesando la respuesta del servicio: %s") % str(e))
        else:
            raise UserError(
                _("Error al generar el reporte aguinaldo: %s") % response.text)

    def generate_data(self):
        employee_ids = self.get_employee_ids()
        employee_data = [self.employee_aguinaldo_data(
            employee, position=index) for index, employee in enumerate(employee_ids, start=1)]
        _logger.info("Se generaron datos para %d empleados",
                     len(employee_data))
        return json.dumps({
            "extension": self.doc_type or 'xlsx',
            "report": "aguinaldo",
            "data": employee_data
        })

    def get_employee_ids(self):
        return self.env["hr.employee"].search([])

    def employee_aguinaldo_data(self, employee, position=0):
        def calcular_promedio_concepto(concept_code):
            payslip_lines = self.env['hr.payslip.line'].search([
                ('employee_id', '=', employee.id),
                ('code', '=', concept_code),
                ('slip_id.date_from', '>=', f'{self.year}-09-01'),
                ('slip_id.date_to', '<=', f'{self.year}-11-30')
            ])
            total = sum(line.total for line in payslip_lines)
            count = len(payslip_lines)
            return total / count if count > 0 else 0.0

        def parse_to_int(value, default=0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        data = {
            "cod_sucursal": position,
            "nro": employee.id,
            "tipo_documento": "CI" if employee.identification_id else "Pasaporte",
            "numero_documento": employee.identification_id or employee.passport_id or "",
            "lugar_expedicion": employee.country_of_birth.code if employee.country_of_birth else "",
            "fecha_nacimiento": employee.birthday.strftime('%d/%m/%Y') if employee.birthday else "",
            "apellido_paterno": employee.lastname or "",
            "apellido_materno": employee.lastname2 or "",
            "nombres": employee.firstname or "",
            "pais_nacionalidad": employee.company_country_id.name if employee.company_country_id else employee.country_id.name if employee.country_id else "",
            "sexo": 'M' if employee.gender == 'male' else 'F' if employee.gender == 'female' else "",
            "jubilado": 1 if employee.afp_retired else 0,
            "aporta_afp": 1 if employee.afp_id else 0,
            "persona_con_discapacidad": 1 if employee.has_disability else 0,
            "tutor_persona_discapacidad": 1 if employee.disability_tutor else 0,
            "fecha_ingreso": employee.date_hired.strftime('%d/%m/%Y') if employee.date_hired else "",
            "fecha_retiro": employee.departure_date.strftime('%d/%m/%Y') if employee.departure_date else "",
            "motivo_retiro": employee.departure_reason_id.name if employee.departure_reason_id else "",
            "caja_salud": employee.health_box_id.name if employee.health_box_id else "",
            "afp": parse_to_int(employee.afp_id.id, 0),
            "nua_cua": employee.afp_nua_cua or "",
            "sucursal_ubicacion_adicional": parse_to_int(employee.staffing_subdivision_id.id, 0),
            "clasificacion_laboral": parse_to_int(employee.laboral_clasication, 0),
            "cargo": employee.job_id.name if employee.job_id else "",
            "modalidad_contrato": 1,  # Valor predeterminado
            "promedio_haber_basico": calcular_promedio_concepto('BASIC'),
            "promedio_bono_antiguedad": calcular_promedio_concepto('BONO_ANTIG'),
            "promedio_bono_produccion": calcular_promedio_concepto('BONO_PROD'),
            "promedio_subsidio_frontera": calcular_promedio_concepto('SUB_FRONTERA'),
            "promedio_trabajo_extraordinario_nocturno": calcular_promedio_concepto('EXTRA_NOCTURNO'),
            "promedio_pago_dominical_trabajado": calcular_promedio_concepto('PAGO_DOMINICAL'),
            "promedio_otros_bonos": calcular_promedio_concepto('OTROS_BONOS'),
            "promedio_total_ganado": calcular_promedio_concepto('TOTAL_GANADO'),
            "meses_trabajados": employee.years_of_service or 0,
            "total_ganado_despues_duodecimas": 0.0,
        }

        _logger.info("Datos generados para el empleado %s: %s",
                     employee.name, json.dumps(data, indent=4, ensure_ascii=False))
        return data
