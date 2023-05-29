from odoo import fields, models, api

class SProductProduct(models.Model):
    _inherit = 'product.product'
    marketplace_sku = fields.Text("Marketplace SKU")
    is_merge_product = fields.Boolean("Is marge product")
    is_synchronized_stock = fields.Boolean("Đã đồng bộ tồn kho")


    # @api.onchange("is_merge_product")
    # def check_merge(self):

