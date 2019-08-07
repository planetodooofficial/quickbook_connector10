# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, SUPERUSER_ID, _
import datetime

class quick_configuration(models.Model):
    _name = "quick.configuration"
    
    def get_url(self, chval):
        if chval:
            return {'value':{'url': 'https://quickbooks.api.intuit.com/v3/company/'}}
        else:
            return {'value':{'url': 'https://sandbox-quickbooks.api.intuit.com/v3/company/'}}
        
    clientkey =  fields.Char('Client Key', size=255, required="1")
    clientsecret = fields.Char('Client Secret', size=264, required="1")
    request_token_url = fields.Char('Request Token Url', size=264)
    access_token_url = fields.Char('Access Token Url', size=264)
    authorization_base_url = fields.Char('Authorization Base Url', size=264)
    company = fields.Char('Company Id', size=264)
    url = fields.Char('Url', required="1" , default = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' )
    production = fields.Boolean('Production')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


# quick_configuration()