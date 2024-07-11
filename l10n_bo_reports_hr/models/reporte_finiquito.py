from odoo import models,fields
import logging

_logger = logging.getLogger(__name__)
class HrPayrollFiniquito(models.Model):
    _inherit="hr.payroll.finiquito"
    
    def finiquito_open_form_action(self):
        action= {
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'reporte.finiquito',
            'target':'new',
        }
        
        return action

class ReporteFiniquito(models.TransientModel):
    _name = "reporte.finiquito"
    _description = "Formulario para reporte de finiquitos"
    
    doc_type = fields.Selection([
        ("pdf", "PDF"),
        ("csv", "CSV"),
    ], string="Formato de Documento")
    report_file = fields.Binary("Archivo de reporte", readonly=True)
    file_name = fields.Char("Nombre de archivo")
    
    def get_employee(self):
        id = self._context.get("active_id")
        employee = self.env['hr.payroll.finiquito'].browse(id)
        return employee
    
    def action_generate_report(self):
        employee = self.get_employee()        
        _logger.info(employee.finiquito)
        
        return True