from odoo import models, fields, api
import base64
import io
import xlsxwriter
import logging
import re
from odoo.exceptions import UserError, ValidationError
from urllib.parse import quote
logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    #1. Documentacion Personal
    has_worker_dni_copy = fields.Boolean(string="Copia de DNI vigente del trabajador")
    worker_dni_expiration_date = fields.Date(string="Fecha de vencimiento del DNI")

    @api.onchange('has_worker_dni_copy')
    def _onchange_has_worker_dni_copy(self):
        self.ensure_one()
        if not self.has_worker_dni_copy:
            self.worker_dni_expiration_date = False

    has_family_dni_copy = fields.Boolean(string="Copia de DNI de hijos y/o cónyuge")
    has_address_proof_copy = fields.Boolean(string="Copia de recibo de servicios (domicilio actualizado)")
    has_id_photo = fields.Boolean(string="Fotografía tamaño carnet (opcional)")
    has_indomin_data_sheet = fields.Boolean(string="Ficha de Datos Indomin / Mecaparts")
    has_vida_ley_doc = fields.Boolean(string="Documento de Vida Ley Legalizado")
    has_domicile_affidavit = fields.Boolean(string="Declaración Jurada de Domicilio")
    has_fifth_income_statement = fields.Boolean(string="Declaración de Renta de Quinta")

    has_driver_license_copy = fields.Boolean(string="Copia de brevete o licencia de conducir (si aplica)")
    driver_license_category = fields.Char(string="Categoría del brevete")
    driver_license_expiration_date = fields.Date(string="Fecha de vencimiento del brevete")

    @api.onchange('has_driver_license_copy')
    def _onchange_has_driver_license_copy(self):
        self.ensure_one()
        if not self.has_driver_license_copy:
            self.driver_license_category = False
            self.driver_license_expiration_date = False

    #2. Documentacion Laboral
    has_signed_contract = fields.Boolean(string="Contrato de trabajo firmado")
    has_cv = fields.Boolean(string="Hoja de vida (CV) actualizada y documentada")
    has_truth_affidavit = fields.Boolean(string="Declaración jurada de veracidad de la información")
    has_criminal_background = fields.Boolean(string="Antecedentes penales/policiales (opcional)")
    has_personal_data_sheet = fields.Boolean(string="Ficha de datos personales")
    has_starsoft_registration = fields.Boolean(string="Constancia de Alta en STARSOFT")

    #3. Obligaciones Legales del Empleador
    has_t_registry_registration = fields.Boolean(string="Registro en T-Registro (SUNAT)")
    has_pension_system_selection = fields.Boolean(string="Elección del sistema previsional (ONP o AFP)")
    has_sctr_coverage = fields.Boolean(string="Registro y cobertura del SCTR (si aplica)")
    has_contract_submission_mtpe = fields.Boolean(string="Remisión del contrato al MTPE (si es plazo fijo)")
    has_electronic_payslips = fields.Boolean(string="Entrega de boletas de pago electrónicas")
    has_salary_band_registration = fields.Boolean(string="Registro de la banda salarial del puesto")
    has_salary_scale_delivery = fields.Boolean(string="Entrega de la escala salarial y criterios de pago")

    #4. Seguridad y Salud en el Trabajo
    has_medical_exam_entry = fields.Boolean(string="Examen médico ocupacional de ingreso")
    medical_exam_start_date = fields.Date(string="Fecha de inicio del examen médico")
    medical_exam_expiry_date = fields.Date(string="Fecha fin de vigencia del examen médico")

    @api.onchange('has_medical_exam_entry')
    def _onchange_has_medical_exam_entry(self):
        self.ensure_one()
        if not self.has_medical_exam_entry:
            self.medical_exam_start_date = False
            self.medical_exam_expiry_date = False

    has_isem_exam = fields.Boolean(string="Examen ISEM (si aplica)")
    isem_exam_start_date = fields.Date(string="Fecha de inicio del examen ISEM")
    isem_exam_expiry_date = fields.Date(string="Fecha fin de vigencia del examen ISEM")

    @api.onchange('has_isem_exam')
    def _onchange_has_isem_exam(self):
        self.ensure_one()
        if not self.has_isem_exam:
            self.isem_exam_start_date = False
            self.isem_exam_expiry_date = False

    has_driving_test = fields.Boolean(string="Examen de manejo (si aplica)")
    driving_test_start_date = fields.Date(string="Fecha de inicio del examen de manejo")
    driving_test_expiry_date = fields.Date(string="Fecha fin de vigencia del examen de manejo")

    @api.onchange('has_driving_test')
    def _onchange_has_driving_test(self):
        self.ensure_one()
        if not self.has_driving_test:
            self.driving_test_start_date = False
            self.driving_test_expiry_date = False

    has_rit_delivery = fields.Boolean(string="Entrega y firma del RIT (si aplica)")
    has_sst_policy_delivery = fields.Boolean(string="Entrega y firma de la Política de SST")
    has_sst_training = fields.Boolean(string="Capacitación en SST (firma de asistencia)")
    has_epp_delivery_ack = fields.Boolean(string="Entrega de EPP y firma de conformidad")


    #5. Prevencion del Hostigamiento Sexual Laboral
    has_harassment_protocol_delivery = fields.Boolean(string="Entrega de protocolo contra hostigamiento sexual")
    has_protocol_receipt_ack = fields.Boolean(string="Firma de constancia de recepción del protocolo")
    has_harassment_prevention_training = fields.Boolean(string="Capacitación en prevención del hostigamiento")
    has_rit_protocol_inclusion = fields.Boolean(string="Inclusión del protocolo en el RIT (si existe)")

    #6. Otros Documentos Recomendables
    has_welcome_letter = fields.Boolean(string="Carta de bienvenida o designación formal del puesto")
    has_job_description = fields.Boolean(string="Manual de funciones y responsabilidades (MOF)")
    has_confidentiality_agreement = fields.Boolean(string="Pacto de confidencialidad y/o no competencia (si aplica)")
    has_tools_delivery_receipt = fields.Boolean(string="Constancia de entrega de herramientas o recursos")


    #7. Documentos de Salida del trabajador
    has_resignation_letter = fields.Boolean(string="Carta de renuncia firmada (si aplica)")
    has_sunat_deregistration = fields.Boolean(string="Registro de baja en SUNAT (T-Registro)")
    has_resignation_acceptance = fields.Boolean(string="Carta de aceptación de renuncia o cese o Correo de aceptación de Jefatura")
    has_social_benefits_liquidation = fields.Boolean(string="Liquidación de beneficios sociales firmada")
    has_work_certificate = fields.Boolean(string="Certificado de trabajo emitida")
    has_cts_release_cert = fields.Boolean(string="Constancia de Liberación de CTS")
    has_final_fifth_income_cert = fields.Boolean(string="Constancia de Renta de Quinta (Si aplica)")
    has_epp_return_act = fields.Boolean(string="Acta de devolución de EPP y herramientas")
    has_final_file_archive = fields.Boolean(string="Archivo final del legajo laboral")

    audit_user_id = fields.Many2one('res.users', string="Auditado por")
    audit_date = fields.Date(string="Fecha de auditoría")
    audit_notes = fields.Html(string="Observaciones")

    has_audit = fields.Boolean(string="Tiene auditoria")


    def action_report_document_checklist(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Reporte de documentos")

        # Formatos
        bold = workbook.add_format({'bold': True})
        yes_format = workbook.add_format({'font_color': '#006100'})
        no_format = workbook.add_format({'font_color': '#9C0006'})

        # Campos booleanos definidos
        fields_to_report = [
            'has_worker_dni_copy', 'has_family_dni_copy', 'has_address_proof_copy',
            'has_id_photo', 'has_indomin_data_sheet', 'has_vida_ley_doc',
            'has_domicile_affidavit', 'has_fifth_income_statement',
            'has_driver_license_copy', 'has_signed_contract', 'has_cv',
            'has_truth_affidavit', 'has_criminal_background', 'has_personal_data_sheet',
            'has_starsoft_registration', 'has_t_registry_registration',
            'has_pension_system_selection', 'has_sctr_coverage',
            'has_contract_submission_mtpe', 'has_electronic_payslips',
            'has_salary_band_registration', 'has_salary_scale_delivery',
            'has_medical_exam_entry', 'has_isem_exam', 'has_driving_test',
            'has_rit_delivery', 'has_sst_policy_delivery', 'has_sst_training',
            'has_epp_delivery_ack', 'has_harassment_protocol_delivery',
            'has_protocol_receipt_ack', 'has_harassment_prevention_training',
            'has_rit_protocol_inclusion', 'has_welcome_letter', 'has_job_description',
            'has_confidentiality_agreement', 'has_tools_delivery_receipt',
            'has_resignation_letter', 'has_sunat_deregistration',
            'has_resignation_acceptance', 'has_social_benefits_liquidation',
            'has_work_certificate', 'has_cts_release_cert',
            'has_final_fifth_income_cert', 'has_epp_return_act',
            'has_final_file_archive',
        ]
        
        # Determinar ancho de columna "Empleado"
        max_name_length = max((len(employee.name or f"ID {employee.id}") for employee in self), default=20)
        worksheet.set_column(0, 1, max_name_length + 2)

        # Encabezados
        headers = ['N° de Identificación','Empleado'] + [self._fields[f].string for f in fields_to_report]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, bold)

        # Datos
        row = 1
        for employee in self:
            worksheet.write(row, 0, employee.identification_id or f"No establecido", bold)
            worksheet.write(row, 1, employee.name or f"ID {employee.id}", bold)
            for col_num, field_name in enumerate(fields_to_report, start=2):
                value = getattr(employee, field_name)
                display_value = '✅' if value else ''
                cell_format = yes_format if value else no_format
                worksheet.write(row, col_num, display_value, cell_format)
            row += 1

        workbook.close()
        output.seek(0)

        file_data = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': 'Reporte de documentos.xlsx',
            'type': 'binary',
            'datas': file_data,
            'res_model': 'hr.employee',
            'res_id': self[0].id if len(self) == 1 else False,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _get_folder_url(self, enable_key, path_key, mod_key):
        self.ensure_one()

        enable = self.env['ir.config_parameter'].sudo().get_param(enable_key)
        if not enable:
            raise UserError(f"La opción para abrir la carpeta está desactivada.")

        path = self.env['ir.config_parameter'].sudo().get_param(path_key)
        if not path:
            raise UserError(f"La ruta configurada para documentos no es una URL válida.")

        if not self.identification_id or not self.name:
            raise ValidationError("No se puede generar la ruta: el empleado debe tener asignado un número de identificación y un nombre.")

        folder_name = f"{self.identification_id}_{self.name}".replace(' ', '_')
        encoded_folder = quote(folder_name)

        include_company = self.env['ir.config_parameter'].sudo().get_param(mod_key)
        if include_company:
            company_clean_name = re.sub(r'[^A-Za-z0-9_]', '', self.company_id.name.replace(' ', '_'))
            company_folder = quote(company_clean_name)
            url = f"{path}%2F{company_folder}%2F{encoded_folder}"
        else:
            url = f"{path}%2F{encoded_folder}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
        

    def action_open_employee_folder(self):
        return self._get_folder_url(
            enable_key='hr_checklist.enable_employee_docs',
            path_key='hr_checklist.employee_docs_path',
            mod_key='hr_checklist.include_company_employee_docs_path'
        )
    

    def action_register_audit(self):
        self.ensure_one()
        return {
            'name': 'Registrar auditoria',
            'type': 'ir.actions.act_window',
            'res_model': 'register.audit.checklist.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'default_audit_user_id': self.env.uid,
                'default_audit_date': fields.Datetime.now(),
            }
        }