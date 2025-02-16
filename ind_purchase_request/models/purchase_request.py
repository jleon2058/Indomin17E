from odoo import _, models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class PurchaseRequest(models.Model):

    _inherit = "purchase.request"

    request_type = fields.Selection(
        [("programado", "Programado"),
         ("no_programado", "No Programado"),
         ("consumible", "Consumible"),
         ("reembolsable", "Reembolsable"),
        ],
        string = "Tipo de RFQ",
        default = False,
        index = True
    )
    
    @api.constrains('request_type')
    def _check_request_type_for_group(self):
        # Obtener el ID del grupo res_group_usuario_RFQ
        group_id = self.env.ref('ind_purchase_request.res_group_usuario_RFQ')

        # Verificar si el usuario actual pertenece al grupo res_group_usuario_RFQ
        if group_id in self.env.user.groups_id:
            # Si el usuario pertenece al grupo, verificar si el campo request_type está vacío
            for record in self:
                if not record.request_type:
                    raise ValidationError("El campo 'Tipo de RFQ' es obligatorio.")

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
        readonly=True
    )

    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
        readonly=True
    )
                    
    planning = fields.Boolean(
        string='Planning Field',
        comodel_name="res.users",
        related="requested_by.planning",
    )
    observations = fields.Char(
        string="Observaciones",
        help="Inserte un archivo"
    )
    document_file = fields.Binary(
        string="Documentos",
    )
    document_file_name = fields.Char(
        string="Nombre del Documento",
        size=80
    )
    approved_by = fields.Many2one(
        comodel_name ="res.users",
        string = "Aprobado por",
        readonly = "True",
        copy =False,
        tracking =True,
        index = True,
    )
    
    date_approved = fields.Datetime(
        string="Fecha de Aprobación",
        readonly = "True",
        copy = False,
        tracking = True,
        index = True,
    )
    
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        tracking=True,
        domain=lambda self: [
            "|",
            "|",
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_manager").id,
            ),
            (
                "groups_id",
                "in",
                self.env.ref("ind_purchase_request.group_purchase_request_manager_personal").id,
            ),
            (
                "groups_id",
                "in",
                self.env.ref("ind_purchase_request.group_purchase_request_manager_department").id,
            ),
        ],
        index=True,
    )

    costo_promedio_total = fields.Float(
        compute="_compute_costo_promedio",
        string="Total Costo en base al Promedio",
        store=True,
    )

    @api.depends("line_ids", "line_ids.costo_promedio")
    def _compute_costo_promedio(self):
        for rec in self:
            rec.costo_promedio_total = sum(rec.line_ids.mapped("costo_promedio"))
    
    @api.depends('line_ids.product_id.detailed_type')
    def button_to_approve(self):
        for request in self:
            for req in request.line_ids:
                if req.product_id.detailed_type in ['service','product']:
                    pass
                else:
                    raise ValidationError("El producto {} esta configurado como consumible".format(req.name))

            self.to_approve_allowed_check()
            return self.write({"state": "to_approve"})

    def button_approved(self):
        self.approved_by = self.env.user
        self.date_approved = fields.Datetime.now()
        super(PurchaseRequest, self).button_approved()
    
    @api.depends('line_ids.request_state')
    def button_draft(self):
        for request in self:
            if all(req.purchase_state in ['cancel',False] for req in request.line_ids):
            #if all(req.purchase_state is False for req in request.line_ids):

                self.approved_by = False
                self.date_approved = False
                super(PurchaseRequest, self).button_draft()
            else:
                raise ValidationError("El requerimiento esta asociado a una OC no cancelada")

    def print_report_purchase_request(self):
        return self.env.ref('ind_purchase_request.action_indomin_report_purchase_requests').report_action(self)

    @api.depends('line_ids.request_state')
    def rechazar_requerimiento(self):
        for request in self:
            if all(req.request_state=='rejected' for req in request.line_ids):
                request.state='rejected'
    
    @api.depends('line_ids.request_state')
    def button_rejected(self):
        for request in self:
            if all(req.purchase_state in ['cancel',False] for req in request.line_ids):
            #if all(req.purchase_state is False for req in request.line_ids):
                self.mapped("line_ids").do_cancel()
                return self.write({"state": "rejected"})
            else:
                raise ValidationError("El requerimiento esta asociado a una OC no cancelada")
            
    def copy(self, default=None):
        if default is None:
            default = {}

        for line in self.line_ids:
            if not line.account_analytic_id:
                raise UserError("No se puede duplicar el requerimiento de compra porque contiene líneas sin centro de costos.")

        default['date_start'] = fields.Date.context_today(self)
        return super(PurchaseRequest, self).copy(default)