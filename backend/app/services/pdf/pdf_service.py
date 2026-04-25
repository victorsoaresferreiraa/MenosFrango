"""
Serviço de geração de relatórios mensais em PDF usando ReportLab.
"""
import io
import logging
from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)

# Paleta de cores Athletic AI
PRIMARY = colors.HexColor("#6366f1")    # Indigo
SECONDARY = colors.HexColor("#10b981")  # Verde
DARK = colors.HexColor("#1f2937")
LIGHT_GRAY = colors.HexColor("#f3f4f6")


class PDFService:
    """Gera relatórios mensais em PDF."""

    def generate_monthly_report(
        self,
        user_name: str,
        month: date,
        workout_summary: dict,
        nutrition_summary: dict,
        recommendations: list[str],
    ) -> bytes:
        """
        Gera relatório mensal completo em PDF.
        Retorna bytes do PDF pronto para armazenar/enviar.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = self._get_styles()
        story = []

        # ── Cabeçalho ─────────────────────────────────────
        story.append(Paragraph("🏋️ Athletic AI", styles["title"]))
        story.append(Paragraph("Relatório Mensal de Progresso", styles["subtitle"]))
        month_str = month.strftime("%B/%Y").capitalize()
        story.append(Paragraph(f"Atleta: {user_name} | Período: {month_str}", styles["info"]))
        story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
        story.append(Spacer(1, 0.5 * cm))

        # ── Resumo de treinos ──────────────────────────────
        story.append(Paragraph("📊 Resumo de Treinos", styles["section"]))
        story.append(Spacer(1, 0.3 * cm))

        workout_data = [
            ["Métrica", "Valor"],
            ["Total de sessões", str(workout_summary.get("total_sessions", 0))],
            ["Exercícios únicos", str(workout_summary.get("unique_exercises", 0))],
            ["Volume total (kg)", f"{workout_summary.get('total_volume', 0):.0f}kg"],
            ["Série mais frequente", workout_summary.get("top_muscle_group", "—")],
        ]
        story.append(self._build_table(workout_data))
        story.append(Spacer(1, 0.5 * cm))

        # ── Resumo nutricional ─────────────────────────────
        story.append(Paragraph("🥗 Resumo Nutricional", styles["section"]))
        story.append(Spacer(1, 0.3 * cm))

        nutrition_data = [
            ["Métrica", "Média Diária", "Meta"],
            ["Calorias", f"{nutrition_summary.get('avg_calories', 0):.0f}kcal",
             f"{nutrition_summary.get('target_calories', 0):.0f}kcal"],
            ["Proteína", f"{nutrition_summary.get('avg_protein', 0):.0f}g",
             f"{nutrition_summary.get('target_protein', 0):.0f}g"],
            ["Carboidratos", f"{nutrition_summary.get('avg_carbs', 0):.0f}g", "—"],
            ["Gordura", f"{nutrition_summary.get('avg_fat', 0):.0f}g", "—"],
            ["Aderência", f"{nutrition_summary.get('adherence_pct', 0):.0f}%", "≥80%"],
        ]
        story.append(self._build_table(nutrition_data, has_header=True))
        story.append(Spacer(1, 0.5 * cm))

        # ── Recomendações da IA ────────────────────────────
        story.append(Paragraph("🤖 Recomendações Personalizadas", styles["section"]))
        story.append(Spacer(1, 0.3 * cm))

        for i, rec in enumerate(recommendations[:8], 1):
            story.append(Paragraph(f"{i}. {rec}", styles["bullet"]))
            story.append(Spacer(1, 0.15 * cm))

        # ── Rodapé ────────────────────────────────────────
        story.append(Spacer(1, 1 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
        story.append(Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | Athletic AI",
            styles["footer"],
        ))

        doc.build(story)
        return buffer.getvalue()

    def _get_styles(self) -> dict:
        """Retorna estilos customizados para o relatório."""
        base = getSampleStyleSheet()
        return {
            "title": ParagraphStyle(
                "Title",
                parent=base["Title"],
                fontSize=24,
                textColor=PRIMARY,
                alignment=TA_CENTER,
                spaceAfter=4,
            ),
            "subtitle": ParagraphStyle(
                "Subtitle",
                parent=base["Normal"],
                fontSize=14,
                textColor=DARK,
                alignment=TA_CENTER,
                spaceAfter=6,
            ),
            "info": ParagraphStyle(
                "Info",
                parent=base["Normal"],
                fontSize=10,
                textColor=colors.gray,
                alignment=TA_CENTER,
                spaceAfter=12,
            ),
            "section": ParagraphStyle(
                "Section",
                parent=base["Heading2"],
                fontSize=13,
                textColor=PRIMARY,
                spaceBefore=8,
                spaceAfter=4,
            ),
            "bullet": ParagraphStyle(
                "Bullet",
                parent=base["Normal"],
                fontSize=10,
                leftIndent=10,
                textColor=DARK,
            ),
            "footer": ParagraphStyle(
                "Footer",
                parent=base["Normal"],
                fontSize=8,
                textColor=colors.gray,
                alignment=TA_CENTER,
            ),
        }

    def _build_table(self, data: list[list], has_header: bool = True) -> Table:
        """Constrói tabela formatada."""
        col_widths = [6 * cm] + [4 * cm] * (len(data[0]) - 1)
        table = Table(data, colWidths=col_widths)

        style = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY if has_header else LIGHT_GRAY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white if has_header else DARK),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]
        table.setStyle(TableStyle(style))
        return table


# Instância singleton
pdf_service = PDFService()
