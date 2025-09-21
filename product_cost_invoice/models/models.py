# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.exceptions import UserError
import re
import logging
logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def product_price_update_before_done(self, forced_qty=None, is_new=False):
        """
        Update and check the standard_price of products before a validate picking or a new invoice entry.

        :param str|date forced_qty: new quantity
        :param str|date is_new: is a new calculation or a update a old calculation
        """
        tmpl_dict = defaultdict(lambda: 0.0)
        # adapt standard price on incomming moves if the product cost_method is 'average'
        std_price_update = {}

        for move in self.filtered(lambda move: move._is_in() and move.with_company(move.company_id).product_id.cost_method == 'average'):

            #product_tot_qty_available = move.product_id.sudo().with_company(move.company_id).quantity_svl + tmpl_dict[move.product_id.id]

            if move.state=='done':
                logger.warning("----move.account_move_line_ids-------")
                logger.warning(move)
                self.env.cr.execute(
                    """
                    SELECT COALESCE(sum(quantity),0)
                    FROM stock_valuation_layer WHERE company_id = %s and stock_move_id != %s and product_id = %s and create_date < %s
                    """,(move.company_id.id,move.id,move.product_id.id,move.date))
                res1 = self.env.cr.fetchone()
                product_tot_qty_available = res1[0] if res1 else 0

            else:
                logger.warning("----move.account_move_line_ids else-------")
                self.env.cr.execute(
                    """
                    SELECT COALESCE(sum(quantity),0)
                    FROM stock_valuation_layer WHERE company_id = %s and product_id = %s
                    """,(move.company_id.id,move.product_id.id))
                res1 = self.env.cr.fetchone()
                product_tot_qty_available = res1[0] if res1 else 0

            logger.warning("-----product_tot_qty-----")
            logger.warning(product_tot_qty_available)
            rounding = move.product_id.uom_id.rounding

            valued_move_lines = move._get_in_move_lines()
            quantity = 0
            for valued_move_line in valued_move_lines:
                quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity, move.product_id.uom_id)
                logger.warning("----for----")
            qty = forced_qty or quantity
            if float_is_zero(product_tot_qty_available, precision_rounding=rounding):
                new_std_price = move._get_price_unit()
                logger.warning("---if float----")
            elif float_is_zero(product_tot_qty_available + move.product_qty, precision_rounding=rounding) or \
                    float_is_zero(product_tot_qty_available + qty, precision_rounding=rounding):
                new_std_price = move._get_price_unit()
                logger.warning("----elif float----")
            else:
                # Get the standard price
                if is_new:
                    logger.warning("----else if float----")

                    # calculo de Cantidades antes del movimiento


                    # calculo de Cantidades antes del movimiento
                    self.env.cr.execute(
                        """
                        select COALESCE(sum(svl.quantity),0) AS suma_qty
                        FROM stock_valuation_layer svl
                        left join stock_move sm on(sm.id = svl.stock_move_id)
                        WHERE svl.company_id = %s and sm.company_id = %s and svl.stock_move_id != %s and svl.product_id = %s and svl.create_date < %s and sm.state ='done'
                        """,(move.company_id.id, move.company_id.id ,move.id, move.product_id.id, move.date))
                    res_cant_mov = self.env.cr.fetchone()



                    # calculo de los montos antes del movimiento
                    self.env.cr.execute(
                        """
                        select COALESCE(sum(svl.value),0) AS suma_valor
                        FROM stock_valuation_layer svl
                        left join stock_move sm on(sm.id = svl.stock_move_id)
                        WHERE svl.company_id = %s and sm.company_id = %s and svl.stock_move_id != %s and svl.product_id = %s and svl.create_date < %s and sm.state ='done'
                        """,(move.company_id.id, move.company_id.id ,move.id, move.product_id.id, move.date))
                    res_monto_mov = self.env.cr.fetchone()

                    self.env.cr.execute(
                        """
                        select coalesce(sum(balance),0)
                        from account_move_line aml 
                        left join account_move am on (am.id=aml.move_id)
                        left join account_account aa on (aa.id = aml.account_id)
                        where aml.company_id = %s and aml.product_id = %s and am.create_date < %s and am.stock_move_id is null and am.state = 'posted' and aa.is_inventory_account is true
                        """,(move.company_id.id,move.product_id.id,move.date))
                    res_ajuste_mov = self.env.cr.fetchone()

                    new_std_price = ((res_monto_mov[0] or 0) + (res_ajuste_mov[0] or 0) + (move._get_price_unit() * abs(qty))) / ((res_cant_mov[0] or 0) + abs(qty))
                    logger.warning("---Parametros----")
                    logger.warning(move._get_price_unit())
                    logger.warning(res_monto_mov[0])
                    logger.warning(res_ajuste_mov[0])
                    logger.warning(res_ajuste_mov[0]+res_monto_mov[0] or 0)
                    logger.warning(res_cant_mov[0])
                else:
                    logger.warning("----else else float----")
                    amount_unit = std_price_update.get((move.company_id.id, move.product_id.id)) or move.product_id.with_company(move.company_id).standard_price
                    logger.warning("----datos else----")
                    logger.warning(amount_unit)
                    logger.warning(move._get_price_unit())
                    logger.warning(qty)
                    logger.warning("----calculo new_std_price----")
                    new_std_price = ((amount_unit * product_tot_qty_available) + (move._get_price_unit() * qty)) / (product_tot_qty_available + qty)
            logger.warning("--precio new_std_price--")
            logger.warning(new_std_price)
            tmpl_dict[move.product_id.id] += quantity
            # logger.warning("----else else----")
            # logger.warning(new_std_price)
            # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products

            # self.env.cr.execute(
            #     """
            #     SELECT sum(value), sum(quantity)_compute_quantity
            #     FROM stock_valuation_layer WHERE company_id = %s and product_id = %s
            #     """,(move.company_id.id,move.product_id.id))
            # res2 = self.env.cr.fetchone()
            # std_price = (res2[0] or 0) / (res2[1] or 1)
            # logger.warning("----precio_std----")
            # logger.warning(std_price)

            #raise UserError("¡Hubo un error! La condición no se cumplió.")
            move.product_id.with_company(move.company_id.id).with_context(disable_auto_svl=True).sudo().write({'standard_price': new_std_price})
            std_price_update[move.company_id.id, move.product_id.id] = new_std_price



        # adapt standard price on incomming moves if the product cost_method is 'fifo'
        for move in self.filtered(lambda move:
                                  move.with_company(move.company_id).product_id.cost_method == 'fifo'
                                  and float_is_zero(move.product_id.sudo().quantity_svl, precision_rounding=move.product_id.uom_id.rounding)):
            move.product_id.with_company(move.company_id.id).sudo().write({'standard_price': move._get_price_unit()})   

        # raise UserError("¡Hubo un error! La condición no se cumplió.")
    def _get_price_unit(self):
        logger.warning("----_get_price_unit----")
        """ Returns the unit price for the move"""
        self.ensure_one()

        # Si la moneda esta en una distinta a lo que esta configurado en la compañia
        if self.purchase_line_id.order_id.currency_id.id != self.purchase_line_id.order_id.company_id.currency_id.id:
            logger.warning("----if get----")
            # if self.purchase_line_id and self.purchase_line_id.invoice_lines.filtered(lambda x: x.move_id.state not in ('draft', 'cancel')) and self.product_id.id == self.purchase_line_id.product_id.id:
            lista_aml=self.account_move_line_ids
            taxes = self.purchase_line_id.taxes_id

            if lista_aml:
                # Filtramos las líneas que corresponden al mismo producto, si es necesario
                filtered_lines = lista_aml.filtered(lambda line: line.product_id == self.product_id)
                logger.warning("----lista_aml 1-----")
                logger.warning(filtered_lines)

                if filtered_lines:
                    # Selecciona la línea con el valor máximo en base a la lógica que estás usando
                    inv_line = max(filtered_lines, key=lambda line: abs(line.balance / line.amount_currency))
                    logger.warning("-----lista_aml 2-----")
                    logger.warning(inv_line)
                else:
                    inv_line = self.env['account.move.line']  # O algún valor predeterminado
            else:
                logger.warning("----lista_aml 1 else-----")
                inv_line = self.env['account.move.line']  # O algún valor predeterminado
                logger.warning(inv_line)

            #inv_line=max(lista_aml,key=lambda line: abs(line.balance/line.amount_currency))
            # if self.purchase_line_id and inv_line.filtered(lambda x: x.move_id.state not in ('draft', 'cancel')) and self.product_id.id == self.purchase_line_id.product_id.id:

            # 
            if inv_line.filtered(lambda x: x.move_id.state not in ('draft', 'cancel')) and self.product_id.id == self.purchase_line_id.product_id.id:
                price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
                logger.warning("-----get_price-----")
                logger.warning(price_unit_prec)
                #line = self.purchase_line_id.invoice_lines.filtered(lambda x: x.move_id.state not in ('draft', 'cancel'))[0]
                line = inv_line.filtered(lambda x: x.stock_move_id.id==self.id)
                logger.warning("-----line----")
                logger.warning(line)
                if line:
                    #---- Si es una nota de credito , el costo en el movimiento no debe variar.
                    if line.move_id.reversed_entry_id:
                        price_unit=self.precio_unit_asiento
                        return price_unit
                    else:
                        logger.warning("-----line_movimiento----")
                        price_unit=line.price_unit
                        order = line.move_id #invoice
                        for tax in taxes:
                            if tax.include_base_amount:
                                if tax.price_include:
                                    # Se multiplicará por 0.01 para llevar a terminos de porcentaje
                                    importe_tax = tax.amount*0.01
                                    price_unit = price_unit/(1+importe_tax)
                                    # for ln in line:
                                    #     logger.warning("---self_purchase if----")
                                    #     ln.price_unit = line.price_unit/(1+importe_tax)
                                    logger.warning("-----price_unit_taxes---------")
                                    logger.warning(price_unit) 
                        
                        if line.discount>0:
                            price_unit=price_unit*(1-line.discount/100)
                        # else:
                        #     price_unit = line.price_unit #invoice
                            logger.warning("-----price_unit_discount---------")
                            logger.warning(price_unit)
                        if line.tax_ids:
                            qty = line.quantity or 1
                        if line.product_uom_id.id != line.product_id.uom_id.id:
                            price_unit *= line.product_uom_id.factor / line.product_id.uom_id.factor
                        if order.currency_id != order.company_id.currency_id:
                            # The date must be today, and not the date of the move since the move move is still
                            # in assigned state. However, the move date is the scheduled date until move is
                            # done, then date of actual move processing. See:
                            # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36

                            # logger.warning("--parametros order--")
                            # logger.warning(price_unit)
                            # logger.warning(order.invoice_date)
                            price_unit = order.currency_id._convert(
                                price_unit, order.company_id.currency_id, order.company_id, order.invoice_date, round=False)
                            logger.warning("---if price_unit---")
                            logger.warning(price_unit)
                            #raise UserError("¡Hubo un error! La condición no se cumplió.")
                        return price_unit
                    
                else:
                    if self.picking_id.origin==self.purchase_line_id.order_id.name:
                        logger.warning("----else_sp_if")
                        price_unit = self.purchase_line_id.currency_id._convert(
                                self.purchase_line_id.price_unit, self.purchase_line_id.company_id.currency_id, self.company_id, self.date, round=False)

                        for tax in taxes:
                            if tax.include_base_ammount:
                                if tax.price_include:
                                    # Se multiplicará por 0.01 para llevar a terminos de porcentaje
                                    importe_tax = tax.amount*0.01
                                    price_unit = price_unit/(1+importe_tax)

                        logger.warning("---else if price_unit---")
                        logger.warning(price_unit)
                        return price_unit
                    
                    else:
                        logger.warning("---else price_unit---")
                        origin_value = self.picking_id.origin
                        logger.warning(origin_value)
                        producto=self.product_id.id
                        partes = origin_value.split(' ')
                        if partes:
                            last_word = partes[-1]
                            logger.warning("---if partes-----")
                            logger.warning(last_word)
                            stock_id=self.env['stock.move'].search([('reference','=',last_word),('product_id','=',producto)])
                            logger.warning(stock_id)
                            # if stock_id.account_move_line_ids:
                            #     logger.warning("---if partes stock_id-----")
                            #     price_unit = self.purchase_line_id.currency_id._convert(
                            #         self.purchase_line_id.price_unit, self.purchase_line_id.company_id.currency_id, self.company_id, stock_id.account_move_line_ids.move_id.invoice_date, round=False)
                            # else:
                            #     logger.warning("---else partes stock_id-----")
                            #     price_unit = self.purchase_line_id.currency_id._convert(
                            #         self.purchase_line_id.price_unit, self.purchase_line_id.company_id.currency_id, self.company_id, stock_id.date, round=False)
                            # logger.warning("---else else price_unit---")
                            # logger.warning(price_unit)
                            price_unit=stock_id.precio_unit_asiento
                            return price_unit
                        else:
                            logger.warning("No se encontraron palabras")
                    

            # elif self.purchase_line_id and not inv_line:

            #     price_unit = self.purchase_line_id.currency_id._convert(
            #                     self.purchase_line_id.price_unit, self.purchase_line_id.company_id.currency_id, self.company_id, self.date, round=False)

            #     if self.purchase_line_id.taxes_id.price_include:
            #         importe_tax = self.purchase_line_id.taxes_id.amount*0.01
            #         price_unit = price_unit/(1+importe_tax)

            #     logger.warning("---elif price_unit---")
            #     logger.warning(price_unit)
            #     return price_unit

            # else:
            #     logger.warning("---else else price_unit---")
            #     return super(StockMove, self)._get_price_unit()

            else:
                if self.picking_id.picking_type_code=='outgoing':
                    logger.warning("---else get_price--")
                    origin_value = self.picking_id.origin
                    logger.warning(origin_value)
                    purchase_line = self.purchase_line_id.id
                    partes = origin_value.split(' ')
                    if partes:
                        last_word = partes[-1]
                        logger.warning("---if partes producto get_price-----")
                        logger.warning(last_word)
                        stock_id=self.env['stock.move'].search([('reference','=',last_word),('purchase_line_id','=',purchase_line)])
                        logger.warning(stock_id)
                        price_unit=stock_id.precio_unit_asiento
                        return price_unit
                    else:
                        raise UserError("No se encontraron palabras")
                else:
                    logger.warning("---elif purchase_line---")
                    logger.warning(self.purchase_line_id.price_unit)

                    if self.purchase_line_id.discount:
                        price_unit = self.purchase_line_id.currency_id._convert(
                                    self.purchase_line_id.price_unit, self.purchase_line_id.company_id.currency_id, self.company_id, self.date, round=False)*(1-self.purchase_line_id.discount*0.01)
                    else:
                        price_unit = self.purchase_line_id.currency_id._convert(
                                    self.purchase_line_id.price_unit, self.purchase_line_id.company_id.currency_id, self.company_id, self.date, round=False)

                    for tax in taxes:
                        if tax.include_base_amount:
                            if tax.price_include:
                                # Se multiplicará por 0.01 para llevar a terminos de porcentaje
                                importe_tax = tax.amount*0.01
                                price_unit = price_unit/(1+importe_tax)

                    logger.warning("---elif price_unit---")
                    logger.warning(price_unit)
                    return price_unit
            
        else:
            logger.warning("----else if get----")
            return super(StockMove, self)._get_price_unit()


    def _get_avg_sql_price_unit(self):
        """ Returns the unit price for the move"""

        # Si el movimiento pertenece a un ingreso de compra con moneda distinta a soles
        if self.purchase_line_id:
            return self._get_price_unit()
        
        # Si el movimiento pertenece a un ingreso por ajuste
        elif self.location_id.usage=='inventory' and self.location_dest_id.usage=='internal':
            costo_ajuste = self.precio_unit_asiento
            return costo_ajuste

        # Si el movimiento pertenece a un consumo por ajuste
        elif self.location_id.usage=='internal' and self.location_dest_id.usage=='inventory':
            costo_ajuste = self.precio_unit_asiento
            return costo_ajuste

        # Si el movimiento pertenece a un consumo o devolucion de consumo
        else:   
            self.env.cr.execute(
                """
                select COALESCE(sum(svl.quantity),0) AS suma_qty
                FROM stock_valuation_layer svl
                left join stock_move sm on(sm.id = svl.stock_move_id)
                WHERE svl.company_id = %s and sm.company_id = %s and svl.stock_move_id != %s and svl.product_id = %s and svl.create_date < %s and sm.state ='done'
                """,(self.company_id.id, self.company_id.id ,self.id, self.product_id.id, self.date))
            res_cant_mov = self.env.cr.fetchone()

            # calculo de los montos antes del movimiento
            self.env.cr.execute(
                """
                select COALESCE(sum(svl.value),0) AS suma_valor
                FROM stock_valuation_layer svl
                left join stock_move sm on(sm.id = svl.stock_move_id)
                WHERE svl.company_id = %s and sm.company_id = %s and svl.stock_move_id != %s and svl.product_id = %s and svl.create_date < %s and sm.state ='done'
                """,(self.company_id.id, self.company_id.id ,self.id, self.product_id.id, self.date))
            res_monto_mov = self.env.cr.fetchone()

            # self.env.cr.execute(
            #     """
            #     SELECT COALESCE(sum(value),0) AS suma_asiento
            #     FROM stock_valuation_layer 
            #     WHERE company_id = %s and product_id = %s and create_date < %s AND stock_move_id IS NULL AND account_move_id IS NOT NULL
            #     """,(self.company_id.id,self.product_id.id,self.date))
            # res4 = self.env.cr.fetchone()

            # Calculo de los montos de Ajuste en el movimiento.
            # self.env.cr.execute(
            #     """
            #     select coalesce(sum(balance),0)
            #     from account_move_line aml 
            #     left join account_move am on (am.id=aml.move_id)
            #     left join account_account aa on (aa.id = aml.account_id)
            #     where aml.company_id = %s and aml.product_id = %s and am.create_date < %s and am.stock_move_id is null and am.state = 'posted' and aa.is_inventory_account is true
            #     """,(self.company_id.id,self.product_id.id,self.date))
            # res_monto_ajuste = self.env.cr.fetchone()


            self.env.cr.execute(
                """
                select COALESCE(sum(svl.value),0) AS valor_ajuste
                FROM stock_valuation_layer svl
                WHERE svl.company_id = %s and svl.product_id = %s and svl.stock_move_id is null and svl.create_date < %s
                """,(self.company_id.id,self.product_id.id,self.date))
            res_monto_ajuste = self.env.cr.fetchone()

            press=((res_monto_mov[0] + res_monto_ajuste[0]) or 0) / (res_cant_mov[0] or 1)
            logger.warning("-----Costo calculado del consumo----")
            #logger.warning(self)
            logger.warning(res_monto_mov[0])
            logger.warning(res_monto_ajuste[0])
            logger.warning(res_monto_mov[0] + res_monto_ajuste[0] or 0)
            logger.warning(res_cant_mov[0])
            logger.warning(press)
            #raise UserError("¡Hubo un error! La condición no se cumplió.")
            #return ((res[0] + res4[0]) or 0) / (res[1] or 1)
            return press

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def cron_update_standard_price(self, start_date=None, end_date=None, invoice_ids=None):
        logger.warning("---------cron------------")
        """
        Update standard_price of products.

        :param str|date start_date: start date of search params
        :param str|date end_date: end date of search params
        :param list invoice_ids: list of ids of invoices
        """
        if invoice_ids:
            return self.browse(invoice_ids).update_standard_price()
        params = []
        if start_date:
            params.append(('invoice_date', '>=', start_date))
        if end_date:
            params.append(('invoice_date', '<=', end_date))
        self.search(params).update_standard_price()

    def update_stock_move_line(self, line):
        logger.warning("----------update_stock_move_line-----------{}".format(line))
        valuation = self.env['stock.valuation.layer'].search([('stock_move_id', '=', line.id)])
        logger.warning(valuation)
        if valuation:
            unit_price = line._get_avg_sql_price_unit()
            logger.warning("-----Costo calculado y costo del movimiento----")
            monto = unit_price*round(line.product_uom_qty,2)
            #Obtencion del nuevo precio
            logger.warning(monto)
            logger.warning(line.monto_asiento)
            #valued_move_lines = line._get_in_move_lines()
            #valued_move_lines = line.move_line_ids.ids
            #logger.warning(valued_move_lines)
            #valued_quantity=line.product_qty
            #valued_quantity = 0
            # for valued_move_line in valued_move_lines:
            #     valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, line.product_id.uom_id)
            #     logger.warning("---------valued_quantity-----------")
            #     logger.warning(valued_quantity)
            # for i in valuation:
            #     logger.warning("-----i in valuation-----")
            #     logger.warning(i)
            #     logger.warning(i.quantity)
            #     logger.warning(unit_price)
            # rounded_monto=Decimal(monto).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
            if round(line.monto_asiento,2) != round(monto,2):
                
                logger.warning("--------precios coinciden---------")
                # raise UserError("¡Hubo un error! La condición no se cumplió.")
                valuation.write({
                    'value': line.company_id.currency_id.round(unit_price * valuation.quantity),
                    'unit_cost': unit_price
                })
                logger.warning(valuation.unit_cost)
                logger.warning(valuation.value)    
                move = self.env['account.move'].search(
                    [('stock_move_id', '=', line.id), ('state', '=', 'posted')],
                    order="create_date asc",
                    limit=1
                )
                logger.warning("-----logger move-----")
                logger.warning(move)
                move.button_draft()
                move.line_ids.unlink()
                value_valuation = sum([v.value for v in valuation]) / len(valuation)
                logger.warning("-------value_valuation---------")
                logger.warning(value_valuation)
                vals = line._account_entry_move(valuation.quantity, valuation.description, valuation.id, value_valuation)[0]
                vals['date'] = move.date
                move.write(vals)
                move._post()
                if valuation.company_id.anglo_saxon_accounting:
                    valuation.stock_move_id._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=valuation.product_id)

            # new_valuation=self.env['stock.valuation.layer'].search([('stock_move_id','=',line.id)])
            # logger.warning("-------new valuation-------")
            #logger.warning(new_valuation.value)

    def update_standard_price(self):

        logger.warning("---------update------------")
        #raise UserError("¡Hubo un error! NO DEBE ENTRAR AQUI.")
        """
        Calculate new standard_price of products of the related purchase order
    ====================

    Legend:
        product = The REPL main loop stop.
        product_standard_price = Exception raised.
        account_move = Stay in REPL.
        ######1 = Account of chart account.
        ######2 = Account of chart account.

-------------------------TIME 0---------------------------
product_standard_price = old product_standard_price # we use the same value
F.E:

product_standard_price = S/. 100.00

 account  | debit      | credit     |
 ######1  | S/. 100.00 | 0          |
 ######2  | 0          | S/. 100.00 |

stock.valuation.layer
- current_date | S/. 100.00
-----------------------------------------------------------
-------------------------TIME 1---------------------------
account.move().update_standard_price
product_standard_price = new product_standard_price
F.E:

product_standard_price = S/. 110.00

 account  | debit      | credit     |
 ######1  | S/. 110.00 | 0          |
 ######2  | 0          | S/. 110.00 |

stock.valuation.layer
- current_date | S/. 110.00
-----------------------------------------------------------
        """
        # line_ids = self.mapped('line_ids').mapped('purchase_line_id').ids
        # move_lines = self.env['stock.move'].search([('purchase_line_id', 'in', line_ids)])

        #productos = self.mapped('invoice_line_ids').mapped('product_id').ids
        #line_ids = self.mapped('transfer_ids').ids
        #move_lines = self.env['stock.move'].search([('picking_id','in',line_ids),('product_id','in',productos)])

        move_lines = self.mapped('invoice_line_ids').mapped('stock_move_id')

        logger.warning("-----------movimientos------------")

        # productos = self.mapped('invoice_line_ids').mapped('product_id').ids
        # line_ids = self.mapped('picking_id').ids  
        # move_lines = self.env['stock.move'].search([('picking_id','in',line_ids),('product_id','in',productos)])
        logger.warning(move_lines)

        for line in move_lines:
            line.product_price_update_before_done(
                forced_qty=sum(
                    [valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity, line.product_id.uom_id)
                     for valued_move_line in line._get_in_move_lines()]) * -1,
                is_new=True,
            )
            logger.warning("------datos del for values------")

            self.update_stock_move_line(line)
        #raise UserError("¡Hubo un error! La condición no se cumplió.")
        if move_lines:


            movimientos_posteriores=self.env['stock.move'].search([
                ('product_id', 'in', move_lines.mapped('product_id').ids),
                ('purchase_line_id', '=', False),
                ('date', '>=', move_lines[0].date),
                ('state','=','done'),
                ('id', 'not in', move_lines.ids),
                ('location_id.usage','=','internal'),
                ('location_dest_id.usage','=','production') 
            ], order='date asc')
            logger.warning("------Movimientos posterior--------")
            logger.warning(movimientos_posteriores)
            # for line in self.env['stock.move'].search([
            #     ('product_id', 'in', move_lines.mapped('product_id').ids),
            #     ('purchase_line_id', '=', False),
            #     ('date', '>=', move_lines[0].date),
            #     ('state','=','done'),
            #     ('id', 'not in', move_lines.ids)
            # ], order='date asc'):
            for line in movimientos_posteriores:
            # raise UserError("¡Hubo un error! La condición no se cumplió.")
                self.update_stock_move_line(line)
                logger.warning("-----product_line-------")
                logger.warning(line.precio_unit_asiento)
                logger.warning(line.id)
            move_lines[-1].product_price_update_before_done(
                forced_qty=sum(
                    [valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity, line.product_id.uom_id)
                     for valued_move_line in line._get_in_move_lines()]) * -1,
                is_new=True,
            )

            for mov in move_lines:
                self.env.cr.execute(
                    """
                    SELECT sum(value), sum(quantity)_compute_quantity
                    FROM stock_valuation_layer WHERE company_id = %s and product_id = %s
                    """,(mov.company_id.id,mov.product_id.id))
                res2 = self.env.cr.fetchone()
                std_price = (res2[0] or 0) / (res2[1] or 1)
                logger.warning("----precio_std----")
                logger.warning(res2[0])
                logger.warning(res2[1])
                logger.warning(std_price)

                mov.product_id.with_company(mov.company_id.id).with_context(disable_auto_svl=True).sudo().write({'standard_price': std_price})

    # def action_post(self):
    #     logger.warning(f"Contexto en product_cost_invoice: {self.env.context}")
    #     if self.env.context.get('skip_product_cost_invoice'):
    #         logger.warning("Saliendo de product_cost_invoice.action_post() por contexto")
    #         return super().action_post()  # Solo ejecuta la versión original de Odoo
    #     """
    #     Function to process an account.move and recalculate the standard_price of products.
    #     """
    #     logger.warning("Ejecutando product_cost_invoice.action_post()")
    #     res = super(AccountMove, self).action_post()
    #     self.filtered(lambda x: x.currency_id.id != x.company_id.currency_id.id).update_standard_price()

    #     return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def standard_price_correction(self, product_ids=None, move_date=None,move_date_end=None,company=None,category=None):
        logger.warning("-----standard_price_correction-------")


        if not product_ids:

            if not category:
                product_obtenidos = self.env['product.product'].search([('active','=','True')]).ids

            else:
                categorias_hija = self.env['product.category'].search([('parent_id','=',category)]).ids
                
                # for categoria in categorias_hija:
                #     product_obtenidos = self.env['product.product'].search([('categ_id','=',categoria)]).ids
                #     logger.warning("-------product obtenidos---------")
                #     logger.warning(product_obtenidos)
                #     product_ids.extend(product_obtenidos)

                product_obtenidos = self.env['product.product'].search([('active','=','True'),('categ_id','in',categorias_hija)]).ids

            movimientos1 = self.env['stock.move'].search([('date','>=',move_date),('state','=','done'),('company_id','=',company),('date','<=',move_date_end),('location_id.usage','=','internal'),('location_dest_id.usage','!=','internal')])
            movimientos2 = self.env['stock.move'].search([('date','>=',move_date),('state','=','done'),('company_id','=',company),('date','<=',move_date_end),('location_id.usage','!=','internal'),('location_dest_id.usage','=','internal')])
            movimientos = (movimientos1 | movimientos2)
            productos_con_movimiento = movimientos.mapped('product_id.id')

            product_ids = list(set(product_obtenidos) & set(productos_con_movimiento))
            logger.warning("--------------product_ids--------")
            logger.warning(product_ids)
        
        for producto in product_ids:
            logger.warning("----------------producto:--------{}".format(producto))
            stock_valuation = self.env['stock.valuation.layer'].search([
            ('product_id', '=', producto),
            ('stock_move_id', '=', False),
            ('quantity', '=', 0),
            ('company_id','=',company),
            ('value', '!=', 0)
            ])
            logger.warning("-------Ajustes de Precio   :----")
            logger.warning(stock_valuation)
            #logger.warning(stock_valuation.value)

            line_ids = self.env['purchase.order.line'].search([('product_id', '=', producto),('company_id','=',company),('state','=','purchase')])
            move_lines_compra = self.env['stock.move'].search([('purchase_line_id', 'in', line_ids.ids),('state','=','done'),('date','>',move_date),('product_id','=',producto)])
            move_lines_ajuste = self.env['stock.move'].search([('product_id','=',producto),('location_id.usage','=','inventory'),('location_dest_id.usage','=','internal'),('state','=','done'),('date','>',move_date),('company_id','=',company)])
            move_line_dev_csm = self.env['stock.move'].search([('product_id','=',producto),('location_id.usage','=','production'),('location_dest_id.usage','=','internal'),('state','=','done'),('date','>',move_date),('company_id','=',company)])
            move_lines_comb = (move_lines_compra | move_lines_ajuste | move_line_dev_csm)
            move_lines = move_lines_comb.sorted(key=lambda x: (x.date,x.id))
            #move_lines = (move_lines_compra | move_lines_ajuste).sorted(key=lambda x: x.date)

            logger.warning("------Movimiento de Compras e Ingreso por Ajuste------")   
            logger.warning(move_lines)

            for line in move_lines:
                logger.warning("Movimiento   :{}".format(line))
                logger.warning("    ")

                # Determinación del costo si es que la moneda es distinta a Soles
                if line.purchase_line_id and line.purchase_line_id.order_id.currency_id.id != line.company_id.currency_id.id:

                    # Si el movimiento esta asociado a lineas de factura que estan publicadas
                    if line.account_move_line_ids.filtered(lambda l: l.move_id.state == 'posted'):

                        # Obtengo las lineas verificando que el que el producto esta contenido en el sm y en sus lineas
                        filtered_lines = line.account_move_line_ids.filtered(lambda l: l.product_id == line.product_id)

                        if filtered_lines:
                            # Selecciona la línea con el valor máximo en base a la lógica que estás usando
                            inv_line = max(filtered_lines, key=lambda line: abs(line.balance / line.amount_currency))
                            logger.warning("------linea de factura con mayor TC: -----{}".format(inv_line))
                            logger.warning("     ")

                        else:
                            inv_line = self.env['account.move.line']
                            logger.warning("---------aml vacio-------")
                            logger.warning(inv_line)

                        precio_subtotal_soles = (line.monto_asiento)*(inv_line.quantity)/(line.product_uom_qty)
                        # Si el precio en el movimiento es distinto al precio de la factura
                        if round(precio_subtotal_soles,2) != round(inv_line.balance,2):
                            logger.warning("-----sm.price_unit_asiento != aml.balance/quantity------")
                            line.product_price_update_before_done(
                                forced_qty=sum(
                                    [valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity, line.product_id.uom_id)
                                    for valued_move_line in line._get_in_move_lines()]) * -1,
                                is_new=True,
                            )
                            logger.warning("-----standard_price_correction_line 1-------")
                            self.env['account.move'].update_stock_move_line(line)
                    
                    # Si el movimiento esta asociado a lineas de factura no publicadas o no estan asociadas a facturas
                    else:
                        if line.picking_id.picking_type_code=='outgoing':

                            logger.warning("-----Devolucion de compra------")
                            origin_value = line.picking_id.origin
                            logger.warning(origin_value)
                            purchase_line = line.purchase_line_id.id
                            partes = origin_value.split(' ')
                            if partes:
                                last_word = partes[-1]
                                logger.warning("-----Devolucion de la linea de transferencia-----")
                                stock_id=self.env['stock.move'].search([('reference','=',last_word),('purchase_line_id','=',purchase_line)])
                                logger.warning(stock_id)
                            
                                if stock_id:
                                    precio_subtotal_soles = (stock_id.precio_unit_asiento)*(line.product_uom_qty)
                                else:
                                    precio_subtotal_soles = line.monto_asiento   

                            else:
                                precio_subtotal_soles = line.monto_asiento
                            
                        else:
                            logger.warning("-----Ingreso de compra sin Factura------")
                        #tc = line.obtener_tipo_cambio(line.date,line.purchase_line_id.order_id.currency_id.id,line.company_id.currency_id.id)

                            from_currency = line.purchase_line_id.order_id.currency_id  # Moneda de origen
                            to_currency = line.company_id.currency_id  # Moneda de destino (soles)

                            # Obtenemos el tipo de cambio en la fecha especificada
                            tipo_cambio = from_currency._get_conversion_rate(
                                from_currency,
                                to_currency,
                                line.company_id,
                                line.date
                            )

                            logger.warning("----Tipo cambio-----{}".format(tipo_cambio))

                            price_subtotal_soles_orden = line.purchase_line_id.order_id.currency_id._convert(
                                line.purchase_line_id.price_subtotal, line.company_id.currency_id, line.company_id, line.date, round=False)
                            
                            # if line.purchase_line_id.discount:
                            #     precio_subtotal_soles = (price_subtotal_soles_orden)*(line.product_uom_qty)*(1-line.purchase_line_id.discount*0.01)/(line.purchase_line_id.product_uom_qty)

                            # else:
                            precio_subtotal_soles = (price_subtotal_soles_orden)*(line.product_uom_qty)/(line.purchase_line_id.product_uom_qty)

                        logger.warning("----Montos comparacion------")
                        logger.warning(line.monto_asiento)
                        logger.warning(precio_subtotal_soles)
                        logger.warning(" ")
                            # precio_subtotal_soles = line.purchase_line_id.precio_subtotal_soles*tc
                            # Si el monto en el movimiento es distinto al monto de la OC
                            # if line.monto_asiento != (line.purchase_line_id.price_subtotal*tc)*(line.product_uom_qty)/(line.purchase_line_id.product_uom_qty):

                        if round(line.monto_asiento,2) != round(precio_subtotal_soles,2):                  
                            line.product_price_update_before_done(
                                forced_qty=sum(
                                    [valued_move_line.product_uom_id._compute_quantity(valued_move_line.quantity, line.product_id.uom_id)
                                    for valued_move_line in line._get_in_move_lines()]) * -1,
                                is_new=True,
                            )
                            logger.warning("-----standard_price_correction_line 2-------")
                            self.env['account.move'].update_stock_move_line(line)

            if move_lines:
                self.env.cr.commit()
                
            movimientos_posteriores1=self.env['stock.move'].search([
                ('product_id', '=', producto),
                ('purchase_line_id', '=', False),
                ('date', '>=', move_date),
                ('state','=','done'),
                ('id', 'not in', move_lines.ids),
                ('company_id','=',company),
                ('location_id.usage','=','internal'),
                ('location_dest_id.usage','=','production')
            ])

            movimientos_posteriores = (movimientos_posteriores1).sorted(key=lambda x: x.date)

            logger.warning("------Movimientos posterior--------")
            logger.warning(movimientos_posteriores)

            for line in movimientos_posteriores:

                self.env['account.move'].update_stock_move_line(line)
            
            if movimientos_posteriores:
                self.env.cr.commit()
                
                # self.env.cr.execute(
                #     """
                #     SELECT coalesce(sum(value),0), coalesce(sum(quantity),0)
                #     FROM stock_valuation_layer svl
                #     left join stock_move sm on(sm.id = svl.stock_move_id)
                #     WHERE svl.company_id = %s and svl.product_id = %s and svl.stock_move_id is not null and sm.state = 'done'
                #     """,(move_lines[0].company_id.id,producto))
                # res2 = self.env.cr.fetchone()

                # Calculo de la cantidad de stock actual
            self.env.cr.execute(
                """
                select COALESCE(sum(svl.quantity),0) AS suma_qty
                FROM stock_valuation_layer svl
                left join stock_move sm on(sm.id = svl.stock_move_id)
                WHERE svl.company_id = %s and svl.product_id = %s and sm.state ='done' and svl.stock_move_id is not null
                """,(company,producto))
            res_cant_prom = self.env.cr.fetchone()

            # Calculo del monto del stock actual
            self.env.cr.execute(
                """
                select coalesce(sum(value),0), coalesce(sum(svl.quantity),0)
                FROM stock_valuation_layer svl
                left join stock_move sm on(sm.id = svl.stock_move_id)
                WHERE svl.company_id = %s and svl.product_id = %s and sm.state ='done' and svl.stock_move_id is not null
                """,(company,producto))
            res_monto_prom = self.env.cr.fetchone()

            # Calculo del monto de Ajuste
            # self.env.cr.execute(
            #     """
            #     select coalesce(sum(balance),0)
            #     from account_move_line aml 
            #     left join account_move am on (am.id=aml.move_id)
            #     left join account_account aa on (aa.id = aml.account_id)
            #     where aml.company_id = %s and aml.product_id = %s and am.stock_move_id is null and am.state = 'posted' and aa.is_inventory_account is true
            #     """,(company,producto))
            # res_ajuste_prom = self.env.cr.fetchone()

            self.env.cr.execute(
                """
                select COALESCE(sum(svl.value),0) AS valor_ajuste
                FROM stock_valuation_layer svl
                WHERE svl.company_id = %s and svl.product_id = %s and svl.stock_move_id is null
                """,(company,producto))
            res_ajuste_prom = self.env.cr.fetchone()
            
            std_price = ((res_monto_prom[0] or 0) + (res_ajuste_prom[0] or 0)) / (res_cant_prom[0] or 1)
            logger.warning("----precio_std-final---")
            logger.warning(res_monto_prom[0])
            logger.warning(res_ajuste_prom[0])
            logger.warning(res_cant_prom[0])
            logger.warning(std_price)

            #mov_productos_id = movimientos_posteriores.filtered(lambda x: x.product_id.id == producto)

            if move_lines or movimientos_posteriores:

                if move_lines:
                    var=move_lines[0]
                else:
                    var=movimientos_posteriores[0]

                if std_price > 0 and res_cant_prom[0]>0:
                    var.product_id.with_company(var.company_id.id).with_context(disable_auto_svl=True).sudo().write({'standard_price': std_price})
                    self.env.cr.commit() 