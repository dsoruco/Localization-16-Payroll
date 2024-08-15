from odoo import models, fields


class HrPayrollRpi(models.Model):
    _name = "hr.payroll.rpi"
    _description = "Reporte de Planilla Impositiva"

    doc_type = fields.Selection(
        [
            ("pdf", "PDF"),
            ("csv", "CSV"),
        ],
        string="Formato de Documento",
        default="pdf",
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

    def action_generate_report(self):
        return True