from odoo import fields, models, api
from num2words import num2words
from dateutil.relativedelta import relativedelta
from datetime import timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Contract'
    
    diferencia_meses = fields.Integer(string='Diferencia en Meses', compute='_compute_diferencia_fechas')
    diferencia_dias = fields.Integer(string='Diferencia en Días', compute='_compute_diferencia_fechas')
    
    dif_meses_text = fields.Char(string='Dif dias texto', compute='_compute_diferencia_fechas')
    dif_dias_text = fields.Char(string='Dif dias texto', compute='_compute_diferencia_fechas')

    date_signature = fields.Date(string='Fecha de Firma', default=fields.Date.today, required=True)
    date_signature_text = fields.Char(string='Fecha de Firma en texto', compute='_compute_date_signature_text')

    def _compute_diferencia_fechas(self):
        for record in self:
            if record.date_start and record.date_end:
                date_end_fake = record.date_end + timedelta(days=1)
                if record.date_start.day == 1 and date_end_fake.day == 1:
                    diferencia = relativedelta(record.date_end, record.date_start)
                    record.diferencia_meses = diferencia.years * 12 + diferencia.months + 1
                    record.diferencia_dias = 0
                    record.dif_meses_text = num2words(record.diferencia_meses, lang='es').lower()
                    record.dif_dias_text = num2words(record.diferencia_dias, lang='es').lower()
                
                else:
                    if record.date_start.month == record.date_end.month:
                        diferencia = relativedelta(record.date_end, record.date_start)
                        record.diferencia_meses = 0
                        record.diferencia_dias = diferencia.days + 1
                        record.dif_meses_text = num2words(record.diferencia_meses, lang='es').lower()
                        record.dif_dias_text = num2words(record.diferencia_dias, lang='es').lower()
                        
                    else:
                        diferencia = relativedelta(record.date_end, record.date_start)
                        record.diferencia_meses = diferencia.years * 12 + diferencia.months
                        record.diferencia_dias = diferencia.days
                        record.dif_meses_text = num2words(record.diferencia_meses, lang='es').lower()
                        record.dif_dias_text = num2words(record.diferencia_dias, lang='es').lower()
            else:
                record.diferencia_meses = 0
                record.diferencia_dias = 0

    @api.depends('date_signature')    
    def _compute_date_signature_text(self):
        for record in self:
            if record.date_signature:
                months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                          'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                
                month = record.date_signature.month

                dia = record.date_signature.day
                mes = months[month-1]
                año = record.date_signature.year

                texto = str(dia) + ' de ' + str(mes) + ' del ' + str(año)
                record.date_signature_text = texto
            else:
                record.date_signature_text = ''
                            
    