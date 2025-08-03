from odoo.tools.misc import xlsxwriter
from io import BytesIO
from collections import defaultdict


class ReportConsumptionXlsx:
    def __init__(self, data, cursor):
        self.moves = data
        self.cursor = cursor

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        style_header = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 10,
            'bold': True,
            'border': 1
        })
        merge_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
        })
        style_number = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
        })
        style_number_bold = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'bold': True
        })
        style_content = workbook.add_format({
            'valign': 'vcenter',
            'font_size': 10,
            'bold': True
        })

        ws = workbook.add_worksheet("Reporte de consumos")
        ws.set_column('A:A', 40)  # Categoría
        ws.set_column('B:B', 100)  # Centro de costos
        ws.set_column('C:C', 15)  # Importe en soles
        ws.set_column('D:D', 15)  # Importe en dólares

        # Encabezados
        ws.write(0, 0, 'Categoría', style_header)
        ws.write(0, 1, 'Centro de costo', style_header)
        ws.write(0, 2, 'Importe en soles', style_header)
        ws.write(0, 3, 'Importe en dólares', style_header)
        ws.freeze_panes(1, 0)

        root_categories = self.cursor['product.category'].sudo().search([('parent_id', '=', False)])
        category_data = {category.id: defaultdict(lambda: [0.0, 0.0]) for category in root_categories}

        usd_currency = self.cursor['res.currency'].search([('name', '=', 'USD'), ('active', '=', True)], limit = 1)
        pen_currency = self.cursor['res.currency'].search([('name', '=', 'PEN'), ('active', '=', True)], limit=1)

        for move in self.moves:
            account_analytic_id = list(move.analytic_distribution.keys())[-1] if move.analytic_distribution else None
            account_analytic = self.cursor['account.analytic.account'].browse(int(account_analytic_id))
            category = move.product_id.categ_id

            while category and category.parent_id:
                category = category.parent_id

            if category and category.id in category_data:
                center_name = account_analytic.display_name

                amount_usd = pen_currency._convert(
                    from_amount=move.monto_asiento,
                    to_currency=usd_currency,
                    company=self.cursor.company.id,
                    date=move.date,
                    round=True
                )

                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'production':
                    category_data[category.id][center_name][0] += move.monto_asiento or 0.0
                    category_data[category.id][center_name][1] += amount_usd
                elif move.location_id.usage == 'production' and move.location_dest_id.usage == 'internal':
                    category_data[category.id][center_name][0] -= move.monto_asiento or 0.0
                    category_data[category.id][center_name][1] -= amount_usd

        row = 1
        for category in root_categories:
            ceco = category_data.get(category.id, {})
            start_row = row
            total_amount_pen = 0.0
            total_amount_usd = 0.0

            for name, amount, in ceco.items():
                ws.write(row, 1, name)
                ws.write(row, 2, amount[0], style_number)
                ws.write(row, 3, amount[1], style_number)
                total_amount_pen += amount[0]
                total_amount_usd += amount[1]
                row += 1
            
            if start_row != row:
                ws.merge_range(start_row, 0, row - 1, 0, category.name, merge_format)

            if ceco:
                ws.write(row, 1, 'Total', style_content)
                ws.write_number(row, 2, total_amount_pen, style_number_bold)
                ws.write_number(row, 3, total_amount_usd, style_number_bold)
                row += 2

        workbook.close()
        output.seek(0)
        return output.read()
