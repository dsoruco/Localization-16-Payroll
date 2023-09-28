from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    treatment = fields.Selection([('senor', 'Sr.'), ('senora', 'Sra.')], string='Tratamiento')
    firstname = fields.Char("First name")
    firstname2 = fields.Char("Second name")
    lastname = fields.Char("Last name")
    lastname2 = fields.Char("Second last name")
    married_name = fields.Char("Apellido de casada")
