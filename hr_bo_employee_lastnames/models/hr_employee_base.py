from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    treatment = fields.Selection([('Sr.', 'Sr.'), ('Sra.', 'Sra.')], string='Tratamiento')
    firstname = fields.Char("First name", size=20)
    firstname2 = fields.Char("Second name", size=20)
    lastname = fields.Char("Last name", size=20)
    lastname2 = fields.Char("Second last name", size=20)
    married_name = fields.Char("Apellido de casada", size=20)
