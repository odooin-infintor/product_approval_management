# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('product_id')
    def _check_product_is_approved(self):
        unapproved = self.filtered(
            lambda m: m.product_id and m.product_id.state != 'approved'
        ).mapped('product_id')
        if unapproved:
            names = '\n'.join('- %s' % p.display_name for p in unapproved)
            raise ValidationError(_(
                'The following product(s) have not been approved yet. Only '
                'Approved products can be moved in Inventory:\n%s'
            ) % names)