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

class quick_account(models.Model):
    _name = "quick.account"

    name = fields.Char('Name', size=255, required="1")
    classification = fields.Char('Classification')
    acc_type = fields.Char('Account Type', size=264, required="1")
    active = fields.Boolean('Active')
    quick_acc_id = fields.Integer('QuickBook AccountId')
    acc_id = fields.Many2one('account.account','Odoo Account')

# quick_account()

class quick_merge(models.Model):
    _name = "quick.marge"

    acc_id = fields.Many2one('account.account','Odoo Account')
    acc_quick_id = fields.Many2one('quick.account','Quick Account')

# quick_merge()