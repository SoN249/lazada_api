from odoo import fields, models, api
from odoo.exceptions import ValidationError

class WarehouseLazada(models.Model):
    _inherit = "stock.warehouse"

    ecom_id = fields.Many2one('list.ecommerce',string="Đồng bộ lên sàn TMĐT")
    is_push_lazada = fields.Boolean('Đồng bộ Lazada')
    @api.onchange('ecom_id')
    def check_platform(self):
        warehouse_id = self.search([]).mapped('ecom_id')
        if self.ecom_id.id in warehouse_id.ids:
            raise ValidationError("Sàn thương mại điện tử đã có kho hàng")



