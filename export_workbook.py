"""
Builds docs/dashboard.xlsx - one Excel workbook with a separate sheet per
category (each category is independent - no cross-category combining).
Each sheet has: search index history, a trailing average, rolling growth %,
and an embedded line chart of the search index over time.
"""
import csv
import glob
import os
import re

import openpyxl
from openpyxl.chart import LineChart, Reference
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
    cleaned = re.sub(r"[:\\/?*\[\]]", "", name)
    return cleaned[:31] or "Sheet"


def build_sheet(wb, label, rows):
    ws = wb.create_sheet(safe_sheet_name(label))
    ws.append(["Date", "Search Index", "Trailing Average", "Rolling Growth %"])
    for cell in ws[1]:
        cell.font = Font(bold=True)

    n = len(rows)
    trailing = min(MAX_TRAILING, max(2, n // 2)) if n >= 4 else 0

    for i, r in enumerate(rows):
        row_idx = i + 2
        idx_val = float(r["search_index"]) if r.get("search_index") else None
        ws.append([r["date"], idx_val, None, None])

        if trailing and i >= trailing - 1:
            start = row_idx - trailing + 1
            ws[f"C{row_idx}"] = f"=AVERAGE(B{start}:B{row_idx})"
        if trailing and i >= trailing:
            prev_row = row_idx - trailing
            ws[f"D{row_idx}"] = f"=IF(C{prev_row}=0,\"\",(C{row_idx}-C{prev_row})/C{prev_row})"
            ws[f"D{row_idx}"].number_format = "0.0%"

    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 18

    # --- chart: Search Index over time. One series, dates on the x-axis. ---
    if n >= 2:
        chart = LineChart()
        chart.title = f"{label.title()} - Search Index Over Time"
        chart.style = 26
        chart.height = 9
        chart.width = 20
        chart.y_axis.title = "Search Index"
        chart.x_axis.title = "Date"

        data_ref = Reference(ws, min_col=2, min_row=1, max_row=n + 1)  # incl. header
        cats_ref = Reference(ws, min_col=1, min_row=2, max_row=n + 1)  # dates only
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)

        ws.add_chart(chart, "F2")


def main():
    os.makedirs("docs", exist_ok=True)
    files = sorted(glob.glob(f"{DATA_DIR}/trends_*.csv"))
    if not files:
        print("No data yet - skipping workbook export")
        return

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

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
