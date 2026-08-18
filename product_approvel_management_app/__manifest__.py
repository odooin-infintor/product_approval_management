# -*- coding: utf-8 -*-
{
    'name': 'Product Approval Management',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Approve or reject products before they can be used anywhere in Odoo.',
    'description': """
    Product Approval Management
    =================================================================================================
    Maintain control over the introduction of new products across your whole
    system. Combines the "simple confirm" workflow with a full 4-state
    approval flow, mass actions, and manager notifications.
    Key Features
    --------------------------------------------------------------------------------------------------
    * Products move through 4 states: Draft, Under Approval, Approved and
      Not Approved.
    * When a normal user creates a product it is automatically submitted
      and moved to "Under Approval".
    * Only users in the "Product Manager" group can Approve, Reject or
      reset a product.
    * Rejecting a product requires a reason, which is stored and shown in
      the chatter / Field history.
    * Mass Approve / Mass Reject actions available from the Products list
      view (Action menu), for approving or rejecting many products at once.
    * A dedicated "Under Approval Products" menu under Inventory > Products
      for managers to review pending requests quickly.
    * Only Approved products can be used on:
        - Sale Order lines
        - Purchase Order lines
        - Customer Invoice / Vendor Bill lines
        - Inventory transfers (stock moves)
    * Product Managers are notified (Discuss / chatter) whenever a new
      product is submitted for approval, and the submitter is notified
      when their product is approved or rejected.
    """,
    'author': 'Infintor Solutions',
    'website': 'https://www.infintor.com',

    # --- Licensing & pricing ---
    'license': 'Other proprietary',
    'price': 15.00,
    'currency': 'USD',
    'images': [
        'static/description/banner.png',
     ],

    'depends': ['sale_management', 'purchase', 'account', 'stock', 'mail'],

    'data': [
        'security/product_approval_security.xml',
        'security/ir.model.access.csv',
        'wizard/product_approval_reject_wizard_views.xml',
        'views/product_template_views.xml',
        'views/product_approval_menus.xml',
        'data/server_actions.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
