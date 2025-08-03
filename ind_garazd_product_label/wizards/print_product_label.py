from odoo import api, models, fields


class PrintProductLabel(models.TransientModel):
    _inherit = 'print.product.label'
    label_ids = fields.One2many(
        comodel_name='print.product.label.line',
        inverse_name='wizard_id',
        string='Labels for Products',
        default=lambda self: self._get_product_label_ids(),
    )

    @api.model
    def _get_product_label_ids(self):
        res = super()._get_product_label_ids()

        if self._context.get('active_model') == 'stock.picking':
            picking = self.env[self._context.get('active_model')].browse(self._context.get('default_picking_ids'))
            for move in picking.move_ids_without_package:

                analytic_account = False
                if move.analytic_distribution:
                    analytic_account_ids = list(move.analytic_distribution.keys())
                    analytic_account = self.env['account.analytic.account'].browse(int(analytic_account_ids[0]))
                        
                label = self.env['print.product.label.line'].create({
                    'product_id': move.product_id.id,
                    'account_analytic_id': analytic_account.id if analytic_account else False,
                    'picking_id': picking.id,
                    'partner_id': picking.partner_id.id,
                    'date_done': picking.date_done,
                    'origin': picking.origin,   
                    'qty': move.quantity
                })
                res.append(label.id)

        res = self._complete_label_fields(res)
        return res
