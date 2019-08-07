import random
from odoo import SUPERUSER_ID
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.http import request
from datetime import datetime
import time

class account_invoice(models.Model):
    _inherit = "account.invoice"

    quick_invoice_id = fields.Integer('QuickBook InvoiceId',readonly=True)
    quick_export = fields.Boolean('Quick Export')
    paid_on_qb = fields.Boolean('Paid On QuickBook',readonly=True)
    faulty = fields.Boolean('Faulty')
    faulty_reason = fields.Text('Faulty Reason')

class account_tax(models.Model):
    _inherit = "account.tax"

    quick_id =  fields.Char('QB ID')


class AccountAccount(models.Model):

    _inherit='account.account'

    quickbook_chart_id=fields.Integer('Quickbook id')

    @api.model
    def create(self, vals):
        print ("creeate ///////////////")
        seq = self.env['ir.sequence'].next_by_code('account.account') or '/'
        print ("seq////////////",seq)
        vals['code']=seq
        print ("vals.............",vals['code'])
        return super(AccountAccount, self).create(vals)


class AccountPaymentTerm(models.Model):

    _inherit='account.payment.term'

    quickbook_id=fields.Char('Quickbook Id')









