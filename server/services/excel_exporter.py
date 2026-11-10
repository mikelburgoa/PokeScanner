"""Exportación silenciosa de la colección a Excel con OpenPyXL."""
from datetime import datetime
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from core.errors import ApiError


def export_excel_file(collection: list, output_path: str) -> str:
    """Genera un archivo Excel profesional con la colección actual.

    Devuelve la fecha/hora de actualización formateada.
    """
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Colección Pokémon"
        ws.views.sheetView[0].showGridLines = True

        # Paleta de colores Dark / Slate Profesional
        COLOR_HEADER_BG = "1E293B"      # Slate 800
        COLOR_HEADER_TEXT = "F8FAFC"    # Slate 50
        COLOR_ROW_ALT = "F8FAFC"        # Slate 50 para filas alternas
        COLOR_BORDER = "E2E8F0"         # Slate 200

        # Estilos
        font_title = Font(name="Calibri", size=16, bold=True, color="0F172A")
        font_subtitle = Font(name="Calibri", size=10, italic=True, color="64748B")
        font_header = Font(name="Calibri", size=11, bold=True, color=COLOR_HEADER_TEXT)
        font_data = Font(name="Calibri", size=11, color="0F172A")
        font_link = Font(name="Calibri", size=11, color="2563EB", underline="single")
        font_total = Font(name="Calibri", size=11, bold=True, color="0F172A")

        fill_header = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
        fill_alt = PatternFill(start_color=COLOR_ROW_ALT, end_color=COLOR_ROW_ALT, fill_type="solid")

        thin_side = Side(border_style="thin", color=COLOR_BORDER)
        border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        border_total = Border(top=Side(border_style="thin", color="0F172A"), bottom=Side(border_style="double", color="0F172A"))

        # Encabezado principal
        ws["A1"] = "PokeScanner - Colección de Cartas"
        ws["A1"].font = font_title

        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        ws["A2"] = f"Última actualización: {now_str} | Total ítems: {len(collection)}"
        ws["A2"].font = font_subtitle

        # Encabezados de tabla (Fila 4)
        headers = [
            "Nombre", "Expansión", "Número", "Rareza", 
            "Estado", "Cantidad", "Precio EUR (€)", "Precio USD ($)", 
            "Valor Total (€)", "Cardmarket", "TCGplayer"
        ]

        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_idx, value=header)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal="center" if col_idx not in (1, 2) else "left", vertical="center")

        ws.row_dimensions[4].height = 25

        # Datos de la colección
        start_row = 5
        for i, card in enumerate(collection):
            row_idx = start_row + i
            qty = int(card.get("quantity") or 1)
            price_eur = float(card.get("price_eur") or card.get("price") or 0.0)
            price_usd = float(card.get("price_usd") or card.get("usd") or 0.0)

            # Cálculo de multiplicador por estado
            cond = card.get("condition", "NM")
            multiplier = 0.85 if cond == "LP" else 0.70 if cond == "MP" else 0.50 if cond == "HP" else 1.0
            total_val = price_eur * multiplier * qty

            ws.cell(row=row_idx, column=1, value=card.get("name", "")).font = font_data
            ws.cell(row=row_idx, column=2, value=card.get("set", "Sin Expansión")).font = font_data
            ws.cell(row=row_idx, column=3, value=card.get("number", "")).font = font_data
            ws.cell(row=row_idx, column=4, value=card.get("rarity", "")).font = font_data
            
            c_cond = ws.cell(row=row_idx, column=5, value=cond)
            c_cond.font = font_data
            c_cond.alignment = Alignment(horizontal="center")

            c_qty = ws.cell(row=row_idx, column=6, value=qty)
            c_qty.font = font_data
            c_qty.alignment = Alignment(horizontal="right")

            c_eur = ws.cell(row=row_idx, column=7, value=price_eur)
            c_eur.font = font_data
            c_eur.number_format = "#,##0.00 €"

            c_usd = ws.cell(row=row_idx, column=8, value=price_usd)
            c_usd.font = font_data
            c_usd.number_format = "$#,##0.00"

            c_tot = ws.cell(row=row_idx, column=9, value=total_val)
            c_tot.font = font_data
            c_tot.number_format = "#,##0.00 €"

            # Enlaces
            cm_url = card.get("cardmarket_url") or f"https://www.cardmarket.com/es/Pokemon/Products/Singles?searchString={card.get('name','')}"
            tcg_url = card.get("tcgplayer_url") or f"https://www.tcgplayer.com/search/pokemon/product?q={card.get('name','')}"

            c_cm = ws.cell(row=row_idx, column=10, value="Ver en Cardmarket")
            c_cm.hyperlink = cm_url
            c_cm.font = font_link

            c_tcg = ws.cell(row=row_idx, column=11, value="Ver en TCGplayer")
            c_tcg.hyperlink = tcg_url
            c_tcg.font = font_link

            # Aplicar bordes y fondo alterno
            for col_idx in range(1, 12):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = border_all
                if i % 2 == 1:
                    cell.fill = fill_alt

            ws.row_dimensions[row_idx].height = 20

        # Fila de Totales
        end_row = start_row + len(collection)
        if len(collection) > 0:
            ws.cell(row=end_row, column=1, value="TOTAL").font = font_total
            
            c_total_qty = ws.cell(row=end_row, column=6, value=f"=SUM(F{start_row}:F{end_row-1})")
            c_total_qty.font = font_total
            c_total_qty.border = border_total

            c_total_val = ws.cell(row=end_row, column=9, value=f"=SUM(I{start_row}:I{end_row-1})")
            c_total_val.font = font_total
            c_total_val.number_format = "#,##0.00 €"
            c_total_val.border = border_total

        # Ajuste automático del ancho de columnas
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if cell.row in (1, 2):
                    continue
                max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        # Guardar en la ruta indicada
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        wb.save(out_file)
        return now_str

    except Exception as e:
        raise ApiError(500, f"Error generando Excel: {e}")