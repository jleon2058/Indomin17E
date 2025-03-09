from odoo import api, fields, models


class DetractionTable(models.Model):
    _name = 'l10n_pe_detraction.table'
    _description = 'Tabla de detracciones'
    _sql_constraints = [
        ('code_annex_number_uniq', 'unique (code,annex_number)',
         'El código debe ser único por anexo')
    ]

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
    annex_number = fields.Selection([
        ('annex_one', 'Anexo I'),
        ('annex_two', 'Anexo II'),
        ('annex_three', 'Anexo III'),
    ], string='Anexo', required=True)

    percent = fields.Float(string='Porcentaje')

    def name_get(self):
        res = []
        for record in self:
            complete_name = f"{record.code}: {record.name}"
            res.append((record.id, complete_name))
        return res
