import base64
import xlrd  # para archivos .xls
from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequestImportLine(models.TransientModel):
    _name = 'purchase.request.import.line'
    _description = 'Importar líneas de requerimiento'

    file = fields.Binary(string='Archivo Excel', required=True)
    purchase_request_id = fields.Many2one('purchase.request', string='Requerimiento', required=True, readonly=True)

    def import_lines(self):
        data = base64.b64decode(self.file)
        book = xlrd.open_workbook(file_contents=data)
        sheet = book.sheet_by_index(0)

        for row in range(1, sheet.nrows):
            product_name = sheet.cell(row, 0).value
            qty = sheet.cell(row, 1).value
            #account_analytic_name = sheet.cell(row, 2).value

            product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
            #account_analytic = self.env['account.analytic.account'].search([('name', '=', account_analytic_name)], limit=1)
            
            #if not product or not account_analytic:
            if not product:
               continue

            if not self.purchase_request_id.classification_rfq:
               raise UserError("!!!!!Clase de RFQ no seleccionada")
            if not self.purchase_request_id.ubication_id:
               raise UserError("!!!!!Ubicacion no seleccionada")
            # Validaciones múltiples sobre líneas existentes
            rest1 = self.purchase_request_id.classification_rfq == product.categ_id.classification_rfq 

            #if rest1 and rest2 and qty>0:
            if rest1 and qty>0:    
               self.env['purchase.request.line'].create({
                  'request_id': self.purchase_request_id.id,
                  'product_id': product.id,
                  'product_qty': qty,
                  'product_uom_id': product.uom_id.id,
                  'description': product.name,
                  #'analytic_account_id': account_analytic.id,
               })
