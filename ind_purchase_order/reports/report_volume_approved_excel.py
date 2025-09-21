from odoo.tools.misc import xlsxwriter
from io import BytesIO
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone, UTC

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


class ReportVolumeApprovedExcel:
    def __init__(self, data, env):
        self.data = data
        self.env = env

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

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

        style_datetime = workbook.add_format({
            'font_size': 10,
            'num_format': 'dd/mm/yyyy hh:mm',
            'align': 'center',
        })

        ws = workbook.add_worksheet("Volumen de Compras Aprobadas")
        ws.set_column('A:A', 15)  # Correlativo de OC
        ws.set_column('B:B', 13)  # RUC del proveedor
        ws.set_column('C:C', 65)  # Razón Social del proveedor
        ws.set_column('D:D', 18)  # Clase de RFQ
        ws.set_column('E:E', 15)  # Ubicación
        ws.set_column('F:F', 15)  # Tipo de RFQ
        ws.set_column('G:G', 15)  # Estado de Pedido
        ws.set_column('H:H', 15)  # Fecha de Aprobación de la OC
        ws.set_column('I:I', 20)  # Condición de pago
        ws.set_column('J:J', 10)  # Tipo de Moneda
        ws.set_column('K:K', 10)  # Monto total de descuento
        ws.set_column('L:L', 10)  # Valor total

        # Encabezados
        ws.write(0, 0, 'Correlativo OC', style_column)
        ws.write(0, 1, 'RUC del proveedor', style_column)
        ws.write(0, 2, 'Razón social del proveedor', style_column)
        ws.write(0, 3, 'Clase de RFQ', style_column)
        ws.write(0, 4, 'Ubicación', style_column)
        ws.write(0, 5, 'Tipo de RFQ', style_column)
        ws.write(0, 6, 'Estado de Pedido', style_column)
        ws.write(0, 7, 'Fecha de Aprobación', style_column)
        ws.write(0, 8, 'Condición de pago', style_column)
        ws.write(0, 9, 'Tipo de Moneda', style_column)
        ws.write(0, 10, 'Descuento total', style_column)
        ws.write(0, 11, 'Valor total', style_column)
        ws.freeze_panes(1, 0)

        user_tz = self.env.user.tz or 'UTC'
        local_tz = timezone(user_tz)

        for i, oc in enumerate(self.data, start=1):
            total_discount = 0.00

            for line in oc.order_line:
                total_discount += round(((line.product_qty * line.price_unit) * (line.discount)/100),2)

            date_value = oc.date_approve
            if date_value:
                date_value = UTC.localize(date_value).astimezone(local_tz)
                date_value = date_value.replace(tzinfo=None)
            
            ws.write(i, 0, oc.name or '', style_content)
            ws.write(i, 1, oc.partner_id.vat or '', style_content)
            ws.write(i, 2, oc.partner_id.name or '', style_content)
            ws.write(i, 3, _RFQ_CLASS.get(oc.classification_rfq, ''), style_content)
            ws.write(i, 4, oc.ubication_id.name or '', style_content)
            ws.write(i, 5, _RFQ_TYPE.get(oc.request_type, ''), style_content)
            ws.write(i, 6, _ORDER_STATUS.get(oc.order_status, ''), style_content)
            ws.write(i, 7, date_value, style_datetime)
            ws.write(i, 8, oc.payment_term_id.name or '', style_content)
            ws.write(i, 9, oc.currency_id.name or '', style_content)
            ws.write(i, 10, total_discount, style_number)
            ws.write(i, 11, oc.amount_total or 0.00, style_number)

        workbook.close()
        output.seek(0)
        return output.read()
