from odoo import fields, models, api
from odoo.exceptions import ValidationError

class WarehouseLazada(models.Model):
    _inherit = "stock.warehouse"

    ecommerce_platform = fields.Many2one('list.ecommerce',string="Đồng bộ lên sàn TMĐT")
    is_push_lazada = fields.Boolean('Đồng bộ Lazada')
    @api.onchange('ecommerce_platform')
    def check_platform(self):
        warehouse_id = self.search([]).mapped('ecommerce_platform')
        if self.ecommerce_platform.id in warehouse_id.ids:
            raise ValidationError("Sàn thương mại điện tử đã có kho hàng")



