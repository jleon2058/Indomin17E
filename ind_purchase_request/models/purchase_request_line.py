from odoo import api, fields, models
from odoo.exceptions import UserError
import json

import logging

_logger = logging.getLogger(__name__)


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    approved_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.approved_by",
        string="Aprobado por",
        store=True,
        readonly=True,
    )
    date_approved = fields.Datetime(
        related="request_id.date_approved",
        string="Fecha de Aprobación",
        store=True,
        readonly=True
    )
    request_type = fields.Selection(
        related="request_id.request_type",
        string="Tipo de RFQ",
        store=True,
        readonly=True
    )
    order_status = fields.Selection(
        related="purchase_lines.order_id.order_status",
        string="Estado de Pedido",
        store=True,
        readonly=True
    )
    request_state = fields.Selection(
        string='Estado RFQ',
        related='request_id.state',
        store=True
    )
    costo_promedio = fields.Monetary(
        string='Costo Promedio',
        compute='_compute_average_cost',
        store=True
    )
    product_classification_domain = fields.Json(
        string='Dominio para la clasificación del producto en el RFQ',
        compute='_compute_product_classification_domain'
    )
    classification_rfq = fields.Selection(
        string='Clasificación RFQ',
        related='request_id.classification_rfq',
        store=True
    )
    location_id = fields.Selection( #   TODO: Campo para eliminar en futuras versiones
        string='Ubicación (deprecado)',
        related='request_id.location_id',
        store=True
    )
    ubication_id = fields.Many2one(
        string='Ubicación',
        related='request_id.ubication_id',
        store=True
    )

    @api.depends('product_id')
    def _compute_product_classification_domain(self):
        for line in self:
            if line.classification_rfq:
                line.product_classification_domain = json.dumps([('categ_id.classification_rfq', '=', line.classification_rfq)])
            else:
                line.product_classification_domain = json.dumps([])

    @api.depends('product_id', 'product_id.standard_price', 'product_qty')
    def _compute_average_cost(self):
        for line in self:
            if line.request_id.state not in ['approved','rejected','done']:
                if line.product_id and line.product_qty:
                    line.costo_promedio = line.product_id.standard_price * line.product_qty
                else:
                    line.costo_promedio = 0.0

    def _reject_line(self):
        if self.request_state == 'approved' and self.purchase_state in ('cancel', False):
            self.do_cancel()
            return self.write({'request_state': 'rejected'})
        else:
            raise UserError("Requerimiento {} cuyo item {} no esta aprobado o esta enlazado a una OC no cancelada".format(self.request_id.name, self.name))

    def button_to_cancel_line(self):
        self.ensure_one()
        self._reject_line()

    def action_reject_multiple_lines(self):
        for record in self:
            record._reject_line()
        return { 'type': 'ir.actions.act_window_close' }

    # TODO: REFACTOR
    @api.onchange('product_id')
    def _onchange_check_request_fields(self):
        if self.request_id:
            missing_fields = []
            if not self.request_id.classification_rfq:
                missing_fields.append("Clase de RFQ")
            if not self.request_id.ubication_id:
                missing_fields.append("Ubicación")

            if missing_fields:
                msg = ""
                for miss_field in missing_fields:
                    msg += f"\n\t- {miss_field}"
                raise UserError(f"Debe completar los siguientes campos en el formulario antes de agregar líneas: {msg}")
