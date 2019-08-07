from odoo import api, fields, models, SUPERUSER_ID, _

class quick_quick(models.Model):
    _name = "quick.quick"

    lastupdate_cust = fields.Datetime('Last Update Date')
    exportdate_cust = fields.Datetime('Last Export Date')
    lastupdate_sup = fields.Datetime('Last Update Date')
    exportdate_sup = fields.Datetime('Last Export Date')
    lastupdate_item = fields.Datetime('Last Update Date')
    exportdate_item = fields.Datetime('Last Export Date')
    from_date_in = fields.Datetime('From Date')
    to_date_in = fields.Datetime('To Date')
    from_date_ex_in = fields.Datetime('From Date')
    to_date_ex_in = fields.Datetime('To Date')
    from_date_pr = fields.Datetime('From Date')
    to_date_pr = fields.Datetime('To Date')
    from_date_ex_pr = fields.Datetime('From Date')
    to_date_ex_pr = fields.Datetime('To Date')
    from_date_so = fields.Datetime('From Date')
    to_date_so = fields.Datetime('To Date')
    from_date_ex_so = fields.Datetime('From Date')
    to_date_ex_so = fields.Datetime('To Date')
    lastupdate_acc = fields.Datetime('Last Update Date')