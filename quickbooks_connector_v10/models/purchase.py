from odoo import api, fields, models, SUPERUSER_ID, _

class purchase_order(models.Model):
    _inherit = "purchase.order"

    quick_purchase_id = fields.Integer('QuickBook PurchaseId')
    quick_export = fields.Boolean('Quick Export')
