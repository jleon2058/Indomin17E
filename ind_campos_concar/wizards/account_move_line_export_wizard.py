from odoo import models, fields
import io
import base64
from odoo.tools.misc import xlsxwriter
from lxml import etree
from odoo.exceptions import UserError
 

class AccountMoveLineExportWizard(models.TransientModel):
    _name = 'account.move.line.export.wizard'
    _description = 'Exportar Movimientos de Cuenta'

    date_filter_i = fields.Date(string="Fecha de inicio")
    date_filter_s = fields.Date(string="Fecha de fin")

    state_filter = fields.Selection(
        [('draft', 'Borrador'), ('posted', 'Publicado')],
        string="Estado"
    )
    journal_filter = fields.Many2one('account.journal', string="Diario")
    
    def _generate_excel_file(self, data):
    # Obtener campos del tree view
      tree_view = self.env['ir.ui.view'].search([
          ('model', '=', 'account.move.line'),
          ('type', '=', 'tree')
      ], limit=1)

      if not tree_view:
          raise UserError("No se encontró la vista tipo 'tree' para el modelo 'account.move.line'.")

      try:
          tree_fields = [
            field.get('name') 
            for field in etree.fromstring(tree_view.arch).xpath("//field")
          ]
      except Exception as e:
          raise UserError(f"Error al procesar la vista tipo 'tree': {e}")

      # Crear el archivo Excel
      output = io.BytesIO()
      workbook = xlsxwriter.Workbook(output)
      worksheet = workbook.add_worksheet("Movimientos de Cuenta")

    # Escribir encabezados
      for col, header in enumerate(tree_fields):
          worksheet.write(0, col, header)

    # Escribir datos
      row = 1
      for line in data:
          for col, field_name in enumerate(tree_fields):
              field_obj = self.env['account.move.line']._fields.get(field_name)
              value = getattr(line, field_name, '')

            # Si el campo es una relación (Many2one), mostrar el nombre
              if isinstance(field_obj, fields.Many2one):
                  value = value.display_name if value else ''
              elif isinstance(field_obj, fields.One2many) or isinstance(field_obj, fields.Many2many):
                  value = ', '.join(value.mapped('display_name')) if value else ''

              worksheet.write(row, col, str(value) if value else '')
          row += 1

      workbook.close()
      output.seek(0)
    
      return output.getvalue()

    def action_export_excel(self):
      data = self._get_filtered_data()
      excel_data = self._generate_excel_file(data)

      file_data = base64.b64encode(excel_data)

      attachment = self.env['ir.attachment'].create({
          'name': 'Reporte_Apuntes_Contables:.xlsx',
          'datas': file_data,
          'type': 'binary',
      })

      return {
          'type': 'ir.actions.act_url',
          'url': '/web/content/%s?download=true' % attachment.id,
          'target': 'self',
      }
    
    def action_export_modified_excel(self):
      data = self._get_filtered_data()

    # Crear el archivo Excel
      output = io.BytesIO()
      workbook = xlsxwriter.Workbook(output)
      worksheet = workbook.add_worksheet("Movimientos Modificados")

    # Obtener campos del tree view
      tree_view = self.env['ir.ui.view'].search([
          ('model', '=', 'account.move.line'),
          ('type', '=', 'tree')
      ], limit=1)

      if not tree_view:
          raise UserError("No se encontró la vista tipo 'tree' para el modelo 'account.move.line'.")

      try:
          tree_fields = [field.get('name') for field in etree.fromstring(tree_view.arch).xpath("//field")]
      except Exception as e:
          raise UserError(f"Error al procesar la vista tipo 'tree': {e}")

      
      rates = self.env['res.currency.rate'].search([('currency_id', '=', 'USD')], order="name DESC")
      rate_dict = {rate.name.strftime('%d/%m/%Y'): rate.inverse_company_rate for rate in rates}
      
      grouped_data = {}
      
      for line in data:
    
        # Columna "Sub diario"
          sub_diario = ''
          num_comprobante = ''
          fecha_comprobante = ''
          tipo_factura = ''
          num_factura = ''
          fecha_factura = ''
          cod_moneda = ''
          glosa = ''
          tipo_cambio = ''
          fecha_vencimiento = ''
          flag = 'S'
          cuenta_contable = ''
          codigo_anexo = ''
          codigo_costo = ''
          dh = ''
          importe = ''
          igv = ''
          glosa_d = ''

          if line.move_id and getattr(line.move_id, 'seat_number', False):
              sub_diario = line.move_id.seat_number.split('-')[0]
              num_comprobante = line.move_id.seat_number.split('-')[1]
          if line.move_id and getattr(line.move_id, 'date', False):
              fecha_comprobante = line.move_id.date.strftime('%d/%m/%Y')
          if line.move_id and getattr(line.move_id, 'invoice_date', False):
              fecha_factura = line.move_id.invoice_date.strftime('%d/%m/%Y')    
          if line.move_id and getattr(line.move_id, 'currency_id', False):
              if line.move_id.currency_id.name == 'PEN':
                cod_moneda = 'MN'
              elif line.move_id.currency_id.name == 'USD':
                cod_moneda = 'US'
              else:
                cod_moneda = line.move_id.currency_id.name
          if line.move_id and getattr(line.move_id, 'ref', False):
              glosa = line.move_id.ref
          if line.move_id and getattr(line.move_id, 'l10n_latam_document_type_id', False):
             if line.move_id.l10n_latam_document_type_id.internal_type == 'credit_note':
                 tipo_cambio = float(line.move_id.exchange_rate)
             else:
                 tipo_cambio = rate_dict.get(fecha_factura, '')
                 if not tipo_cambio and rate_dict:
                    closest_date = max(rate_dict.keys())  # Última fecha disponible
                    tipo_cambio = rate_dict[closest_date] 

          if fecha_comprobante == '' or fecha_factura == '':
              tipo_conversion = ''
          elif fecha_comprobante == fecha_factura:
              tipo_conversion = 'V'
          else:
              tipo_conversion = 'C'

          if line.move_id and getattr(line.move_id, 'name', False):
             partes = line.move_id.name.split(' ')  
             tipo_factura = partes[0] if len(partes) > 0 else ''
             num_factura = partes[1] if len(partes) > 1 else ''

          if line.move_id and getattr(line.move_id, 'invoice_date_due', False):
              fecha_vencimiento = line.move_id.invoice_date_due.strftime('%d/%m/%Y') if line.move_id.invoice_date_due else ''      
          
          if line.account_id and getattr(line.account_id, 'code', False):
              cuenta_contable = line.account_id.code

          if line.partner_id and getattr(line.partner_id, 'vat', False):
              codigo_anexo = line.partner_id.vat  
          
          if line.analytic_distribution:
             analytic_ids = list(line.analytic_distribution.keys())
             analytic_accounts = self.env['account.analytic.account'].browse(int(analytic_ids[0]))
             if line.account_id.group_id.name != 'COMPRAS' and analytic_accounts[0].concar_id:
                codigo_costo = analytic_accounts[0].concar_id

          if float(line.debit) == 0 and float(line.credit) != 0:
              dh = 'H'
          if float(line.debit) != 0 and float(line.credit) == 0:
              dh = 'D'
          
          importe = abs(float(line.amount_currency))
          
          if line.tax_line_id and getattr(line.tax_line_id, 'amount', False):
              igv = line.tax_line_id.amount

            
          if line.move_id.invoice_line_ids:
             first_line = line.move_id.invoice_line_ids[0]  # Obtener la primera línea
             if getattr(first_line, 'purchase_order_id', False):
                glosa_d = first_line.purchase_order_id.name
              
          if line.stock_move_id and getattr(line.stock_move_id, 'reference', False):
                glosa_d = glosa_d + ' ' + line.stock_move_id.reference
          
          if not line.is_target_move_line:
            key = (sub_diario, num_comprobante, fecha_comprobante,
                 tipo_factura, num_factura, fecha_factura, cod_moneda,
                 glosa, tipo_cambio, tipo_conversion, fecha_vencimiento,
                 flag, cuenta_contable, codigo_anexo, codigo_costo,
                 dh, igv, glosa_d)
      
            if key in grouped_data:
               grouped_data[key] += importe
            else:
               grouped_data[key] = importe      
      
      worksheet.write(0, 0, "Sub Diario")#1
      worksheet.write(0, 1, "Numero de Comprobante")#2
      worksheet.write(0, 2, "Fecha de Comprobante")#3
      worksheet.write(0, 3, "Codigo de Moneda")#4
      worksheet.write(0, 4, "Glosa Principal")#5
      worksheet.write(0, 5, "Tipo de Cambio")#6
      worksheet.write(0, 6, "Tipo de Conversión")#7
      worksheet.write(0, 7, "Flag de Conversión de Moneda")#8
      worksheet.write(0, 8, "Cuenta Contable")#9
      worksheet.write(0, 9, "Código de Anexo")#10
      worksheet.write(0, 10, "Código de Centro de Costo")#11
      worksheet.write(0, 11, "Debe/Haber")#12
      worksheet.write(0, 12, "Importe Original")#13  //
      worksheet.write(0, 13, "Tipo de Documento")#14
      worksheet.write(0, 14, "Numero de Documento")#15
      worksheet.write(0, 15, "Fecha de Documento")#16
      worksheet.write(0, 16, "Fecha de Vencimiento")#17
      worksheet.write(0, 17, "Tasa IGV")#19
      worksheet.write(0, 18, "Glosa Detalle")#18   //
      
      row = 1
      for key, importe in grouped_data.items():
         if row == 1:
           cos = key[1] 
           glo = key[17] 
         worksheet.write(row, 0, key[0])
         worksheet.write(row, 1, key[1])
         worksheet.write(row, 2, key[2])
         worksheet.write(row, 3, key[6])
         worksheet.write(row, 4, key[7])
         worksheet.write(row, 5, key[8])
         worksheet.write(row, 6, key[9])
         worksheet.write(row, 7, key[11])
         worksheet.write(row, 8, key[12])
         worksheet.write(row, 9, key[13])
         worksheet.write(row, 10, key[14])
         worksheet.write(row, 11, key[15])
         worksheet.write(row, 12, importe)
         worksheet.write(row, 13, key[3])
         worksheet.write(row, 14, key[4])
         worksheet.write(row, 15, key[5])
         worksheet.write(row, 16, key[10])
         worksheet.write(row, 17, key[16])
         if cos == key[1]:
            #if key[17] == '':
            worksheet.write(row, 18, glo) 
            #else:
            #    worksheet.write(row, 17, key[17])      
         else:
            cos = key[1]
            glo = key[17]  
            worksheet.write(row, 18, key[17])
         #worksheet.write(row, 17, key[17])
         #worksheet.write(row, 19, key[18])
         row += 1

      workbook.close()
      output.seek(0)

      file_data = base64.b64encode(output.getvalue())  

      attachment = self.env['ir.attachment'].create({
          'name': 'Apuntes_Contables.xlsx',
          'datas': file_data,
          'type': 'binary',
      })

      return {
          'type': 'ir.actions.act_url',
          'url': '/web/content/%s?download=true' % attachment.id,
          'target': 'self',
      }
    
    
    def _get_filtered_data(self):
        domain = []
        if self.date_filter_i:
            domain.append(('date', '>=', self.date_filter_i))
        if self.date_filter_s:
            domain.append(('date', '<=', self.date_filter_s))
        if self.state_filter:
            domain.append(('move_id.state', '=', self.state_filter))
        if self.journal_filter:
            domain.append(('journal_id', '=', self.journal_filter.id))

        return self.env['account.move.line'].search(domain)
