from odoo import models, fields
from odoo.exceptions import UserError
import logging
import json
import datetime

_logger = logging.getLogger(__name__)


class HrPayrollFiniquito(models.Model):
    _inherit = "hr.payroll.finiquito"

    def finiquito_open_form_action(self):
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "reporte.finiquito",
            "target": "new",
        }

        return action


class ReporteFiniquito(models.TransientModel):
    _name = "reporte.finiquito"
    _description = "Formulario para reporte de finiquitos"

    doc_type = fields.Selection(
        [
            ("pdf", "PDF"),
            ("csv", "CSV"),
        ],
        string="Formato de Documento",
    )
    report_file = fields.Binary("Archivo de reporte", readonly=True)
    file_name = fields.Char("Nombre de archivo")

    def get_employee(self):
        id = self._context.get("active_id")
        employee = self.env["hr.payroll.finiquito"].browse(id)
        return employee
    
    def generate_data(self,employee):
        data = {
            "document_type": self.doc_type,
            "name": employee.employee_id.display_name,
            "date_hire":employee.date_hire.strftime("%Y-%m-%d"),
            "date_end":employee.date_end.strftime("%Y-%m-%d"),
            "concept":[]
        }
        
        for i in range(1,4):
            month_data = {
                f"compensation{i}": getattr(employee,f"monthly_compensation{i}"),
                f"seniority_bonus{i}":getattr(employee,f"seniority_bonus{i}"),
                f"border_bonus{i}":getattr(employee,f"border_bonus{i}"),
                f"commissions{i}":getattr(employee,f"commissions{i}"),
                f"overtime{i}":getattr(employee,f"overtime{i}"),
                f"other_bonuses{i}":getattr(employee,f"other_bonuses{i}"),
                f"total_month{i}":getattr(employee,f"total{i}"),
            }
            data["concept"].append(month_data)
        
        return json.dumps(data)

    def action_generate_report(self):
        if not self.doc_type:
            raise UserError("Selecciona el formato de documento")

        employee = self.get_employee()
        api_key = ""
        url_service = ""
        data = self.generate_data(employee)
        _logger.info(data)

        return True
