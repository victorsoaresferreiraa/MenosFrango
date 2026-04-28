"""
Geração de relatório mensal em PDF com ReportLab.
"""

import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
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

from app.core.logging import get_logger

logger = get_logger(__name__)

# Cores da marca Athletic AI
PRIMARY = colors.HexColor("#3B82F6")  # Azul
SECONDARY = colors.HexColor("#10B981")  # Verde
DARK = colors.HexColor("#1F2937")
GRAY = colors.HexColor("#6B7280")
LIGHT = colors.HexColor("#F9FAFB")


def generate_monthly_report(data: Dict[str, Any]) -> bytes:
    """
    Gera relatório mensal em PDF.
    Retorna bytes do PDF gerado.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Athletic AI — Relatório Mensal",
    )

    styles = getSampleStyleSheet()
    story = []

    # Estilos customizados
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=PRIMARY,
        spaceAfter=0.3 * cm,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=DARK,
        spaceBefore=0.5 * cm,
        spaceAfter=0.2 * cm,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=11,
        textColor=DARK,
        leading=16,
    )

    # ===========================================================
    # Cabeçalho
    # ===========================================================
    user = data.get("user", {})
    month_name = data.get("month_name", "")

    story.append(Paragraph("🏋️ Athletic AI", title_style))
    story.append(Paragraph(f"Relatório Mensal — {month_name}", heading_style))
    story.append(
        Paragraph(
            f"Gerado em: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC",
            ParagraphStyle("small", parent=styles["Normal"], fontSize=9, textColor=GRAY),
        )
    )
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=0.5 * cm))

    # ===========================================================
    # Dados do Usuário
    # ===========================================================
    story.append(Paragraph("👤 Perfil", heading_style))
    user_data = [
        ["Nome", user.get("name", "—")],
        ["Objetivo", user.get("goal", "—").capitalize()],
        ["Nível", user.get("level", "—").capitalize()],
        ["Peso Atual", f"{user.get('weight_kg', '—')} kg"],
    ]
    user_table = Table(user_data, colWidths=[5 * cm, 10 * cm])
    user_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(user_table)
    story.append(Spacer(1, 0.5 * cm))

    # ===========================================================
    # KPIs de Treino
    # ===========================================================
    workouts = data.get("workouts", {})
    story.append(Paragraph("🏋️ Resumo de Treinos", heading_style))

    kpi_data = [
        ["Métrica", "Valor"],
        ["Total de treinos", str(workouts.get("total", 0))],
        ["Séries totais", str(workouts.get("total_sets", 0))],
        ["Volume total (kg)", f"{workouts.get('total_volume', 0):,.0f}"],
        ["Exercícios únicos", str(workouts.get("unique_exercises", 0))],
    ]
    kpi_table = Table(kpi_data, colWidths=[10 * cm, 5 * cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.5 * cm))

    # ===========================================================
    # KPIs Nutricionais
    # ===========================================================
    nutrition = data.get("nutrition", {})
    if nutrition:
        story.append(Paragraph("🥗 Resumo Nutricional", heading_style))
        nut_data = [
            ["Métrica", "Média Diária"],
            ["Calorias", f"{nutrition.get('avg_calories', 0):.0f} kcal"],
            ["Proteína", f"{nutrition.get('avg_protein', 0):.0f} g"],
            ["Carboidratos", f"{nutrition.get('avg_carbs', 0):.0f} g"],
            ["Gordura", f"{nutrition.get('avg_fat', 0):.0f} g"],
        ]
        nut_table = Table(nut_data, colWidths=[10 * cm, 5 * cm])
        nut_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ]))
        story.append(nut_table)
        story.append(Spacer(1, 0.5 * cm))

    # ===========================================================
    # Recomendações IA
    # ===========================================================
    recommendations = data.get("recommendations", [])
    if recommendations:
        story.append(Paragraph("🤖 Recomendações da IA", heading_style))
        for i, rec in enumerate(recommendations, 1):
            story.append(
                Paragraph(
                    f"{i}. {rec}",
                    ParagraphStyle(
                        "rec",
                        parent=styles["Normal"],
                        fontSize=11,
                        leading=18,
                        leftIndent=0.5 * cm,
                        spaceBefore=0.2 * cm,
                    ),
                )
            )
        story.append(Spacer(1, 0.5 * cm))

    # ===========================================================
    # Rodapé
    # ===========================================================
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY))
    story.append(
        Paragraph(
            "Athletic AI — Plataforma de Acompanhamento de Treinos e Nutrição | Modo IA: A (Offline)",
            ParagraphStyle("footer", parent=styles["Normal"], fontSize=8, textColor=GRAY, alignment=1),
        )
    )

    doc.build(story)
    return buffer.getvalue()
