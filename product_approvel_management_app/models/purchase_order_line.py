# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.constrains('product_id')
    def _check_product_is_approved(self):
        unapproved = self.filtered(
            lambda l: l.product_id and l.product_id.state != 'approved'
        ).mapped('product_id')
        if unapproved:
            names = '\n'.join('- %s' % p.display_name for p in unapproved)
            raise ValidationError(_(
                'The following product(s) have not been approved yet. Only '
                'Approved products can be added to a purchase order:\n%s'
            ) % names)