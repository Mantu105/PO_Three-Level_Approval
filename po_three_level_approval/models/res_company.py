from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    three_level_approve = fields.Boolean(string="Three Level Approval")
    # approval_email_template = fields.Many2one(
    #     "mail.template",
    #     string="Approval Email Template",
    #     domain=[("model_id", "=", "purchase.model_purchase_order")],
    # )
    # refuse_email_template = fields.Many2one(
    #     "mail.template",
    #     string="Refuse Email Template",
    #     domain=[
    #         ("model_id", "=", "po_three_level_approval.model_refuse_reason_wizard")
    #     ],
    # )
    manager_approve_limit = fields.Float(string="Manager Approve Limit")
    finance_manager_approve_limit = fields.Float(string="Finance Manager Approve Limit")
    director_approve_limit = fields.Float(string="Director Approve Limit")
