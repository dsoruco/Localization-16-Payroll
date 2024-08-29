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
            (
                "6",
                "Productores y trabajadores en la agricultura, pecuaria, agropecuaria y pesca.",
            ),
            (
                "7",
                "Trabajadores de la industria extractiva, construcción, industria manufacturera y otros oficios.",
            ),
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
        # Assuming you want to return something, otherwise, this function needs a clearer purpose
        return overtime_hours  # Adjust based on actual requirements


class HrPayrollAguinaldoWizard(models.TransientModel):
    _name = "hr.payroll.aguinaldo.wizard"

    name = fields.Char("Nombre", default="Reporte aguinaldo")
    doc_type = fields.Selection(
        [
            ("xlsx", "Excel"),
            ("csv", "CSV"),
        ]
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
        return json.dumps({
            "extension": 'csv',
            "report": "aguinaldo",
            "data": employee_data
        })

    def get_employee_ids(self):
        return self.env["hr.employee"].search([("active", "=", True)])

    def _bool_to_number(self, value):
        return 1 if value else 0

    def employee_aguinaldo_data(self, employee, position=0):
        data = {
            "cod_sucursal": position,
            "nro": employee.id,
            "tipo_documento": "CI",  # Si necesitas asignar un tipo de documento específico
            "numero_documento": employee.identification_id or employee.passport_id or "",
            "lugar_expedicion": employee.country_of_birth.id if employee.country_of_birth else "",
            "fecha_nacimiento": employee.birthday,
            "apellido_paterno": employee.lastname,
            "apellido_materno": employee.lastname2,
            "nombres": employee.firstname,
            "pais_nacionalidad": employee.company_country_id.id if employee.company_country_id else employee.country_id.id if employee.country_id else "",
            "sexo": employee.gender,
            "jubilado": employee.afp_retired,
            "aporta_afp": employee.afp_id.id if employee.afp_id else "",
            "persona_con_discapacidad": employee.has_disability,
            "tutor_persona_discapacidad": employee.disability_tutor,
            "fecha_ingreso": employee.date_hired,
            "fecha_retiro": employee.departure_date,
            "motivo_retiro": employee.departure_reason_id.id if employee.departure_reason_id else "",
            "caja_salud": employee.health_box_id.id if employee.health_box_id else "",
            "afp_aporta": employee.afp_id.id if employee.afp_id else "",
            "nua_cua": employee.afp_nua_cua or "",
            "sucursal_ubicacion_adicional": employee.staffing_subdivision_id.id if employee.staffing_subdivision_id else "",
            "clasificacion_laboral": employee.laboral_clasication or "",
            "cargo": employee.job_id.id if employee.job_id else "",
            "modalidad_contrato": employee.contract_id.id if employee.contract_id else "",
            "promedio_haber_basico": "",  # Requiere cálculo o dato adicional
            "promedio_bono_antiguedad": "",  # Requiere cálculo o dato adicional
            "promedio_bono_produccion": "",  # Requiere cálculo o dato adicional
            "promedio_subsidio_frontera": employee.frontier_subsidy or "",
            # Requiere cálculo o dato adicional
            "promedio_trabajo_extraordinario_nocturno": "",
            "promedio_pago_dominical_trabajado": "",  # Requiere cálculo o dato adicional
            "promedio_otros_bonos": "",  # Requiere cálculo o dato adicional
            "promedio_total_ganado": "",  # Requiere cálculo o dato adicional
            "meses_trabajados": employee.years_of_service or "",
            "total_ganado_despues_duodecimas": "",  # Requiere cálculo o dato adicional
        }

        # Aquí se agrega el log para ver el resultado
        _logger.info("Datos generados para el empleado %s: %s",
                     employee.name, json.dumps(data, indent=4, ensure_ascii=False))

        return data
