from odoo import _, models, fields, api
from odoo.exceptions import UserError
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_retired = fields.Boolean(
        "Retirado", 
        compute="_compute_is_retired", 
        store=False
    )
    has_disability = fields.Boolean(
        "Discapacidad",
        help="Indica si el empleado tiene alguna discapacidad",
        default=False
    )
    disability_tutor = fields.Boolean(
        "Tutor de discapacidad", 
        help="Indica si el empleado es tutor de una persona con discapacidad",
        default=False
    )
    laboral_clasication = fields.Selection([
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
    ], string="Clasificación Laboral")

    def _compute_is_retired(self):
        for employee in self:
            employee.is_retired = employee.contract_id.state == 'close'
            

# class HrContract(models.Model):
#     _inherit = "hr.contract"
#
#     contract_format = fields.Selection([
#         ("1", "Escrito"),
#         ("2", "Verbal"),
#     ], string="Formato de contrato", default="1")
#     worked_days = fields.Integer("Dias pagados", default=30)
#     worked_hours = fields.Integer("Horas pagadas", default=240)

class HrPayrollMintraWizard(models.TransientModel):
    _name = "hr.payroll.mintra.wizard"

    name = fields.Char("Nombre", default="Reporte mintra")
    doc_type = fields.Selection([
        ("pdf", "PDF"),
        ("csv", "CSV"),
    ])
    month = fields.Selection([
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
    ], string="Mes", default="01")
    year = fields.Char("Año", default="2021")

    
    @api.onchange("month", "year")
    def _onchange_month_year(self):
        if self.year and self.month:
            self.name = f"Reporte mintra {self.month}/{self.year}"

    
    @api.model
    def _onchange_year(self):
        if not self.year.isdigit():
            raise UserError(_("El año debe ser un número"))


    def action_generate_mintra(self):
        data = self.generate_data()
        url = f"{self.env.user.company_id.url_report_service}/api/v1/mintra"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            # Return the file
            return {
                "name": "Reporte Mintra",
                "type": "ir.actions.act_url",
                "url": f"{url}/{self.year}/{self.month}",
                "target": "new",
            }
        else:
            raise UserError(_("Error al generar el reporte mintra"))


    def generate_data(self):
        employee_ids = self.get_employee_ids()
        employee_data = []
        index = 1
        for employee in employee_ids:
            employee_data.append(self.employee_mintra_data(employee, position=index))
            index += 1
        return json.dumps({
            "data": employee_data
        })
        
    
    def get_employee_ids(self):
        return self.env["hr.employee"].search([('active', '=', True)])

    
    def employee_mintra_data(self, employee, position=0):
        employee_data = {
            "code": position,
            "document_type": employee.address_id.l10n_bo_document_type,
            "document_number": employee.address_id.vat,
            "expedition_city": employee.address_id.l10n_bo_document_city_id.name,
            "date_of_birth": employee.birthday.strftime("%d/%m/%Y") if employee.birthday else "",
            "last_name": employee.lastname,
            "mother_last_name": employee.lastname2,
            "first_name": f"{employee.firstname} {employee.firstname2}".strip(),
            "nationality": employee.country_id.name,
            "gender": employee.gender,
            "retired": employee.is_retired,
            "contributes_to_afp": employee.afp_id.name if employee.afp_id else "",
            "disabled": employee.has_disability,
            "disability_tutor": employee.disability_tutor,
            "date_of_entry": employee.date_hired.strftime("%d/%m/%Y") if employee.date_hired else "",
            "date_of_exit": employee.contract_id.date_end.strftime("%d/%m/%Y") if employee.contract_id.date_end else "",
            "reason_for_exit": employee.contract_id.notes,
            "health_box": employee.health_box_id.name,
            "afp_contributing": employee.afp_code,
            "membership_number": employee.afp_nua_cua,
            "branch_number": employee.company_id.id,
            "laboral_clasication": employee.laboral_clasication or "",
            "job_name": employee.job_id.name,
            "contract_type": employee.contract_id.contract_type_id.name,
            "contract_type_format": employee.contract_id.contract_format,
            "payed_days": employee.contract_id.worked_days,
            "payed_hours": employee.contract_id.worked_hours,
            "salary": employee.contract_id.wage,
            "antiquity_bonus": employee.seniority_bonus_total,
            "extra_hours_total_time": 0, # Preguntar como calcular las horas extras
            "extra_hours_total_amount": 0, # Preguntar como calcular las horas extras
            "extra_hours_night_time": 0, # Preguntar como calcular las horas extras
            "extra_hours_dominical_time": 0, # Preguntar como calcular las horas extras
            "extra_hours_dominical_amount": 0, # Preguntar como calcular las horas extras
            "worked_sunday_total": 0, # Preguntar como calcular los domingos trabajados
            "worked_sunday_amount": 0, # Preguntar como calcular los domingos trabajados
            "worked_sundsay_salary": 0, # Preguntar como calcular los domingos trabajados
            "productive_bonus": 0, # Preguntar como calcular el bono productivo
            "frontier_bonus": 0, # Preguntar como calcular el bono fronterizo
            "other_bonuses": 0, # Preguntar como calcular otros bonos
            "tax_discount": 0, # Preguntar como calcular los descuentos RC-IVA
            "health_box_discount": 0, # Preguntar como calcular los descuentos de la caja de salud
            "other_discounts": 0, # Preguntar como calcular otros descuentos
        }
        return employee_data


# class HrPayrollMintra(models.Model):
#     _name = "hr.payroll.mintra"

#     doc_type = fields.Selection(
#         [
#             ("pdf", "PDF"),
#             ("csv", "CSV"),
#         ],
#         string="Formato de Documento", default="pdf"
#     )
#     report_file = fields.Binary("Archivo de reporte", readonly=True)
#     file_name = fields.Char("Nombre de archivo")


#     def get_employee_ids(self):
#         return self.env["hr.employee"].search([('active', '=', True)])

#     # self.env["hr.payroll.mintra"].browse(1).generate_data()
#     # All dates are dd/mm/yyyy


#     def employee_mintra_data(self, employee, position=0):
#         employee_data = {
#             "code": position,
#             "document_type": employee.address_id.l10n_bo_document_type,
#             "document_number": employee.address_id.vat,
#             "expedition_city": employee.address_id.l10n_bo_document_city_id.name,
#             "date_of_birth": employee.birthday.strftime("%d/%m/%Y") if employee.birthday else "",
#             "last_name": employee.lastname,
#             "mother_last_name": employee.lastname2,
#             "first_name": f"{employee.firstname} {employee.firstname2}".strip(),
#             "nationality": employee.country_id.name,
#             "gender": employee.gender,
#             "retired": employee.is_retired,
#             "contributes_to_afp": employee.afp_id.name if employee.afp_id else "",
#             "disabled": employee.has_disability,
#             "disability_tutor": employee.disability_tutor,
#             "date_of_entry": employee.date_hired.strftime("%d/%m/%Y") if employee.date_hired else "",
#             "date_of_exit": employee.contract_id.date_end.strftime("%d/%m/%Y") if employee.contract_id.date_end else "",
#             "reason_for_exit": employee.contract_id.notes,
#             "health_box": employee.health_box_id.name,
#             "afp_contributing": employee.afp_code,
#             "membership_number": employee.afp_nua_cua,
#             "branch_number": employee.company_id.id,
#             "laboral_clasication": employee.laboral_clasication or "",
#             "job_name": employee.job_id.name,
#             "contract_type": employee.contract_id.contract_type_id.name,
#             "contract_type_format": employee.contract_id.contract_format,
#             "payed_days": employee.contract_id.worked_days,
#             "payed_hours": employee.contract_id.worked_hours,
#             "salary": employee.contract_id.wage,
#             "antiquity_bonus": "", # Preguntar como calcular el bono de antiguedad
#             "extra_hours_total_time": 0, # Preguntar como calcular las horas extras
#             "extra_hours_total_amount": 0, # Preguntar como calcular las horas extras
#             "extra_hours_night_time": 0, # Preguntar como calcular las horas extras
#             "extra_hours_dominical_time": 0, # Preguntar como calcular las horas extras
#             "extra_hours_dominical_amount": 0, # Preguntar como calcular las horas extras
#             "worked_sunday_total": 0, # Preguntar como calcular los domingos trabajados
#             "worked_sunday_amount": 0, # Preguntar como calcular los domingos trabajados
#             "worked_sundsay_salary": 0, # Preguntar como calcular los domingos trabajados
#             "productive_bonus": 0, # Preguntar como calcular el bono productivo
#             "frontier_bonus": 0, # Preguntar como calcular el bono fronterizo
#             "other_bonuses": 0, # Preguntar como calcular otros bonos
#             "tax_discount": 0, # Preguntar como calcular los descuentos RC-IVA
#             "health_box_discount": 0, # Preguntar como calcular los descuentos de la caja de salud
#             "other_discounts": 0, # Preguntar como calcular otros descuentos
#         }
#         return employee_data

#     def generate_data(self):
#         employee_ids = self.get_employee_ids()
#         employee_data = []
#         index = 1
#         for employee in employee_ids:
#             employee_data.append(self.employee_mintra_data(employee, position=index))
#             index += 1
#         return json.dumps({
#             "data": employee_data
#         })
