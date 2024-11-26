from odoo import models, fields


class ResGroup(models.Model):
    _inherit = "res.groups"

    def get_application_groups(self, domain):
        group_id = self.env.ref("purchase.group_purchase_manager").id
        # user_group_id = self.env.ref("purchase.group_purchase_user").id
        return super(ResGroup, self).get_application_groups(
            domain + [("id", "!=", group_id)]
        )
