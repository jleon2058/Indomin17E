from odoo import _, models, fields, api
from odoo.exceptions import UserError

class PurchaseRequestLine(models.Model):
    
    _inherit = "purchase.request.line"
    
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
    
    planning = fields.Boolean(
        string='Planning Field',
        related="request_id.planning",
    )

    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        store=True,
    )
    
    costo_promedio = fields.Float(string='Costo Promedio total',compute='_compute_costo_promedio',store=True)

    @api.depends('product_id.standard_price', 'product_qty')
    def _compute_costo_promedio(self):
        for line in self:
            if line.request_id.state not in ['approved','rejected','done']:
                if line.product_id and line.product_qty:
                    line.costo_promedio = line.product_id.standard_price * line.product_qty
                else:
                    line.costo_promedio = 0.0

    @api.onchange('company_id') 
    def _onchange_company_id(self):
        # Aplicar un dominio al campo account_analytic_id basado en la compañía seleccionada
        domain = [('company_id', '=', self.company_id.id)]
        return {'domain': {'account_analytic_id': domain}} 

    def write(self,vals):
        result = super(PurchaseRequestLine,self).write(vals)
        if 'request_state' in vals:
            self.mapped('request_id').rechazar_requerimiento()
        return result

    def rechazar_request_line(self):
        for record in self:
            if record.request_state == 'approved' and record.purchase_state in ['cancel',False]:
                record.request_state='rejected'
            else:
                raise UserError(_("Requerimiento {} cuyo item {} no esta aprobada o esta enlazada a una OC no cancelada").format(record.request_id.name,record.name))
        return True

    def rechazar_multiple_request_line(self):
        for record in self:
            record.rechazar_request_line()
        return {
            'type':'ir.actions.act_window_close'
        }