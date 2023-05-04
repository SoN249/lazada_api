from odoo import fields, models


class SOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_item_id = fields.Char("Order item id")