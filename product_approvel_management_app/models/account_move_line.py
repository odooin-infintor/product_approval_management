# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('product_id')
    def _check_product_is_approved(self):
        invoice_types = ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
        for line in self:
            if (line.display_type in (False, 'product')
                    and line.move_id.move_type in invoice_types
                    and line.product_id
                    and line.product_id.state != 'approved'):
                raise ValidationError(_(
                    'The product "%s" has not been approved yet. Only '
                    'Approved products can be used on an invoice or bill.'
                ) % line.product_id.display_name)
