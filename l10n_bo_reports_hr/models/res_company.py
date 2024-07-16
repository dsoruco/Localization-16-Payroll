from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"
    
    report_api_key = fields.Char("API KEY")
    url_report_service = fields.Char("URL del servicio")