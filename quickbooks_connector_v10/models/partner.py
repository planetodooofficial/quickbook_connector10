import random
from odoo import SUPERUSER_ID
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.http import request
from datetime import datetime
import time

class res_partner(models.Model):
    _inherit = "res.partner"

    quick_id = fields.Char('QuickBook Id',readonly=True)
    quick_export = fields.Boolean('Quick Export')
    faulty = fields.Boolean('Faulty')
    faulty_reason = fields.Text('Faulty Reason')
    create_time=fields.Char('Create Time')
    last_update_time=fields.Char('Last Update Time')


class ResTitle(models.Model):
    _inherit='res.partner.title'

    quick_book_id=fields.Integer('Quickbook ID')




class ResPartner(models.Model):

    _inherit='res.partner'

    quic_bill_shipp = fields.Integer('Quick Bill Ship Id')
    quic_bill_invoice=fields.Integer('Quick Bill Invoice Id')



    
# class purchase_order(models.Model):
#     _inherit = "purchase.order"
#
#     quick_purchase_id = fields.Integer('QuickBook PurchaseId')
#     quick_export = fields.Boolean('Quick Export')

# class sale_order(models.Model):
#     _inherit = "sale.order"
#
#     quick_sale_id = fields.Integer('QuickBook SaleId')
#     quick_export = fields.Boolean('Quick Export')

#class account_account(osv.osv):
#    _inherit = "account.account"
#    _columns = {
#        'quick_acc_id': fields.integer('QuickBook AccountId'),
#    }
    
    
# class quick_quick(models.Model):
#     _name = "quick.quick"
#
#     lastupdate_cust = fields.Datetime('Last Update Date')
#     exportdate_cust = fields.Datetime('Last Export Date')
#     lastupdate_sup = fields.Datetime('Last Update Date')
#     exportdate_sup = fields.Datetime('Last Export Date')
#     lastupdate_item = fields.Datetime('Last Update Date')
#     exportdate_item = fields.Datetime('Last Export Date')
#     from_date_in = fields.Datetime('From Date')
#     to_date_in = fields.Datetime('To Date')
#     from_date_ex_in = fields.Datetime('From Date')
#     to_date_ex_in = fields.Datetime('To Date')
#     from_date_pr = fields.Datetime('From Date')
#     to_date_pr = fields.Datetime('To Date')
#     from_date_ex_pr = fields.Datetime('From Date')
#     to_date_ex_pr = fields.Datetime('To Date')
#     from_date_so = fields.Datetime('From Date')
#     to_date_so = fields.Datetime('To Date')
#     from_date_ex_so = fields.Datetime('From Date')
#     to_date_ex_so = fields.Datetime('To Date')
#     lastupdate_acc = fields.Datetime('Last Update Date')


