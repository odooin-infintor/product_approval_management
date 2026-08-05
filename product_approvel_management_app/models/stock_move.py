# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('product_id')
    def _check_product_is_approved(self):
        for move in self:
            if move.product_id and move.product_id.state != 'approved':
                raise ValidationError(_(
                    'The product "%s" has not been approved yet. Only '
                    'Approved products can be moved in Inventory.'
                ) % move.product_id.display_name)
