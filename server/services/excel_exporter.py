import os
import re
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

class ApiError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg

COND_MULT = {"NM": 1.0, "LP": 0.85, "MP": 0.70, "HP": 0.50}

def sanitize_sheet_name(name):
    clean = re.sub(r"[\\/*?:\[\]]", "", str(name or "Sin Expansion")).strip()
    return clean[:31] if clean else "General"

def export_excel_file(items, output_path, session_date=None):
    if not HAS_OPENPYXL:
        raise ApiError(500, "La librería openpyxl no está disponible en el servidor.")
    if session_date is None:
        session_date = datetime.now().strftime("%d/%m/%Y")

    wb = openpyxl.Workbook()
    ws_resumen = wb.active
    ws_resumen.title = "Resumen"

    # Estilos compartidos
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"), right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"), bottom=Side(style="thin", color="CBD5E1")
    )
    total_top_border = Side(style="thin", color="0F172A")
    total_bottom_border = Side(style="double", color="0F172A")
    total_border = Border(left=Side(style="thin", color="CBD5E1"), right=Side(style="thin", color="CBD5E1"),
                          top=total_top_border, bottom=total_bottom_border)

    by_set = {}
    for it in items:
        sname = (it.get("set") or "Sin Expansión").strip()
        by_set.setdefault(sname, []).append(it)

    headers_detail = [
        "ID Colección", "ID Carta", "Nombre", "Número", "Rareza",
        "Estado", "Cantidad", "Enlace Cardmarket",
        f"Precio Unit. {session_date} (€)", f"Valor Total {session_date} (€)"
    ]

    set_totals = {}

    # --- PESTAÑAS DETALLADAS DE CADA EXPANSIÓN ---
    for sname, set_items in by_set.items():
        sheet_title = sanitize_sheet_name(sname)
        ws = wb.create_sheet(sheet_title)
        ws.views.sheetView[0].showGridLines = True

        for col_num, h in enumerate(headers_detail, 1):
            cell = ws.cell(row=1, column=col_num, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

        r_idx = 2
        set_val = 0.0
        set_qty = 0

        for it in set_items:
            cond = (it.get("condition") or "NM").upper()
            mult = COND_MULT.get(cond, 1.0)
            base_p = float(it.get("price_eur") or 0.0)
            unit_p = round(base_p * mult, 2)
            qty = int(it.get("quantity") or 1)
            tot_p = round(unit_p * qty, 2)

            set_val += tot_p
            set_qty += qty

            url_val = it.get("cardmarket_url") or ""
            row_data = [
                it.get("uid"), it.get("id"), it.get("name"), it.get("number"),
                it.get("rarity"), cond, qty, "Ver en Cardmarket" if url_val else "",
                unit_p, tot_p
            ]

            is_even = (r_idx % 2 == 0)

            for c_idx, val in enumerate(row_data, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")
                
                if is_even:
                    cell.fill = zebra_fill

                if c_idx in [1, 2, 4, 5, 6]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif c_idx == 7:
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = "#,##0"
                elif c_idx in [9, 10]:
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = '#,##0.00 "€"'
                elif c_idx == 8 and url_val:
                    cell.hyperlink = url_val
                    cell.font = Font(name="Calibri", size=11, color="2563EB", underline="single")
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            ws.row_dimensions[r_idx].height = 22
            r_idx += 1

        # Auto-ajuste de ancho de columnas para la pestaña de expansión
        for col_idx in range(1, len(headers_detail) + 1):
            col_letter = get_column_letter(col_idx)
            max_len = 0
            for row_j in range(1, r_idx):
                cell_val = str(ws.cell(row=row_j, column=col_idx).value or "")
                if len(cell_val) > max_len:
                    max_len = len(cell_val)
            ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

        set_totals[sname] = {"qty": set_qty, "val": round(set_val, 2), "count": len(set_items)}

    # --- PESTAÑA PRINCIPAL DE RESUMEN ---
    ws_resumen.views.sheetView[0].showGridLines = True
    res_headers = ["Expansión", "Cartas Únicas", "Total Copias", f"Valor Total ({session_date})"]
    for col_num, h in enumerate(res_headers, 1):
        cell = ws_resumen.cell(row=1, column=col_num, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws_resumen.row_dimensions[1].height = 28

    r_idx = 2
    tot_cartas = 0
    tot_copias = 0
    tot_valor = 0.0

    for sname, info in sorted(set_totals.items(), key=lambda x: x[0]):
        is_even = (r_idx % 2 == 0)

        cell_s = ws_resumen.cell(row=r_idx, column=1, value=sname)
        cell_s.border = thin_border
        cell_s.alignment = Alignment(vertical="center")

        cell_u = ws_resumen.cell(row=r_idx, column=2, value=info["count"])
        cell_u.border = thin_border
        cell_u.alignment = Alignment(horizontal="center", vertical="center")

        cell_c = ws_resumen.cell(row=r_idx, column=3, value=info["qty"])
        cell_c.border = thin_border
        cell_c.alignment = Alignment(horizontal="right", vertical="center")
        cell_c.number_format = "#,##0"

        cell_v = ws_resumen.cell(row=r_idx, column=4, value=info["val"])
        cell_v.border = thin_border
        cell_v.alignment = Alignment(horizontal="right", vertical="center")
        cell_v.number_format = '#,##0.00 "€"'

        if is_even:
            cell_s.fill = zebra_fill
            cell_u.fill = zebra_fill
            cell_c.fill = zebra_fill
            cell_v.fill = zebra_fill

        ws_resumen.row_dimensions[r_idx].height = 22
        tot_cartas += info["count"]
        tot_copias += info["qty"]
        tot_valor += info["val"]
        r_idx += 1

    # Fila de TOTAL GENERAL
    tot_row = r_idx
    cell_tot_lbl = ws_resumen.cell(row=tot_row, column=1, value="TOTAL GENERAL")
    cell_tot_lbl.font = Font(name="Calibri", size=11, bold=True)
    cell_tot_lbl.border = total_border
    cell_tot_lbl.alignment = Alignment(vertical="center")

    cell = ws_resumen.cell(row=tot_row, column=2, value=tot_cartas)
    cell.font = Font(name="Calibri", size=11, bold=True)
    cell.border = total_border
    cell.alignment = Alignment(horizontal="center", vertical="center")

    cell = ws_resumen.cell(row=tot_row, column=3, value=tot_copias)
    cell.font = Font(name="Calibri", size=11, bold=True)
    cell.border = total_border
    cell.alignment = Alignment(horizontal="right", vertical="center")
    cell.number_format = "#,##0"

    cell = ws_resumen.cell(row=tot_row, column=4, value=round(tot_valor, 2))
    cell.font = Font(name="Calibri", size=11, bold=True)
    cell.border = total_border
    cell.alignment = Alignment(horizontal="right", vertical="center")
    cell.number_format = '#,##0.00 "€"'
    ws_resumen.row_dimensions[tot_row].height = 26

    # Auto-ajuste de ancho de columnas para el Resumen
    for col_idx in range(1, 5):
        col_letter = get_column_letter(col_idx)
        max_len = max(len(str(ws_resumen.cell(row=row_j, column=col_idx).value or "")) for row_j in range(1, r_idx + 1))
        ws_resumen.column_dimensions[col_letter].width = max(max_len + 6, 18)

    wb.save(output_path)