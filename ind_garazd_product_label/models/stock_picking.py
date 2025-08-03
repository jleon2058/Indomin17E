from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_open_label_type(self):
        if not self.env['ir.config_parameter'].sudo().get_param('garazd_product_label.replace_standard_wizard'):
            return super(StockPicking, self).action_open_label_type()
        action = self.env['ir.actions.act_window']._for_xml_id('ind_garazd_product_label.action_print_label_from_stock_picking')
        action['context'] = {'default_picking_ids': self.ids}
        return action
