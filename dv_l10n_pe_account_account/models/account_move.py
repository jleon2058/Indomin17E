from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
import json
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_pe_in_edi_serie = fields.Char(string='Serie', copy=False)
    l10n_pe_in_edi_number = fields.Char(string='N°', copy=False)

    @api.onchange('l10n_pe_in_edi_number')
    def _onchange_l10n_pe_in_edi_number(self):
        l10n_pe_in_edi_number = self.l10n_pe_in_edi_number
        if l10n_pe_in_edi_number:
            self.l10n_pe_in_edi_number = l10n_pe_in_edi_number.zfill(8)
        else:
            self.l10n_pe_in_edi_number = l10n_pe_in_edi_number

    @api.depends('name', 'l10n_pe_in_edi_serie', 'l10n_pe_in_edi_number')
    def _compute_l10n_latam_document_number(self):
        recs_with_name = self.filtered(lambda x: x.name != '/')
        _logger.info("recs_with_name")
        _logger.info(recs_with_name)
        for rec in recs_with_name:
            name = rec.name
            _logger.info("name")
            _logger.info(name)
            if rec.l10n_pe_in_edi_serie and rec.l10n_pe_in_edi_number:
                new_name = f"{rec.l10n_pe_in_edi_serie}-{rec.l10n_pe_in_edi_number}"
            else:
                new_name = False
            doc_code_prefix = rec.l10n_latam_document_type_id.doc_code_prefix
            _logger.info("doc_code_prefix")
            _logger.info(doc_code_prefix)
            if doc_code_prefix and name:
                name = name.split(" ", 1)[-1]
                _logger.info("name split")
                _logger.info(name)
            if new_name and name != new_name:
                _logger.info("new_name")
                _logger.info(new_name)
                name = new_name
            rec.l10n_latam_document_number = name
        remaining = self - recs_with_name
        _logger.info("remaining")
        _logger.info(remaining)
        for rem in remaining:
            if rem.l10n_pe_in_edi_serie and rem.l10n_pe_in_edi_number:
                rem.l10n_latam_document_number = f"{rem.l10n_pe_in_edi_serie}-{rem.l10n_pe_in_edi_number}"
            else:
                rem.l10n_latam_document_number = False