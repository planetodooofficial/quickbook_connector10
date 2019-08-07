from odoo import api, fields, models, SUPERUSER_ID, _

class sale_order(models.Model):
    _inherit = "sale.order"

    quick_sale_id = fields.Integer('QuickBook SaleId')
    quick_export = fields.Boolean('Quick Export')