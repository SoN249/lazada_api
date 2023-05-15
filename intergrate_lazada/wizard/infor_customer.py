from odoo import fields, models, api

class InforCusomer(models.TransientModel):
    _name="infor.customer"

    order_id = fields.Many2one('sale.order', readonly=True)
    partner_id = fields.Many2one('res.partner')

    @api.model
    def default_get(self, fields):
        res = super(InforCusomer, self).default_get(fields)
        res['order_id'] = self.env.context.get('active_id')
        return res

    def btn_confirm(self):
        if self.partner_id:
            self.order_id.write({
                "partner_id": self.partner_id
            })

