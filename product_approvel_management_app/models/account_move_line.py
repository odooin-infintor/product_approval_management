# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('product_id')
    def _check_product_is_approved(self):
        invoice_types = ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
        unapproved = self.filtered(
            lambda l: l.display_type in (False, 'product')
            and l.move_id.move_type in invoice_types
            and l.product_id
            and l.product_id.state != 'approved'
        ).mapped('product_id')
        if unapproved:
            names = '\n'.join('- %s' % p.display_name for p in unapproved)
            raise ValidationError(_(
                'The following product(s) have not been approved yet. Only '
                'Approved products can be used on an invoice or bill:\n%s'
            ) % names)