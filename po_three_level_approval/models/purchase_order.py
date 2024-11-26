# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(
        [
            ("draft", "RFQ"),
            ("to_manager_approve", "Waiting for Manager Approval"),
            ("to_finance_approval", "Waiting for Finance Manager Approval"),
            ("to_director_approval", "Waiting for Director Approval"),
            ("purchase", "Purchase Order"),
            ("cancel", "Cancel"),
            ("refuse", "Refuse"),
        ],
        string="Status",
        readonly=True,
        index=True,
        track_visibility="onchange",
        default="draft",
    )

    def send_email(self, subject, body, recipient_email):
        mail = (
            self.env["mail.mail"]
            .sudo()
            .create(
                {
                    "subject": subject,
                    "body_html": body,
                    "email_to": recipient_email,
                    "email_from": self.env.user.email,
                }
            )
        )
        mail.send()
        # import pdb;pdb.set_trace()
        self.message_post(
        body=_("Email sent to %s with subject: %s") % (recipient_email, subject),
        )

    def generate_email_body(self, recipient_name, order_name):
        return f"""
        <div style="margin: 0px; padding: 0px;">
            <p style="margin: 0px; padding: 0px; font-size: 13px;">
                Dear {recipient_name},
                <br/>
                <p> Please, Approve Purchase Order
                <strong>{order_name}</strong>
                </p>
                <br/>
                Regards,
                <p>{self.env.user.name}</p>
            </p>
        </div>
        """

    def button_confirm(self):
        # import pdb;pdb.set_trace()
        for order in self:
            if order.company_id.three_level_approve:
                if order.amount_total > order.company_id.manager_approve_limit:
                    order.state = "to_manager_approve"
                    purchase_manager_group = self.env.ref(
                        "po_three_level_approval.group_purchase_manager_access"
                    )
                    managers = self.env["res.users"].search(
                        [("groups_id", "=", purchase_manager_group.id)]
                    )
                    for manager in managers:
                        if manager.email:
                            subject = f"Approval Purchase Order: {order.name} (Waiting)"
                            body = self.generate_email_body(manager.name, order.name)
                            self.send_email(subject, body, manager["email"])
                else:
                    super(PurchaseOrder, order).button_confirm()
            else:
                order.state = "purchase"
                super(PurchaseOrder, order).button_confirm()

    def button_approve(self, force=True):
        for order in self:
            if order.company_id.three_level_approve:
                if order.state == "to_manager_approve":
                    order.manager_approval = self.env.user
                    order.purchase_manager = self.env.user
                    order.manager_approval_date = date.today()
                    if (
                        order.amount_total
                        > order.company_id.finance_manager_approve_limit
                    ):
                        order.state = "to_finance_approval"
                        finance_manager_group = self.env.ref(
                            "po_three_level_approval.group_purchase_finance_manager_access"
                        )
                        finance_managers = self.env["res.users"].search(
                            [("groups_id", "=", finance_manager_group.id)]
                        )
                        for finance_manager in finance_managers:
                            if finance_manager.email:
                                subject = (
                                    f"Approval Purchase Order: {order.name} (Waiting)"
                                )
                                body = self.generate_email_body(
                                    finance_manager.name, order.name
                                )
                                self.send_email(subject, body, finance_manager.email)
                    else:
                        order.state = "purchase"
                else:
                    super(PurchaseOrder, self).button_approve(force)
            else:
                order.state = "purchase"

    def button_approve_finance(self):
        for order in self:
            if order.company_id.three_level_approve:
                if order.state == "to_finance_approval":
                    order.finance_manager_approval = self.env.user
                    order.finance_manager = self.env.user
                    order.finance_manager_approval_date = date.today()
                    if order.amount_total > order.company_id.director_approve_limit:
                        order.state = "to_director_approval"
                        director_group = self.env.ref(
                            "po_three_level_approval.group_purchase_director_access"
                        )
                        director_managers = self.env["res.users"].search(
                            [("groups_id", "=", director_group.id)]
                        )
                        for director_manager in director_managers:
                            if director_manager.email:
                                subject = (
                                    f"Approval Purchase Order: {order.name} (Waiting)"
                                )
                                body = self.generate_email_body(
                                    director_manager.name, order.name
                                )
                                self.send_email(subject, body, director_manager.email)
                    else:
                        order.state = "purchase"
            else:
                order.state = "purchase"

    def button_approve_director(self):
        for order in self:
            if order.company_id.three_level_approve:
                if order.state == "to_director_approval":
                    order.director_approval = self.env.user
                    order.director_manager = self.env.user
                    order.director_approval_date = date.today()
                    order.state = "purchase"
            else:
                order.state = "purchase"

    manager_approval = fields.Many2one("res.users", string="Manager Approval")
    finance_manager_approval = fields.Many2one(
        "res.users", string="Finance Manager Approval"
    )
    director_approval = fields.Many2one("res.users", string="Director Approval")
    manager_approval_date = fields.Date(string="Manager Approval Date")
    finance_manager_approval_date = fields.Date(string="Finance Manager Approval Date")
    director_approval_date = fields.Date(string="Director Approval Date")

    purchase_manager = fields.Many2one("res.users", string="Purchase Manager")
    finance_manager = fields.Many2one("res.users", string="Finance Manager")
    director_manager = fields.Many2one("res.users", string="Director Manager")

    refused_by = fields.Many2one("res.users", string="Refused By")
    refused_date = fields.Date(string="Refused Date")
    refused_reason = fields.Char(string="Refused Reason")

    def button_refuse(self):
        for order in self:
            order.refused_by = self.env.user
            order.refused_date = date.today()
            wizard = self.env["refuse.reason.wizard"].create(
                {
                    "purchase_order_id": self.id,
                }
            )
            return {
                "name": "Refuse Purchase Order",
                "view_mode": "form",
                "view_id": self.env.ref(
                    "po_three_level_approval.refuse_reason_wizard_form_view"
                ).id,
                "res_model": "refuse.reason.wizard",
                "res_id": wizard.id,
                "type": "ir.actions.act_window",
                "target": "new",
            }
