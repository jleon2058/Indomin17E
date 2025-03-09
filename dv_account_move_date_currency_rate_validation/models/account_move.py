from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def currency_rate_move_date_domain(self):
        self.ensure_one()
        move_currency_id = self.currency_id.id
  
        if self.move_type == 'entry' or not self.invoice_date:
            move_date = self.date
        else:
            move_date = self.invoice_date
   
        domain = [
                    ('currency_id','=', move_currency_id),
                    ('name','=', move_date)
        ]
        return domain

    def validate_currency_rate(self):
        for record in self:
            if record.currency_id.id != record.company_id.currency_id.id:
                currency_rate_obj = self.env['res.currency.rate']
                
                domain = record.currency_rate_move_date_domain()
                currency_rate_move_date = currency_rate_obj.search(domain)
                if not currency_rate_move_date:
                    raise ValidationError(_(f'No se ha encontrado tipo de cambio a la fecha para el asiento: {record.name}'))


    def _post(self, soft=True):
        self.validate_currency_rate()
        return super()._post(soft)