import xlsxwriter
import calendar
import base64
from datetime import datetime,date,timedelta
from io import BytesIO
from odoo import models,fields,api, _,tools
from .formats import Cellformato
from .sql_queries import SQLQueries
import locale
import logging
logger = logging.getLogger(__name__)

class Cencos(models.TransientModel):
    _name = 'ind.cencos'

    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    file_data = fields.Binary('File', readonly=True)

    def genera_reporte_cencos(self):
        pass