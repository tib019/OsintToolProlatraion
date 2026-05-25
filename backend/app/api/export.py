from __future__ import annotations

import csv
import io
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import case_service

router = APIRouter()


@router.get("/{case_id}/json")
async def export_json(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    state = await case_service.get_graph_state(db, case_id)

    payload = {
        "case": {
            "id": str(case.id),
            "name": case.name,
            "description": case.description,
            "tags": case.tags,
            "notes_md": case.notes_md,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
        },
        "nodes": [
            {
                "id": str(n.id),
                "entity_type": n.entity_type,
                "value": n.value,
                "label": n.label,
                "properties": n.properties,
                "pos_x": n.pos_x,
                "pos_y": n.pos_y,
                "created_at": n.created_at.isoformat(),
            }
            for n in state["nodes"]
        ],
        "edges": [
            {
                "id": str(e.id),
                "source_id": str(e.source_id),
                "target_id": str(e.target_id),
                "label": e.label,
                "transform_name": e.transform_name,
                "created_at": e.created_at.isoformat(),
            }
            for e in state["edges"]
        ],
    }

    content = json.dumps(payload, indent=2)
    filename = f"phantom_case_{case_id}.json"
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{case_id}/csv")
async def export_csv(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    state = await case_service.get_graph_state(db, case_id)

    output = io.StringIO()
    writer = csv.writer(output)

    # Nodes sheet
    writer.writerow(["=== NODES ==="])
    writer.writerow(["id", "entity_type", "value", "label", "pos_x", "pos_y", "created_at"])
    for n in state["nodes"]:
        writer.writerow([
            str(n.id),
            n.entity_type,
            n.value,
            n.label,
            n.pos_x,
            n.pos_y,
            n.created_at.isoformat(),
        ])

    writer.writerow([])

    # Edges sheet
    writer.writerow(["=== EDGES ==="])
    writer.writerow(["id", "source_id", "target_id", "label", "transform_name", "created_at"])
    for e in state["edges"]:
        writer.writerow([
            str(e.id),
            str(e.source_id),
            str(e.target_id),
            e.label,
            e.transform_name,
            e.created_at.isoformat(),
        ])

    output.seek(0)
    filename = f"phantom_case_{case_id}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{case_id}/pdf")
async def export_pdf(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    state = await case_service.get_graph_state(db, case_id)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
        from reportlab.lib import colors
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ReportLab is not installed",
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"PHANTOM — Case Report", styles["Title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"<b>Name:</b> {case.name}", styles["Normal"]))
    if case.description:
        story.append(Paragraph(f"<b>Description:</b> {case.description}", styles["Normal"]))
    if case.tags:
        story.append(Paragraph(f"<b>Tags:</b> {', '.join(case.tags)}", styles["Normal"]))
    story.append(
        Paragraph(f"<b>Created:</b> {case.created_at.strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"])
    )
    story.append(Spacer(1, 0.5 * cm))

    # Notes
    if case.notes_md:
        story.append(Paragraph("<b>Notes</b>", styles["Heading2"]))
        story.append(Paragraph(case.notes_md.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 0.5 * cm))

    # Nodes table
    story.append(Paragraph("<b>Graph Nodes</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * cm))

    nodes = state["nodes"]
    if nodes:
        node_data = [["Type", "Value", "Label", "Created At"]]
        for n in nodes:
            node_data.append([
                n.entity_type,
                n.value[:60] + ("..." if len(n.value) > 60 else ""),
                n.label[:40] + ("..." if len(n.label) > 40 else ""),
                n.created_at.strftime("%Y-%m-%d %H:%M"),
            ])
        node_table = Table(node_data, repeatRows=1)
        node_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(node_table)
    else:
        story.append(Paragraph("No nodes.", styles["Normal"]))

    story.append(Spacer(1, 0.5 * cm))

    # Edges table
    story.append(Paragraph("<b>Graph Edges</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * cm))

    edges = state["edges"]
    if edges:
        # Build a node id -> label map for readable display
        node_label_map = {str(n.id): n.label for n in nodes}
        edge_data = [["Source", "Target", "Label", "Transform", "Created At"]]
        for e in edges:
            edge_data.append([
                node_label_map.get(str(e.source_id), str(e.source_id))[:30],
                node_label_map.get(str(e.target_id), str(e.target_id))[:30],
                e.label[:30],
                e.transform_name[:30],
                e.created_at.strftime("%Y-%m-%d %H:%M"),
            ])
        edge_table = Table(edge_data, repeatRows=1)
        edge_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        story.append(edge_table)
    else:
        story.append(Paragraph("No edges.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)

    filename = f"phantom_case_{case_id}.pdf"
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{case_id}/svg")
async def export_svg(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate a simple force-layout SVG representation of the graph."""
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    state = await case_service.get_graph_state(db, case_id)
    nodes = state["nodes"]
    edges = state["edges"]

    width, height = 1200, 800
    cx, cy = width / 2, height / 2
    import math

    # Compute positions: use stored pos or arrange in circle
    node_positions: dict[str, tuple[float, float]] = {}
    n_count = len(nodes)
    for i, n in enumerate(nodes):
        if n.pos_x is not None and n.pos_y is not None:
            node_positions[str(n.id)] = (n.pos_x, n.pos_y)
        else:
            angle = (2 * math.pi * i / max(n_count, 1))
            r = min(cx, cy) * 0.7
            node_positions[str(n.id)] = (
                cx + r * math.cos(angle),
                cy + r * math.sin(angle),
            )

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'style="background:#0d0d1a;font-family:monospace">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">',
        '<polygon points="0 0, 10 3.5, 0 7" fill="#4ade80"/>',
        "</marker>",
        "</defs>",
    ]

    # Draw edges
    for e in edges:
        sx, sy = node_positions.get(str(e.source_id), (cx, cy))
        tx, ty = node_positions.get(str(e.target_id), (cx, cy))
        lines.append(
            f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" '
            f'stroke="#4ade80" stroke-width="1.5" stroke-opacity="0.6" '
            f'marker-end="url(#arrow)"/>'
        )
        mid_x = (sx + tx) / 2
        mid_y = (sy + ty) / 2
        lines.append(
            f'<text x="{mid_x:.1f}" y="{mid_y:.1f}" fill="#a3e635" font-size="10" '
            f'text-anchor="middle">{_escape_xml(e.label)}</text>'
        )

    # Draw nodes
    for n in nodes:
        x, y = node_positions[str(n.id)]
        lines.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="20" '
            f'fill="#1e1e3a" stroke="#7c3aed" stroke-width="2"/>'
        )
        label_short = n.label[:20] + ("…" if len(n.label) > 20 else "")
        lines.append(
            f'<text x="{x:.1f}" y="{y + 5:.1f}" fill="#e2e8f0" font-size="11" '
            f'text-anchor="middle">{_escape_xml(label_short)}</text>'
        )
        lines.append(
            f'<text x="{x:.1f}" y="{y + 35:.1f}" fill="#94a3b8" font-size="9" '
            f'text-anchor="middle">{_escape_xml(n.entity_type)}</text>'
        )

    lines.append("</svg>")
    content = "\n".join(lines)

    filename = f"phantom_case_{case_id}.svg"
    return Response(
        content=content,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{case_id}/png")
async def export_png(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Render PNG via Pillow from the SVG-like layout."""
    case = await case_service.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    state = await case_service.get_graph_state(db, case_id)
    nodes = state["nodes"]
    edges = state["edges"]

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pillow is not installed",
        )

    import math

    width, height = 1400, 900
    cx, cy = width / 2, height / 2

    img = Image.new("RGB", (width, height), color=(13, 13, 26))
    draw = ImageDraw.Draw(img)

    # Compute positions
    node_positions: dict[str, tuple[float, float]] = {}
    n_count = len(nodes)
    for i, n in enumerate(nodes):
        if n.pos_x is not None and n.pos_y is not None:
            node_positions[str(n.id)] = (n.pos_x, n.pos_y)
        else:
            angle = (2 * math.pi * i / max(n_count, 1))
            r = min(cx, cy) * 0.7
            node_positions[str(n.id)] = (
                cx + r * math.cos(angle),
                cy + r * math.sin(angle),
            )

    # Draw edges
    for e in edges:
        sx, sy = node_positions.get(str(e.source_id), (cx, cy))
        tx, ty = node_positions.get(str(e.target_id), (cx, cy))
        draw.line([(sx, sy), (tx, ty)], fill=(74, 222, 128), width=2)
        mid_x = int((sx + tx) / 2)
        mid_y = int((sy + ty) / 2)
        draw.text((mid_x, mid_y), e.label[:20], fill=(163, 230, 53))

    # Draw nodes
    r = 22
    for n in nodes:
        x, y = node_positions[str(n.id)]
        xi, yi = int(x), int(y)
        draw.ellipse(
            [(xi - r, yi - r), (xi + r, yi + r)],
            fill=(30, 30, 58),
            outline=(124, 58, 237),
            width=2,
        )
        label_short = n.label[:18] + ("…" if len(n.label) > 18 else "")
        draw.text((xi - r, yi + r + 4), label_short, fill=(226, 232, 240))
        draw.text((xi - r, yi + r + 18), n.entity_type[:16], fill=(148, 163, 184))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    filename = f"phantom_case_{case_id}.png"
    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _escape_xml(text: str) -> str:
    """Escape special characters for XML/SVG text nodes."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
