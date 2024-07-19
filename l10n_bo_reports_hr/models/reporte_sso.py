from odoo import models, fields


class ReporteFiniquito(models.TransientModel):
    _name = "reporte.sso"
    _description = "Formulario para reporte de seguro social obligatorio"

    doc_type = fields.Selection(
        [("xlsx", "Excel"), ("csv", "CSV")],
        string="Formato de documento",
        default="xlsx",
    )

    # action para abrir popup en caso de necesitarse
    # def finiquito_open_form_action(self):
    #     action = {
    #         "type": "ir.actions.act_window",
    #         "view_mode": "form",
    #         "res_model": "reporte.finiquito",
    #         "target": "new",
    #     }

    #     return action
