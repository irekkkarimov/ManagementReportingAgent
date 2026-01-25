import pandas as pd


class ExcelReportGenerator:
    def generate(self, table: pd.DataFrame, output_path: str):
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            table.to_excel(writer, sheet_name="Management Report")

            workbook = writer.book
            worksheet = writer.sheets["Management Report"]

            money_fmt = workbook.add_format({"num_format": "#,##0.00"})
            worksheet.set_column(1, len(table.columns), 15, money_fmt)
            worksheet.freeze_panes(1, 1)