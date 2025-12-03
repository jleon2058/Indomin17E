from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging
_logger=logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_pe_is_detraction_line = fields.Boolean(string='Es apunte de detracción')

    @api.ondelete(at_uninstall=False)
    def _prevent_automatic_line_deletion(self):
        _logger.info("----buton prevent----")
        if not self.env.context.get('dynamic_unlink'):
            for line in self:
                # es línea de detracción, permitimos eliminarla
                if line.l10n_pe_is_detraction_line:
                    continue

                if line.display_type == 'tax' and line.move_id.line_ids.tax_ids:
                    raise ValidationError(
                        "No puede eliminar una línea de impuestos porque impactaría el reporte de impuestos"
                    )
                elif line.display_type == 'payment_term':
                    raise ValidationError(_(
                        "No puede eliminar una línea por pagar/por cobrar porque no sería consistente "
                        "con los términos de pago"
                    ))
