from odoo import api,fields,models,_
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_status = fields.Selection(
        [("pago", "Área de pago"),
         ("transporte", "Área de Transporte"),
         ("proveedor","Proveedor trae"),
         ("almacen","En almacén"),
         ("regularización","Regularización"),
        ],
        string="Estado de Pedido",
        default=False,
        index=True,
    )

    # currency_rate = fields.Float(
    #     string="Tipo de Cambio",
    #     compute="_compute_currency_rate",
    #     help="Tipo de cambio según la fecha de la orden y la moneda seleccionada.",
    # )

    inverse_rate = fields.Float("Tipo de cambio", compute="_compute_date_currency_rate", 
                                compute_sudo=True, store=True, readonly=False, digits=(9, 3))
    fake_inverse_rate = fields.Float("Tipo de cambio falso", store=True, digits=(9,3))

    view_notes = fields.Boolean(string='Imprimir notas', default=True)
    
    purchase_request_related = fields.Many2many('purchase.request', string='RFQs Relacionadas', compute='_compute_related_rfqs', copy=False, store=True)
    
    rfq_related_count = fields.Integer(string='RFQs de origen', compute='_compute_rfq_count')
    
    date_picking = fields.Datetime(string="Fecha de recojo", store=True, tracking=True)

    def action_view_rfq(self):
        return self._get_action_view_rfq(self.purchase_request_related)
    
    def _get_action_view_rfq(self, rfqs):
        """ This function returns an action that display existing rfqs of given purchase order ids. When only one found, show the rfq immediately.
        """
        self.ensure_one()
        result = self.env["ir.actions.actions"]._for_xml_id('purchase_request.purchase_request_form_action')
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name}
        # choose the view_mode accordingly
        if not rfqs or len(rfqs) > 1:
            result['domain'] = [('id', 'in', rfqs.ids)]
        elif len(rfqs) == 1:
            res = self.env.ref('purchase_request.view_purchase_request_form', False)
            form_view = [(res and res.id or False, 'form')]
            result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if view != 'form']
            result['res_id'] = rfqs.id
        return result
    
    # @api.depends('currency_id', 'date_order')
    # def _compute_currency_rate(self):
    #     for order in self:
    #         if order.currency_id != order.company_id.currency_id:
    #             # Obtenemos el tipo de cambio según la moneda y la fecha de la orden
    #             order.currency_rate = order.currency_id._get_conversion_rate(
    #                 order.company_id.currency_id,
    #                 order.currency_id,
    #                 order.company_id,
    #                 order.date_order or fields.Date.today()
    #             )
    #         else:
    #             order.currency_rate = 1.0  # No hay cambio si la moneda es la misma que la de la compañía

    def button_update_currency_rate(self):
        datetime_today = datetime.now()
        datetime_today = int(datetime_today.strftime('%Y%m%d%H%M%S'))
        purchase_order_to_update = self.search([('state', '=', 'purchase')])
        for purchase_order in purchase_order_to_update:
            purchase_order.fake_inverse_rate = datetime_today
    
    @api.depends('date_approve', 'date_order', 'currency_id', 'company_id', 'company_id.currency_id', 'fake_inverse_rate')
    def _compute_date_currency_rate(self):
        for record in self:
            if record.currency_id.name == 'PEN':
                record.inverse_rate = 1
                continue

            date = record.date_approve or record.date_order
            if date:
                # Obtener la tasa de cambio para la fecha actual
                currency_id = record.currency_id.id
                company_id = record.company_id.id

                # Obtener la tasa de cambio para la fecha de aprobación o de orden
                currency_rate = self.env['res.currency.rate'].search(
                    [('currency_id', '=', currency_id),
                     ('name', '=', date),
                     ('company_id', '=', company_id)],
                    limit=1)

                if currency_rate:
                    rate = round(1.0 / currency_rate.rate, 3)
                    record.inverse_rate = rate
                else:
                    raise ValidationError(_('No se ha encontrado tipo de cambio a la fecha para la OC: %s') % record.name)
            else:
                record.inverse_rate = 0


    @api.depends('purchase_request_related')
    def _compute_rfq_count(self):
        for rfq in self:
            rfq.rfq_related_count = len(rfq.purchase_request_related)
    
    @api.depends('order_line.purchase_request_lines.request_id')
    def _compute_related_rfqs(self):
        for order in self:
            rfqs = order.order_line.mapped('purchase_request_lines.request_id')
            order.purchase_request_related = [(6, 0, rfqs.ids)]

    def button_draft(self):
        for order in self:
            for line in order.order_line:
                allocations = self.env['purchase.request.allocation'].search([
                    ('purchase_line_id', '=', line.id)
                ])

                for allocation in allocations:
                    request_state = allocation.purchase_request_line_id.request_state
                    if request_state in ['rejected','draft','to_approve']:
                        raise ValidationError("No se puede cambiar a borrador porque la solicitud no está aprobada")
                    else:
                        self.write({'state': 'draft'})
                        return {}
    
    taxes_id = fields.Many2many('account.tax', string="Impuestos")

    @api.onchange('taxes_id')
    def _onchange_taxes_id(self):
        # Al cambiar los impuestos generales, se actualizan los impuestos de las líneas
        for order in self:
            if order.taxes_id:
                for line in order.order_line:
                    line.taxes_id = [(6, 0, order.taxes_id.ids)]

    def button_confirm(self):
        # Llamar al método original para confirmar la orden de compra
        res = super(PurchaseOrder, self).button_confirm()
        
        # Recorrer las órdenes y sus líneas para actualizar los movimientos de inventario
        for order in self:
            for line in order.order_line:
                # Verificar si la línea de pedido tiene una distribución analítica
                if line.analytic_distribution:
                    # Buscar movimientos de inventario generados para esta línea de pedido
                    stock_moves = self.env['stock.move'].search([
                        ('purchase_line_id', '=', line.id)
                    ])
                    
                    # Actualizar cada movimiento con la misma distribución analítica
                    stock_moves.write({
                        'analytic_distribution': line.analytic_distribution
                    })
        
        return res