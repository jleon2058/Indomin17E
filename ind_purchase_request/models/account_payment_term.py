# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    advance_payment = fields.Boolean(
        string='Pago anticipado sin factura',
        help='Marcar si este término implica un pago anticipado antes de la emisión de factura.'
    )