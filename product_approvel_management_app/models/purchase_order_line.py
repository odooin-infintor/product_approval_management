# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.constrains('product_id')
    def _check_product_is_approved(self):
        for line in self:
            if line.product_id and line.product_id.state != 'approved':
                raise ValidationError(_(
                    'The product "%s" has not been approved yet. Only '
                    'Approved products can be added to a purchase order.'
                ) % line.product_id.display_name)
