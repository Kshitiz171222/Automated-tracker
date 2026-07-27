"""
Builds docs/dashboard.xlsx - one Excel workbook with a separate sheet per
category (each category is independent - no cross-category combining).
Each sheet has: search index history, a trailing average, rolling growth %,
and an embedded dark-themed line chart, formatted like the original
Babycare-style analysis sheet.
"""
import csv
import glob
import os
import re

import openpyxl
from openpyxl.chart import LineChart, Reference
from openpyxl.drawing.text import CharacterProperties, ParagraphProperties
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.fill import ColorChoice
from openpyxl.styles import Font

DATA_DIR = "data"
MAX_TRAILING = 8  # rolling window, in weeks, once enough history exists


def slug_to_label(path):
    name = os.path.basename(path)
    name = re.sub(r"^trends_", "", name)
    return re.sub(r"\.csv$", "", name).replace("-", " ")


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def safe_sheet_name(name):
    # Excel sheet names: max 31 chars, no : \ / ? * [ ]
    cleaned = re.sub(r"[:\\/?*\[\]]", "", name)
    return cleaned[:31] or "Sheet"


def build_sheet(wb, label, rows):
    ws = wb.create_sheet(safe_sheet_name(label))
    headers = ["Date", "Search Index", "Trailing Average", "Rolling Growth %"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    n = len(rows)
    trailing = min(MAX_TRAILING, max(2, n // 2)) if n >= 4 else 0

    for i, r in enumerate(rows):
        row_idx = i + 2
        idx_val = float(r["search_index"]) if r.get("search_index") else ""
        ws.append([r["date"], idx_val, "", ""])

        if trailing and i >= trailing - 1:
            start = row_idx - trailing + 1
            ws[f"C{row_idx}"] = f"=AVERAGE(B{start}:B{row_idx})"
        if trailing and i >= trailing:
            prev_row = row_idx - trailing
            ws[f"D{row_idx}"] = (
                f"=IF(C{prev_row}=0,\"\",(C{row_idx}-C{prev_row})/C{prev_row})"
            )
            ws[f"D{row_idx}"].number_format = "0.0%"

    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 18

    if trailing and n > trailing:
        chart = LineChart()
        chart.style = 26  # built-in dark chart style
        chart.height = 9
        chart.width = 20

        data_ref = Reference(ws, min_col=4, min_row=1, max_row=1 + n)
        cats_ref = Reference(ws, min_col=1, min_row=2, max_row=1 + n)
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)

        chart.title = f"{label.upper()} SEARCH GROWTH TREND"
        title_para = chart.title.tx.rich.p[0]
        title_para.pPr = ParagraphProperties(
            defRPr=CharacterProperties(sz=1500, b=True, cap="all",
                                        solidFill=ColorChoice(srgbClr="FFFFFF"))
        )
        chart.graphical_properties = GraphicalProperties(solidFill="1F1F1F")

        ws.add_chart(chart, f"F2")


def main():
    os.makedirs("docs", exist_ok=True)
    files = sorted(glob.glob(f"{DATA_DIR}/trends_*.csv"))
    if not files:
        print("No data yet - skipping workbook export")
        return

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # drop the default blank sheet

    for path in files:
        rows = load_csv(path)
        if not rows:
            continue
        label = rows[0].get("category", slug_to_label(path))
        build_sheet(wb, label, rows)
        print(f"{label}: {len(rows)} rows")

    wb.save("docs/dashboard.xlsx")
    print(f"Workbook written to docs/dashboard.xlsx ({len(wb.sheetnames)} category sheets)")


if __name__ == "__main__":
    main()
