# -*- coding: utf-8 -*-
# from odoo import http
# import odoo
# import odoo.modules.registry
# from odoo import http
# from odoo.exceptions import AccessError
# from odoo.http import request
# from odoo.service import security
# from odoo.tools import ustr
# from odoo.tools.translate import _

# from odoo.addons.web.controllers.home import Home

# class MyUserManager(Home):
    
    # @http.route('/web/login', type='http', auth="none")
    # def web_login(self, redirect=None, **kw):
        
    #     request.params.update({
    #         "company_name": 1
    #     })
        
    #     response = super(MyUserManager, self).web_login(self)
        
    #     return response
    
    
#     @http.route('/user_manager/user_manager', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/user_manager/user_manager/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('user_manager.listing', {
#             'root': '/user_manager/user_manager',
#             'objects': http.request.env['user_manager.user_manager'].search([]),
#         })

#     @http.route('/user_manager/user_manager/objects/<model("user_manager.user_manager"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('user_manager.object', {
#             'object': obj
#         })
