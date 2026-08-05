# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class ProductApprovalRejectWizard(models.TransientModel):
    _name = 'product.approval.reject.wizard'
    _description = 'Reject Product(s)'

    product_ids = fields.Many2many('product.template', string='Products', required=True)
    reason = fields.Text(string='Reject Reason', required=True)

    def action_confirm_reject(self):
        self.ensure_one()
        if not self.reason or not self.reason.strip():
            raise UserError(_('Please provide a reject reason.'))
        self.product_ids._apply_rejection(self.reason)
        return {'type': 'ir.actions.act_window_close'}
