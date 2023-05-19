from odoo import fields, models
class SOrderLine(models.Model):
    _inherit = "sale.order.line"

    tracking_code = fields.Char('Tracking Code')