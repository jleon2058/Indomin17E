from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Documentacion Personal

    has_id = fields.Boolean(string='Copia DNI vigente del trabajador')
    has_id_hijo_conyuge = fields.Boolean(string='Copia de DNI de hijos y/o cónyuge')
    has_copy_servicios = fields.Boolean(string='Copia de recibo de servicios (domicilio actualizado)')
    has_foto_carnet = fields.Boolean(string='Fotografía tamaño carnet (opcional)')
    has_ficha_datos = fields.Boolean(string='Ficha de Datos Indomin / Mecaparts')
    has_doc_vida_ley = fields.Boolean(string='Doc de Vida Ley Legalizado')
    has_declaracion_jur_dom = fields.Boolean(string='Declaración jurad de Domicilio')
    has_declaracion_renta_quinta = fields.Boolean(string='Declaración de Renta de Quinta')
    has_copia_brevet_lic_cond = fields.Boolean(string='Copia de brevee o licencia de conducir (si aplica)')

    # Documentacion Laboral

    has_contrato_firmado = fields.Boolean(string='Currículum Vitae')
    has_cv = fields.Boolean(string='Hoja de vida (CV) actualizada y documentada')
    has_declaracion_jur_ver_info = fields.Boolean(string='Declaración jurada de veracidad de la información')
    has_antecedentes_pp = fields.Boolean(string='Antecedentes penales/policiales (opcional)')
    has_ficha_st_personales = fields.Boolean(string='Ficha de datos personales')
    has_const_STARSOFT = fields.Boolean(string='Constancia de Alta en STARSOFT')


    # Obligaciones Legales del Empleador

    has_registro_T_Registro = fields.Boolean(string='Registro en T-Registro (SUNAT)')
    has_eleccion_sist_pre_ONP_AFP = fields.Boolean(string='Elección del sistema previsional (ONP o AFP)')
    has_reg_cobert_SCTR = fields.Boolean(string='Registro y cobertura del SCTR (si aplica)')
    has_rem_cont_MTPE = fields.Boolean(string='Remisión del contrato al MTPE (si es plazo fijo)')
    has_boleta_pag_elect = fields.Boolean(string='Entrega de boletas de pago electrónicas')
    has_banda_salar = fields.Boolean(string='Registro de la banda salarial del puesto')
    has_escala_salar = fields.Boolean(string='Entrega de la escala salarial y criterios de pago')

    

    # Campo calculado para el porcentaje de completado
    document_completion = fields.Integer(
        string='Completado (%)',
        compute='_compute_document_completion',
        store=True,
        default=0
    )
    


    @api.depends('has_id','has_id_hijo_conyuge','has_copy_servicios','has_foto_carnet',
                'has_ficha_datos','has_doc_vida_ley','has_declaracion_jur_dom',
                'has_declaracion_renta_quinta','has_copia_brevet_lic_cond',
                'has_contrato_firmado','has_cv','has_declaracion_jur_ver_info','has_antecedentes_pp','has_ficha_st_personales','has_const_STARSOFT',
                'has_registro_T_Registro','has_eleccion_sist_pre_ONP_AFP','has_reg_cobert_SCTR','has_rem_cont_MTPE','has_boleta_pag_elect','has_banda_salar','has_escala_salar')  # ← has_copy_servicios quitado del final
    def _compute_document_completion(self):
        for employee in self:
            logger.warning("-------for employee-------")
            # Lista de TODOS los campos booleanos a considerar (11 campos)
            boolean_fields = [
                employee.has_id,
                employee.has_id_hijo_conyuge,
                employee.has_copy_servicios,  # ← Este aparece una sola vez
                employee.has_foto_carnet,
                employee.has_ficha_datos,
                employee.has_doc_vida_ley,
                employee.has_declaracion_jur_dom,
                employee.has_declaracion_renta_quinta,
                employee.has_copia_brevet_lic_cond,
                employee.has_contrato_firmado,
                employee.has_cv,
                employee.has_declaracion_jur_ver_info,
                employee.has_antecedentes_pp,
                employee.has_ficha_st_personales,
                employee.has_const_STARSOFT,
                employee.has_registro_T_Registro,
                employee.has_eleccion_sist_pre_ONP_AFP,
                employee.has_reg_cobert_SCTR,
                employee.has_rem_cont_MTPE,
                employee.has_boleta_pag_elect,
                employee.has_banda_salar,
                employee.has_escala_salar
            ]
            
            total_fields = len(boolean_fields)  # ← Esto será 11
            completed_fields = sum(boolean_fields)
            
            percentage = (completed_fields * 100) // total_fields if total_fields > 0 else 0
        
            # Debug info
            print(f"Employee: {employee.name}")
            print(f"Total fields: {total_fields}")
            print(f"Completed: {completed_fields}")
            print(f"Percentage: {percentage}%")
            print("Field values:", boolean_fields)
            
            employee.document_completion = percentage
            logger.warning("------document_completion-------")
            logger.warning(employee.document_completion)
        
    # def write(self, vals):
    #     logger.warning("-------write-check-------")
    #     result = super().write(vals)
    #     # Si se modificó algún campo booleano, forzar recálculo
    #     boolean_fields = ['has_id', 'has_id_hijo_conyuge', 'has_copy_servicios', 'has_foto_carnet',
    #                      'has_ficha_datos', 'has_doc_vida_ley', 'has_declaracion_jur_dom',
    #                      'has_declaracion_renta_quinta', 'has_copia_brevet_lic_cond',
    #                      'has_contrato_firmado', 'has_registro_T_Registro']
        
    #     if any(field in vals for field in boolean_fields):
    #         logger.warning("-------if any-------")
    #         print("🔄 Boolean field changed, recomputing document_completion")
    #         self._compute_document_completion()
    #         #self.env.invalidate_cache(fnames=['document_completion'], ids=self.ids)
    #     return result
    
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     """Override para asegurar que la vista se actualice correctamente"""
    #     res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     return res