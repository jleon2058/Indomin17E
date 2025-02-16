from odoo import models
import xlsxwriter
import logging
_logger = logging.getLogger(__name__)

class PartnerXlsx(models.AbstractModel):
    _name = 'report.ind_purchase_request.reporte_rfq'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rfq):
        sheet = workbook.add_worksheet()
        
        title_format=workbook.add_format({
            'bold':True,
            'bg_color':'#edece7',
            'border':1,
            'align':'center',
            'valign':'vcenter',
            'font_size':14
            })
        header_format_rfq=workbook.add_format({
            'bold':True,
            'bg_color': '#154f99',
            'border':1,
            'font_size':12,
            'align':'center',
            'font_color':'white',
        })
        header_format_oc=workbook.add_format({
            'bold':True,
            'bg_color':'#154f99',
            'border':1,
            'font_size':12,
            'align':'center',
            'font_color':'white',
        })
        header_format_ing=workbook.add_format({
            'bold':True,
            'bg_color':'#154f99',
            'border':1,
            'font_size':12,
            'align':'center',
            'font_color':'white',
        })
        header_format = workbook.add_format({
            'bold': True,
            'bg_color':'#ef7c23',
            'border': 1,
            'font_size': 12,
            'align': 'center',
            'text_wrap': True,
        })
        date_format=workbook.add_format({'num_format':'dd/mm/yy'})

        sheet.set_row(3,30)
        sheet.set_column('C:C',15)
        sheet.set_column('D:D',15)
        sheet.set_column('E:E',35)
        sheet.set_column('F:F',35)
        sheet.set_column('G:G',15)
        sheet.set_column('H:H',20)
        sheet.set_column('I:I',20)
        sheet.set_column('J:J',15)
        sheet.set_column('K:K',50)
        sheet.set_column('L:L',65)
        sheet.set_column('M:M',15)
        sheet.set_column('N:N',60)
        sheet.set_column('O:O',11)
        sheet.set_column('P:P',15)
        sheet.set_column('Q:Q',11)
        sheet.set_column('R:R',15)
        sheet.set_column('S:S',10)
        sheet.set_column('T:T',15)
        sheet.set_column('U:U',13)
        sheet.set_column('V:V',13)
        sheet.set_column('W:W',35)
        sheet.set_column('X:X',13)
        sheet.set_column('Y:Y',10)
        sheet.set_column('Z:Z',20)
        sheet.set_column('AA:AA',12)
        sheet.set_column('AB:AB',13)
        sheet.set_column('AC:AC',13)
        sheet.set_column('AD:AD',13)
        """ RFQ -
        Estado RFQ -
        Fecha de RFQ -
        Solicitado por -
        Aprobado por -
        Fecha de Aprobación -
        Descripción -
        Cant -
        Unidad de medida -
        Ce-co -
        Líneas de Orden de compra/Referencia del pedido
        Líneas de Orden de compra/Estado
        Líneas de Orden de compra/Creado por
        Estado de Pedido
        Líneas de Orden de compra/Referencia del pedido/Fecha confirmación
        Líneas de Orden de compra/Reserva/Estado
        Líneas de Orden de compra/Reserva/Cantidad hecha
        Líneas de Orden de compra/Reserva/Fecha programada """
        
        """ RFQ - 1
        Estado RFQ - 2
        Solicitado por - 3
        Aprobado por - 4
        Fecha de RFQ - 5
        Fecha de Aprobación - 6
        Tipo de RFQ - 7
        Producto - 8
        Descripción - 9
        Ce-co - 10
        Cant - 11
        Unidad de medida - 12
        Costo estimado - 13
        Estado de Pedido - 14
        Cant OC - 15 *
        Estado de compra - 16 *     
        Etiquetas analíticas *
        Proveedor preferido * """
        

        sheet.merge_range('A1:AD1','REPORTE DE RFQ - ORDEN DE COMPRA - INGRESOS',title_format)
        sheet.merge_range('A2:R2','RFQ',header_format_rfq)
        sheet.merge_range('S2:X2','ORDEN DE COMPRA',header_format_oc)
        sheet.merge_range('Y2:AD2','INGRESOS',header_format_ing)
        sheet.write(2,0,"N°",header_format)
        sheet.write(2,1,"LÍNEA DE RFQ",header_format)
        sheet.write(2,2,"RFQ",header_format)
        sheet.write(2,3,"ESTADO DE RFQ",header_format)
        sheet.write(2,4,"SOLICITANTE",header_format)
        sheet.write(2,5,"APROBADOR",header_format)
        sheet.write(2,6,"FECHA DE CREACIÓN RFQ",header_format)
        sheet.write(2,7,"FECHA DE APROBACIÓN", header_format)
        sheet.write(2,8,"TIPO DE RFQ",header_format)
        sheet.write(2,9,"REFERENCIA INTERNA",header_format)
        sheet.write(2,10,"PRODUCTO",header_format)
        sheet.write(2,11,"DESCRIPCIÓN",header_format)
        sheet.write(2,12,"REFERENCIA C.C.",header_format)
        sheet.write(2,13,"CENTRO DE COSTO",header_format)
        sheet.write(2,14,"CANTIDAD",header_format)
        sheet.write(2,15,"UNIDAD DE MEDIDA",header_format)
        sheet.write(2,16,"COSTO ESTIMADO",header_format)
        sheet.write(2,17,"ESTADO DE PEDIDO",header_format)
        sheet.write(2,18,"ID OC",header_format)
        sheet.write(2,19,"REFERENCIA OC",header_format)
        sheet.write(2,20,"ESTADO DE  OC", header_format)
        sheet.write(2,21,"CANTIDAD OC", header_format)
        sheet.write(2,22,"RESPONSABLE",header_format)
        sheet.write(2,23,"FECHA DE CREACIÓN",header_format)
        sheet.write(2,24,"ID INGRESO",header_format)
        sheet.write(2,25,"REFERENCIA INGRESO",header_format)
        sheet.write(2,26,"ESTADO DE INGRESO",header_format)
        sheet.write(2,27,"FECHA EFECTIVA",header_format)
        sheet.write(2,28,"CANTIDAD HECHA",header_format)
        sheet.write(2,29,"TIPO DE OPERACIÓN",header_format)
        """ sheet.write(2,25,"Fecha de Mov",header_format)
        sheet.write(2,26,"Cant Ing",header_format)
        sheet.write(2,27,"UMD en Ingreso",header_format)
        sheet.write(2,28,"Estado de Ingreso",header_format) """

        row=3

        Lista_id =()
        Lista_mov_id =()
        print(Lista_id)

        for request_line in rfq:
            if request_line.purchase_lines:
                cont2=0
                for order_line in request_line.purchase_lines:
                    cont1=0
                    if order_line.move_ids:
                        if all(sm.state in ["assigned","done","confirmed"] for sm in order_line.move_ids):
                            for picking_line in order_line.move_ids:
                                if picking_line.state in ["assigned", "done", "confirmed"] and picking_line.location_dest_id.usage=='internal':
                                    sheet.write(row, 0, int(row - 2))
                                    sheet.write(row, 1, request_line.id)
                                    sheet.write(row, 2, request_line.request_id.name)
                                    sheet.write(row, 3, request_line.request_state)
                                    sheet.write(row, 4, request_line.requested_by.name or "")
                                    sheet.write(row, 5, request_line.approved_by.name or "")
                                    sheet.write(row, 6, request_line.date_start or "", date_format)
                                    sheet.write(row, 7, request_line.date_approved or "",date_format)
                                    sheet.write(row, 8, request_line.request_type or "")
                                    sheet.write(row, 9, request_line.product_id.default_code or "")
                                    sheet.write(row, 10, request_line.product_id.name or "")
                                    sheet.write(row, 11, request_line.name or "")
                                    sheet.write(row, 12, request_line.account_analytic_id.code)
                                    sheet.write(row, 13, request_line.account_analytic_id.name)
                                    sheet.write(row, 14, request_line.product_qty or "")
                                    sheet.write(row, 15, request_line.product_uom_id.name or "")
                                    sheet.write(row, 16, request_line.estimated_cost or "")
                                    sheet.write(row, 17, request_line.order_status or "")
                                    """ if cont1==0 and cont2==0:
                                        sheet.write(row, 9, obj.product_qty)
                                    sheet.write(row, 10, obj.product_uom_id.name) """
                                    sheet.write(row, 18, order_line.id)
                                    sheet.write(row, 19, order_line.order_id.name or "")
                                    sheet.write(row, 20, order_line.order_id.state or "")
                                    sheet.write(row, 21, order_line.product_qty or "")
                                    sheet.write(row, 22, order_line.order_id.user_id.name or "")
                                    sheet.write(row, 23, order_line.order_id.date_approve or "",date_format)
                                    """ sheet.write(row, 16, rec.order_id.payment_term_id.name or "")
                                    sheet.write(row, 17, rec.order_id.state or "")
                                    if cont1==0:
                                        if rec.id in Lista_id:
                                            sheet.write(row,18,"")
                                        else:    
                                            sheet.write(row, 18, rec.product_qty)
                                    Lista_id=(*Lista_id,rec.id)
                                    sheet.write(row, 19, rec.product_uom.name)
                                    sheet.write(row, 20, rec.price_unit or "")
                                    sheet.write(row, 21, rec.discount or "")
                                    sheet.write(row, 22, rec.price_subtotal)
                                    sheet.write(row, 23, rec.currency_id.name or "") """
                                    if picking_line.state=='done':
                                        sheet.write(row, 24, picking_line.id)
                                        sheet.write(row, 25, picking_line.reference)
                                        sheet.write(row, 26, "Realizado")
                                        sheet.write(row, 27, picking_line.picking_id.date_done,date_format)
                                        if picking_line.id in Lista_mov_id:
                                            sheet.write(row, 28, "")
                                        else:
                                            sheet.write(row, 28, picking_line.product_uom_qty)
                                            """ if picking_line.location_dest_id.usage=='internal': """
                                            sheet.write(row, 29, 'Ingreso')
                                            """ else:
                                                sheet.write(row, 29, 'Salida') """
                                        Lista_mov_id=(*Lista_mov_id,picking_line.id)
                                    elif picking_line.state=='assigned':
                                        sheet.write(row, 24, picking_line.id)
                                        sheet.write(row, 25, picking_line.reference or "")
                                        sheet.write(row, 26, "Listo")
                                        sheet.write(row, 27, "")
                                        sheet.write(row, 28, "")
                                        sheet.write(row, 29, "")
                                    else:
                                        sheet.write(row, 24, picking_line.id)
                                        sheet.write(row, 25, picking_line.reference or "")
                                        sheet.write(row, 26, "Esperando")
                                        sheet.write(row, 27, "")
                                        sheet.write(row, 28, "")
                                        sheet.write(row, 29, "")
                                    row += 1
                                    cont1 +=1
                        else:
                            _logger.warning("-----ELSE----OC")
                            _logger.warning(order_line)
                            sheet.write(row, 0, int(row - 2))
                            sheet.write(row, 1, request_line.id)
                            sheet.write(row, 2, request_line.request_id.name)
                            sheet.write(row, 3, request_line.request_state)
                            sheet.write(row, 4, request_line.requested_by.name or "")
                            sheet.write(row, 5, request_line.approved_by.name or "")
                            sheet.write(row, 6, request_line.date_start or "", date_format)
                            sheet.write(row, 7, request_line.date_approved or "",date_format)
                            sheet.write(row, 8, request_line.request_type or "")
                            sheet.write(row, 9, request_line.product_id.default_code or "")
                            sheet.write(row, 10, request_line.product_id.name or "")
                            sheet.write(row, 11, request_line.name or "")
                            sheet.write(row, 12, request_line.account_analytic_id.code)
                            sheet.write(row, 13, request_line.account_analytic_id.name)
                            sheet.write(row, 14, request_line.product_qty or "")
                            sheet.write(row, 15, request_line.product_uom_id.name or "")
                            sheet.write(row, 16, request_line.estimated_cost or "")
                            sheet.write(row, 17, request_line.order_status or "")
                            """ if cont2==0 and cont1==0:
                                sheet.write(row, 9, obj.product_qty)
                            sheet.write(row, 10, obj.product_uom_id.name or "") """
                            sheet.write(row, 18, order_line.id)
                            sheet.write(row, 19, order_line.order_id.name or "")
                            sheet.write(row, 20, order_line.order_id.state or "")
                            sheet.write(row, 21, order_line.product_qty or "")
                            sheet.write(row, 22, order_line.order_id.user_id.name or "")
                            sheet.write(row, 23, order_line.order_id.date_approve or "",date_format)
                            """ sheet.write(row, 23, order_line.order_id.payment_term_id.name or "")
                            sheet.write(row, 17, order_line.order_id.state or "")
                            if cont2==0 and cont1==0:
                                if order_line.id in Lista_id:
                                    sheet.write(row,18,"")
                                else:    
                                    sheet.write(row, 18, order_line.product_qty)
                            Lista_id=(*Lista_id,order_line.id)
                            sheet.write(row, 19, order_line.product_uom.name)
                            sheet.write(row, 20, order_line.price_unit or "")
                            sheet.write(row, 21, order_line.discount or "")
                            sheet.write(row, 22, order_line.price_subtotal)
                            sheet.write(row, 23, order_line.currency_id.name) """
                            sheet.write(row, 24, "")
                            sheet.write(row, 25, "")
                            sheet.write(row, 26, "")
                            sheet.write(row, 27, "")
                            sheet.write(row, 28, "")
                            sheet.write(row, 29, "")
                            row += 1
                        cont2 +=1
                    else:
                        _logger.warning("-----ELSE----OC_move_id---")
                        _logger.warning(order_line)
                        sheet.write(row, 0, int(row - 2))
                        sheet.write(row, 1, request_line.id)
                        sheet.write(row, 2, request_line.request_id.name)
                        sheet.write(row, 3, request_line.request_state)
                        sheet.write(row, 4, request_line.requested_by.name or "")
                        sheet.write(row, 5, request_line.approved_by.name or "")
                        sheet.write(row, 6, request_line.date_start or "", date_format)
                        sheet.write(row, 7, request_line.date_approved or "",date_format)
                        sheet.write(row, 8, request_line.request_type or "")
                        sheet.write(row, 9, request_line.product_id.default_code or "")
                        sheet.write(row, 10, request_line.product_id.name or "")
                        sheet.write(row, 11, request_line.name or "")
                        sheet.write(row, 12, request_line.account_analytic_id.code)
                        sheet.write(row, 13, request_line.account_analytic_id.name)
                        sheet.write(row, 14, request_line.product_qty or "")
                        sheet.write(row, 15, request_line.product_uom_id.name or "")
                        sheet.write(row, 16, request_line.estimated_cost or "")
                        sheet.write(row, 17, request_line.order_status or "")
                        """ if cont2==0 and cont1==0:
                            sheet.write(row, 9, obj.product_qty)
                        sheet.write(row, 10, obj.product_uom_id.name or "") """
                        sheet.write(row, 18, order_line.id)
                        sheet.write(row, 19, order_line.order_id.name or "")
                        sheet.write(row, 20, order_line.order_id.state or "")
                        sheet.write(row, 21, order_line.product_qty or "")
                        sheet.write(row, 22, order_line.order_id.user_id.name or "")
                        sheet.write(row, 23, order_line.order_id.date_approve or "",date_format)
                        """ sheet.write(row, 23, order_line.order_id.payment_term_id.name or "")
                        sheet.write(row, 17, order_line.order_id.state or "")
                        if cont2==0 and cont1==0:
                            if order_line.id in Lista_id:
                                sheet.write(row,18,"")
                            else:    
                                sheet.write(row, 18, order_line.product_qty)
                        Lista_id=(*Lista_id,order_line.id)
                        sheet.write(row, 19, order_line.product_uom.name)
                        sheet.write(row, 20, order_line.price_unit or "")
                        sheet.write(row, 21, order_line.discount or "")
                        sheet.write(row, 22, order_line.price_subtotal)
                        sheet.write(row, 23, order_line.currency_id.name) """
                        sheet.write(row, 24, "")
                        sheet.write(row, 25, "")
                        sheet.write(row, 26, "")
                        sheet.write(row, 27, "")
                        sheet.write(row, 28, "")
                        sheet.write(row, 29, "")
                        row +=1
                        cont2 +=1
            else:
                sheet.write(row, 0, int(row - 2))
                sheet.write(row, 1, request_line.id)
                sheet.write(row, 2, request_line.request_id.name)
                sheet.write(row, 3, request_line.request_state)
                sheet.write(row, 4, request_line.requested_by.name or "")
                sheet.write(row, 5, request_line.approved_by.name or "")
                sheet.write(row, 6, request_line.date_start or "", date_format)
                sheet.write(row, 7, request_line.date_approved or "",date_format)
                sheet.write(row, 8, request_line.request_type or "")
                sheet.write(row, 9, request_line.product_id.default_code or "")
                sheet.write(row, 10, request_line.product_id.name or "")
                sheet.write(row, 11, request_line.name or "")
                sheet.write(row, 12, request_line.account_analytic_id.code)
                sheet.write(row, 13, request_line.account_analytic_id.name)
                sheet.write(row, 14, request_line.product_qty or "")
                sheet.write(row, 15, request_line.product_uom_id.name or "")
                sheet.write(row, 16, request_line.estimated_cost or "")
                sheet.write(row, 17, request_line.order_status or "")
                sheet.write(row, 18, "")
                sheet.write(row, 19, "")
                sheet.write(row, 20, "")
                sheet.write(row, 21, "")
                sheet.write(row, 22, "")
                sheet.write(row, 23, "")
                sheet.write(row, 24, "")
                sheet.write(row, 25, "")
                sheet.write(row, 26, "")
                sheet.write(row, 27, "")
                sheet.write(row, 28, "")
                sheet.write(row, 29, "")
                """ sheet.write(row, 29, "")
                sheet.write(row, 30, "")
                sheet.write(row, 31, "")
                sheet.write(row, 32, "")
                sheet.write(row, 33, "") """

                row += 1
            # Añadir una fila en blanco entre objetos
            # row+=1
        row += 1
