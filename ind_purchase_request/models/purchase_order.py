from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

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
            
    @api.onchange('company_id') 
    def _onchange_company_id(self):
        # Aplicar un dominio al campo account_analytic_id basado en la compañía seleccionada
        domain = [('company_id', '=', self.company_id.id)]
        return {'domain': {'project_id': domain}}

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

class Currency(models.Model):
    _inherit = "res.currency.rate"
    
    @api.model
    def create_currency_rate_record(self):
        # Obtener las monedas y las compañías
        usd_currency = self.env.ref('base.USD')
        companies = self.env['res.company'].sudo().search([])

        url = 'https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx'
        response = requests.get(url, headers={'Cache-Control': 'no-cache'})

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'id': 'ctl00_cphContent_rgTipoCambio_ctl00'})
            if not table:
                raise ValidationError("No se pudo encontrar la tabla de tipo de cambio en la página de SBS.")
            
            rows = table.find_all('tr')

            # Ajustar la fecha actual
            today = datetime.now() + timedelta(days=1)
            today_str = today.strftime('%d/%m/%Y')

            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 3 and today_str in columns[0].text:
                    tipo_cambio_venta = float(columns[2].text.replace(',', '.'))

                    for company in companies:
                        existing_record = self.env['res.currency.rate'].sudo().search([
                            ('name', '=', fields.Date.today()),
                            ('currency_id', '=', usd_currency.id),
                            ('company_id', '=', company.id),
                        ])

                        if not existing_record:
                            currency_rate_data = {
                                'name': fields.Date.today(),
                                'rate': tipo_cambio_venta,
                                'currency_id': usd_currency.id,
                                'company_id': company.id,
                            }
                            self.env['res.currency.rate'].create(currency_rate_data)
                        else:
                            _logger.info("Ya existe un registro para la fecha y empresa actual. No se creará un nuevo tipo de cambio.")
                    break
        else:
            _logger.info(f"Error al realizar la solicitud GET. Código de estado: {response.status_code}")