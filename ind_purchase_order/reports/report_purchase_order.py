from odoo import models
from odoo.fields import Datetime


_RFQ_TYPE = {
    'programado': 'PREVENTIVO',
    'no_programado': 'CORRECTIVO',
    'consumible': 'CONSUMIBLE',
    'reembolsable': 'REEMBOLSABLE',
    'activo fijo': 'ACTIVO FIJO'
}

_RFQ_CLASS = {
    'service': 'SERVICIO',
    'products': 'PRODUCTOS',
    'fixed_assets': 'ACTIVO FIJO',
    'rental_service': 'SERVICIO DE ALQUILER'
}

_ORDER_STATUS = {
    'pago': 'Área de pago',
    'transporte': 'Área de transporte',
    'proveedor': 'Proveedor trae',
    'almacen': 'En almacén',
    'regularización': 'Regularización',
    'en_aprobación': 'En aprobación'
}

_OC_STATE = {
    'draft': 'SdP',
    'to approve': 'Para Aprobar',
    'purchase': 'Orden de Compra',
    'cancel': 'Cancelado'
}

class PurchaseOrderXlsx(models.AbstractModel):
    _name = 'report.ind_purchase_order.report_oc'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Reporte de OC'

    def generate_xlsx_report(self, workbook, data, records):
        records = records.with_context(active_test=False)
        style_column = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 10,
            'bold': True,
            'border': 1
        })
        style_number = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
        })
        style_content = workbook.add_format({
            'valign': 'vcenter',
            'font_size': 10,
        })
        style_date = workbook.add_format({
            'font_size': 10,
            'num_format': 'yyyy-mm-dd hh:mm:ss',
            'align': 'center',
        })
        
        ws = workbook.add_worksheet('Reporte de OC')
        ws.set_column('A:A', 20)  # Fecha de creación
        ws.set_column('B:B', 20)  # Fecha de aprobación
        ws.set_column('C:C', 18)  # Referencia de OC
        ws.set_column('D:D', 60)  # Producto
        ws.set_column('E:E', 60)  # Familia del producto
        ws.set_column('F:F', 10)  # Cantidad
        ws.set_column('G:G', 10)  # Unidad de medida
        ws.set_column('H:H', 50)  # Proveedor
        ws.set_column('I:I', 19)  # Requerimiento
        ws.set_column('J:J', 15)  # CECO
        ws.set_column('K:K', 45)  # Centro de costo
        ws.set_column('L:L', 15)  # Estado de pedido
        ws.set_column('M:M', 10)  # Tipo de moneda
        ws.set_column('N:N', 10)  # Tipo de cambio
        ws.set_column('O:O', 10)  # Costo unitario
        ws.set_column('P:P', 12)  # Subtotal
        ws.set_column('Q:Q', 10)  # Impuesto
        ws.set_column('R:R', 13)  # IVG
        ws.set_column('S:S', 10)  # TOTAL
        ws.set_column('T:T', 20)  # Estado de orden de compra
        ws.set_column('U:U', 15)  # Plazos de pago
        ws.set_column('V:V', 15)  # Tipo de requerimiento
        ws.set_column('W:W', 18)  # Clase de RFQ
        ws.set_column('X:X', 15)  # Ubicación

        ws.write(0, 0, 'FECHA DE CREACIÓN', style_column)
        ws.write(0, 1, 'FECHA DE APROBACIÓN', style_column)
        ws.write(0, 2, 'ORDEN DE COMPRA', style_column)
        ws.write(0, 3, 'PRODUCTO', style_column)
        ws.write(0, 4, 'FAMILIA', style_column)
        ws.write(0, 5, 'CANTIDAD', style_column)
        ws.write(0, 6, 'UNIDAD DE MEDIDA', style_column)
        ws.write(0, 7, 'PROVEEDOR', style_column)
        ws.write(0, 8, 'REQUERIMIENTO', style_column)
        ws.write(0, 9, 'CECO', style_column)
        ws.write(0, 10, 'CENTRO DE COSTO', style_column)
        ws.write(0, 11, 'ESTADO DE PEDIDO', style_column)
        ws.write(0, 12, 'TIPO DE MONEDA', style_column)
        ws.write(0, 13, 'TIPO DE CAMBIO (NO)', style_column)
        ws.write(0, 14, 'COSTO UNITARIO (NO)', style_column)
        ws.write(0, 15, 'SUBTOTAL (NO)', style_column)
        ws.write(0, 16, 'IMPUESTO (NO)', style_column)
        ws.write(0, 17, 'IVG', style_column)
        ws.write(0, 18, 'TOTAL', style_column)
        ws.write(0, 19, 'ESTADO DE ORDEN DE COMPRA', style_column)
        ws.write(0, 20, 'PLAZOS DE PAGO', style_column)
        ws.write(0, 21, 'TIPO DE RFQ', style_column)
        ws.write(0, 22, 'CLASE DE RFQ', style_column)
        ws.write(0, 23, 'UBICACIÓN', style_column)
        ws.freeze_panes(1, 0)


        row = 1  # o la fila de inicio, si tienes cabecera
        for oc in records:
            for line in oc.order_line:
                approved_date_dt = Datetime.context_timestamp(self, oc.date_approve) if oc.date_approve else None
                naive_approved_date_dt = approved_date_dt.replace(tzinfo=None) if approved_date_dt else None

                local_dt = Datetime.context_timestamp(self, oc.create_date)
                naive_dt = local_dt.replace(tzinfo=None)

                request_name = line.purchase_request_lines[0].request_id.name if line.purchase_request_lines else ''
                account_analytic = line.distribution_analytic_account_ids[0] if line.distribution_analytic_account_ids else None
                account_analytic_name = account_analytic.name or '' if account_analytic else ''
                account_analytic_code = account_analytic.code or '' if account_analytic else ''

                ws.write(row, 0, naive_dt or '', style_date)
                ws.write(row, 1, naive_approved_date_dt if naive_approved_date_dt else None, style_date)
                ws.write(row, 2, oc.name or '', style_content) 
                ws.write(row, 3, line.product_id.display_name or '', style_content)
                ws.write(row, 4, line.product_id.categ_id.display_name or '', style_content)
                ws.write(row, 5, line.product_qty or '', style_number)
                ws.write(row, 6, line.product_uom.name or '', style_content)
                ws.write(row, 7, line.partner_id.name or '', style_content)
                ws.write(row, 8, request_name, style_content)
                ws.write(row, 9, account_analytic_code, style_content) 
                ws.write(row, 10, account_analytic_name, style_content)
                ws.write(row, 11, _ORDER_STATUS.get(oc.order_status, ''), style_content)
                ws.write(row, 12, oc.currency_id.name or '', style_content)
                ws.write(row, 13, oc.inverse_rate or '', style_number)
                ws.write(row, 14, line.price_unit or '', style_number)
                ws.write(row, 15, line.price_subtotal or '', style_number)
                ws.write(row, 16, line.price_tax or '', style_number)
                ws.write(row, 17, line.taxes_id[0].name if line.taxes_id else '', style_content)
                ws.write(row, 18, line.price_total or '', style_number)
                ws.write(row, 19, _OC_STATE.get(oc.state, ''), style_content)
                ws.write(row, 20, oc.payment_term_id.name or '', style_content)
                ws.write(row, 21, _RFQ_TYPE.get(oc.request_type, ''), style_content)
                ws.write(row, 22, _RFQ_CLASS.get(oc.classification_rfq, ''), style_content)
                ws.write(row, 23, oc.ubication_id.name or '', style_content)
                row += 1
