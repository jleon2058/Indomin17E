from odoo import api, fields, models


class PrintProductLabelLine(models.TransientModel):
    _inherit = 'print.product.label.line'

    picking_id = fields.Many2one(comodel_name='stock.picking')
    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        compute='_compute_partner_id'
    )
    date_done = fields.Datetime(
        string='Date Done',
        compute='_compute_date_done'
    )
    origin = fields.Char(
        string='Origin',
        compute='_compute_origin'
    )

    @api.depends('picking_id')
    def _compute_partner_id(self):
        for label in self:
            label.partner_id = label.picking_id.partner_id

    @api.depends('picking_id')
    def _compute_origin(self):
        for label in self:
            label.origin = label.picking_id.origin

    @api.depends('picking_id')
    def _compute_date_done(self):
        for label in self:
            label.date_done = label.picking_id.date_done
