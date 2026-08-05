# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('under_approval', 'Under Approval'),
            ('approved', 'Approved'),
            ('not_approved', 'Not Approved'),
        ],
        string='Approval Status',
        default='draft',
        copy=False,
        tracking=True,
        index=True,
        help='Draft: just created, not yet submitted.\n'
             'Under Approval: waiting for a Product Manager to review it.\n'
             'Approved: can be used in Sales, Purchases, Invoices and '
             'Inventory.\n'
             'Not Approved: rejected by a Product Manager, see the reject '
             'reason below.',
    )
    approved_by = fields.Many2one(
        'res.users', string='Approved By', copy=False, readonly=True, tracking=True)
    approved_date = fields.Datetime(
        string='Approved On', copy=False, readonly=True, tracking=True)
    rejected_by = fields.Many2one(
        'res.users', string='Rejected By', copy=False, readonly=True, tracking=True)
    rejected_date = fields.Datetime(
        string='Rejected On', copy=False, readonly=True, tracking=True)
    reject_reason = fields.Text(
        string='Reject Reason', copy=False, readonly=True, tracking=True)
    is_product_manager = fields.Boolean(
        string='Is Product Manager', compute='_compute_is_product_manager')

    @api.depends_context('uid')
    def _compute_is_product_manager(self):
        is_manager = self.env.user.has_group(
            'product_approvel_management_app.group_product_manager')
        for product in self:
            product.is_product_manager = is_manager

    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['state'] = 'draft'
            for f in ('approved_by', 'approved_date', 'rejected_by',
                      'rejected_date', 'reject_reason'):
                vals.pop(f, None)
        products = super().create(vals_list)
        # A newly created product is immediately submitted for approval,
        # and the Product Managers are notified.
        for product in products:
            product.state = 'under_approval'
            product._notify_product_managers(
                subject=_('New product waiting for approval'),
                body=_('%(user)s submitted the product "%(name)s" for approval.',
                       user=self.env.user.name, name=product.display_name),
            )
        return products

    # ---------------------------------------------------------
    # Workflow actions
    # ---------------------------------------------------------
    def _check_is_product_manager(self):
        if not self.env.user.has_group(
                'product_approvel_management_app.group_product_manager'):
            raise UserError(_(
                'Only a Product Manager can perform this action.'))

    def action_submit_for_approval(self):
        """Manual (re)submission, e.g. after being Not Approved."""
        self.write({'state': 'under_approval'})
        for product in self:
            product._notify_product_managers(
                subject=_('Product resubmitted for approval'),
                body=_('%(user)s resubmitted the product "%(name)s" for approval.',
                       user=self.env.user.name, name=product.display_name),
            )

    def action_approve(self):
        """Approve a single product. Product Managers only."""
        self._check_is_product_manager()
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
            'rejected_by': False,
            'rejected_date': False,
            'reject_reason': False,
        })
        for product in self:
            product.message_post(body=_(
                'Product approved by %s.', self.env.user.name))
            product._notify_submitter(
                subject=_('Product approved'),
                body=_('Your product "%s" has been approved.', product.display_name),
            )

    def action_reset_to_draft(self):
        """Reset the product back to Draft. Product Managers only."""
        self._check_is_product_manager()
        self.write({
            'state': 'draft',
            'approved_by': False,
            'approved_date': False,
            'rejected_by': False,
            'rejected_date': False,
            'reject_reason': False,
        })

    def action_open_reject_wizard(self):
        """Open the wizard to collect a reject reason (single or mass)."""
        self._check_is_product_manager()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Product(s)'),
            'res_model': 'product.approval.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_product_ids': self.ids},
        }

    def _apply_rejection(self, reason):
        self._check_is_product_manager()
        self.write({
            'state': 'not_approved',
            'rejected_by': self.env.user.id,
            'rejected_date': fields.Datetime.now(),
            'reject_reason': reason,
        })
        for product in self:
            product.message_post(body=_(
                'Product rejected by %(user)s.<br/>Reason: %(reason)s',
                user=self.env.user.name, reason=reason))
            product._notify_submitter(
                subject=_('Product rejected'),
                body=_('Your product "%(name)s" was rejected.<br/>Reason: %(reason)s',
                       name=product.display_name, reason=reason),
            )

    # ---------------------------------------------------------
    # Mass actions (bound to the Products list view Action menu)
    # ---------------------------------------------------------
    def action_mass_approve(self):
        self._check_is_product_manager()
        to_approve = self.filtered(lambda p: p.state != 'approved')
        to_approve.action_approve()
        return True

    def action_mass_reject(self):
        return self.action_open_reject_wizard()

    # ---------------------------------------------------------
    # Notifications
    # ---------------------------------------------------------
    def _notify_product_managers(self, subject, body):
        managers = self.env['res.users'].sudo().search([
            ('group_ids', '=', self.env.ref(
                'product_approvel_management_app.group_product_manager').id),
        ])
        partners = managers.mapped('partner_id') - self.env.user.partner_id
        if not partners:
            return
        for product in self:
            product.message_post(
                body=body,
                subject=subject,
                partner_ids=partners.ids,
                message_type='notification',
            )

    def _notify_submitter(self, subject, body):
        self.ensure_one()
        creator = self.create_uid
        if not creator or creator.id == self.env.user.id or not creator.partner_id:
            return
        self.message_post(
            body=body,
            subject=subject,
            partner_ids=[creator.partner_id.id],
            message_type='notification',
        )