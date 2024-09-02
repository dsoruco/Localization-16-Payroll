from odoo import _, models, fields, api
from odoo.exceptions import UserError
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_retired = fields.Boolean(
        "Retirado", compute="_compute_is_retired", store=False)
    has_disability = fields.Boolean(
        "Discapacidad",
        help="Indica si el empleado tiene alguna discapacidad",
        default=False,
    )
    disability_tutor = fields.Boolean(
        "Tutor de discapacidad",
        help="Indica si el empleado es tutor de una persona con discapacidad",
        default=False,
    )
    laboral_clasication = fields.Selection(
        [
            ("1", "Ocupaciones de dirección en la administración pública y empresas."),
            ("2", "Ocupaciones de profesionales científicos e intelectuales."),
            ("3", "Ocupaciones de técnicos y profesionales de apoyo."),
            ("4", "Empleados de oficina."),
            ("5", "Trabajadores de los servicios y vendedores del comercio."),
            ("6", "Productores y trabajadores en la agricultura, pecuaria, agropecuaria y pesca."),
            ("7", "Trabajadores de la industria extractiva, construcción, industria manufacturera y otros oficios."),
            ("8", "Operadores de instalaciones y maquinarias."),
            ("9", "Trabajadores no calificados."),
            ("10", "Fuerzas armadas."),
        ],
        string="Clasificación Laboral",
    )

    def _compute_is_retired(self):
        for employee in self:
            employee.is_retired = employee.contract_id.state == "close"

    def compute_extra_hours_total_time(self, date_from, date_to):
        self.ensure_one()
        payroll_time_model = self.env['hr.payroll.overtime.hours.list']
        overtime_hours = payroll_time_model.search([
            ('employee_id', '=', self.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ])
        return overtime_hours


class HrPayrollAguinaldoWizard(models.TransientModel):
    _name = "hr.payroll.aguinaldo.wizard"

    name = fields.Char("Nombre", default="Reporte aguinaldo")
    doc_type = fields.Selection(
        [("xlsx", "Excel"), ("csv", "CSV")]
    )
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
                attachment = self.env['ir.attachment'].create({
                    'name': f"Reporte Aguinaldo {self.month}/{self.year}",
                    'type': 'binary',
                    'datas': base64_doc,
                    'store_fname': f"Reporte Aguinaldo {self.month}/{self.year}.csv",
                    'res_model': 'hr.payroll.aguinaldo.wizard',
                    'res_id': self.id,
                })
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
        employee_data = []
        for index, employee in enumerate(employee_ids, start=1):
            employee_data.append(
                self.employee_aguinaldo_data(employee, position=index))
        _logger.info("Se generaron datos para %d empleados",
                     len(employee_data))
        return json.dumps({
            "extension": 'csv',
            "report": "aguinaldo",
            "data": employee_data
        })

    def get_employee_ids(self):
        return self.env["hr.employee"].search([])

    def _bool_to_number(self, value):
        return 1 if value else 0

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

        data = {
            "cod_sucursal": position,
            "nro": employee.id,
            "tipo_documento": "CI" if employee.identification_id else "Pasaporte",
            "numero_documento": employee.identification_id or employee.passport_id or "",
            "lugar_expedicion": employee.country_of_birth.code if employee.country_of_birth else "",
            "fecha_nacimiento": employee.birthday.strftime('%d/%m/%Y') if employee.birthday else "",
            "apellido_paterno": employee.lastname or "",
            "apellido_materno": employee.lastname2 or "",
            # Campo adicional para apellido de casada
            "apellido_casada": employee.married_name or "",
            "nombres": employee.firstname or "",
            "otro_nombre": employee.firstname2 or "",  # Campo adicional para otro nombre
            "pais_nacionalidad": employee.company_country_id.name if employee.company_country_id else employee.country_id.name if employee.country_id else "",
            "sexo": 'M' if employee.gender == 'male' else 'F' if employee.gender == 'female' else "",
            "jubilado": 1 if employee.afp_retired else 0,
            "afp": employee.afp_id.afp_code if employee.afp_id else "",
            "numero_afiliado": employee.afp_nua_cua or "",
            "clasificacion_laboral": employee.laboral_clasication or "",
            "cargo": employee.job_id.name if employee.job_id else "",
            "fecha_ingreso": employee.date_hired.strftime('%d/%m/%Y') if employee.date_hired else "",
            "modalidad_contrato": employee.contract_id.contract_type or "",
            "fecha_retiro": employee.departure_date.strftime('%d/%m/%Y') if employee.departure_date else "",
            "promedio_haber_basico": calcular_promedio_concepto('BASIC'),
            "promedio_bono_antiguedad": calcular_promedio_concepto('BONO_ANTIG'),
            "promedio_bono_produccion": calcular_promedio_concepto('BONO_PROD'),
            "promedio_subsidio_frontera": calcular_promedio_concepto('SUB_FRONTERA'),
            "promedio_trabajo_extraordinario_nocturno": calcular_promedio_concepto('EXTRA_NOCTURNO'),
            "promedio_pago_dominical_trabajado": calcular_promedio_concepto('PAGO_DOMINICAL'),
            "promedio_otros_bonos": calcular_promedio_concepto('OTROS_BONOS'),
            "promedio_total_ganado": calcular_promedio_concepto('TOTAL_GANADO'),
            "meses_trabajados": employee.years_of_service or "",
            "total_ganado_despues_duodecimas": "",  # Requiere cálculo adicional
            "ubicacion": employee.work_location_id.name if employee.work_location_id else "",
        }

        _logger.info("Datos generados para el empleado %s: %s",
                     employee.name, json.dumps(data, indent=4, ensure_ascii=False))
        return data
