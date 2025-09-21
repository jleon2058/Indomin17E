from odoo import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_test_send_email_purchase_done(self):
        template = self.env.ref('ind_purchase_order.email_template_edi_notify_purchase_done')
        if template:
            for po in self:
                template.send_mail(po.id, force_send=True)