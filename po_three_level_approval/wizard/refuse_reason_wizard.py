from odoo import models, fields, _


class RefuseReason(models.TransientModel):
    _name = "refuse.reason.wizard"
    _inherit = [
        "portal.mixin",
        "product.catalog.mixin",
        "mail.thread",
        "mail.activity.mixin",
    ]
    _description = "Write the Refuse Reason"

    refused_reason = fields.Char(string="Refuse Reason")
    purchase_order_id = fields.Many2one("purchase.order", string="Purchase Order")

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

    def generate_email_body(self, recipient_name, order_name, refused_reason):
        return f"""
        <div style="margin: 0px; padding: 0px;">
           <p style="margin: 0px; padding: 0px; font-size: 13px;">
            Dear {recipient_name},
            <br/>
            <p> Please, Approve Purchase Order
            <strong>{order_name}</strong></p>
            <p>
            Reason :{refused_reason}</p>
            <br/>
            Regards,
            <p>{self.env.user.name}</p>
            </p>
        </div>
    """

    def refuse_button_record(self):
        for wizard in self:
            if wizard.purchase_order_id:
                wizard.purchase_order_id.refused_reason = wizard.refused_reason
                wizard.purchase_order_id.state = "refuse"
                user_group = self.env.ref(
                    "po_three_level_approval.group_purchase_user_access"
                )
                demo_users = self.env["res.users"].search(
                    [("groups_id", "in", user_group.id)]
                )
                for demo_user in demo_users:
                    if demo_user.email:
                        subject = (
                            f"Purchase Order: {self.purchase_order_id.name}(Refused)"
                        )
                        body = self.generate_email_body(
                            demo_user.name,
                            self.purchase_order_id.name,
                            self.refused_reason,
                        )
                        self.send_email(subject, body, demo_user["email"])
                        wizard.purchase_order_id.message_post(
                            body=_("Email sent to %s with subject: %s. Reason: %s")
                            % (demo_user.email, subject, wizard.refused_reason)
                        )
