from odoo import api, fields, models, SUPERUSER_ID, _

class product_product(models.Model):
    _inherit = "product.product"

    quick_prod_id = fields.Integer('QuickBook ProductId')
    lastupdate = fields.Datetime('Last Update Date')
    quick_export = fields.Boolean('Quick Export')



class product_template(models.Model):
    _inherit = "product.template"

    quick_prod_id = fields.Integer('QuickBook ProductId',related='product_variant_ids.quick_prod_id')
    lastupdate = fields.Datetime('Last Update Date',related='product_variant_ids.lastupdate')
    quick_export = fields.Boolean('Quick Export',related='product_variant_ids.quick_export')


class productCategory(models.Model):

    _inherit='product.category'

    quickbook_id=fields.Integer('Quickbook Id')
