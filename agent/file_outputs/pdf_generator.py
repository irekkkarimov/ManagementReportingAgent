import pandas as pd
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Регистрируем шрифт с поддержкой кириллицы
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # путь к .ttf файлу шрифта


class PDFReportGenerator:
    def generate(self, df: pd.DataFrame, output_path: str, title: str = "Management Report"):
        df = df.copy()
        df.reset_index(inplace=True)

        # данные для PDF-таблицы
        table_data = [df.columns.tolist()] + df.values.tolist()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        table = Table(table_data, repeatRows=1)

        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("FONTNAME", (0, 0), (-1, -1), "Arial"),  # применяем шрифт
                ]
            )
        )

        doc.build([table])