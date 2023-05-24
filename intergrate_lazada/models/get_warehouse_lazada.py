from odoo import fields, models, api
from odoo.exceptions import ValidationError
class SStockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_push_lazada = fields.Boolean('Đồng bộ Lazada')
    e_commerce = fields.Selection([('lazada', 'Lazada'),
                                   ('tiktok', 'Tiktok')],
                                  string="Đồng bộ lên sàn TMĐT")

    @api.constrains("e_commerce","is_push_lazada")
    def _check_e_commerce(self):
        search_count = self.env['stock.warehouse'].search_count(['|',('e_commerce', '=', 'lazada'),('is_push_lazada', '=', True)])
        if search_count > 1:
            raise ValidationError('Kho của sàn TMĐT Lazada đã tồn tại.')




