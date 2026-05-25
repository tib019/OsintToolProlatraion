from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(1024), nullable=False)
    label: Mapped[str] = mapped_column(String(512), nullable=False)
    properties: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    pos_x: Mapped[Optional[float]] = mapped_column(nullable=True)
    pos_y: Mapped[Optional[float]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    case: Mapped["Case"] = relationship(back_populates="nodes")  # noqa: F821

    # Edges where this node is the source
    outgoing_edges: Mapped[list["GraphEdge"]] = relationship(
        back_populates="source_node",
        foreign_keys="GraphEdge.source_id",
        cascade="all, delete-orphan",
    )
    # Edges where this node is the target
    incoming_edges: Mapped[list["GraphEdge"]] = relationship(
        back_populates="target_node",
        foreign_keys="GraphEdge.target_id",
        cascade="all, delete-orphan",
    )


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    transform_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    case: Mapped["Case"] = relationship(back_populates="edges")  # noqa: F821
    source_node: Mapped["GraphNode"] = relationship(
        back_populates="outgoing_edges", foreign_keys=[source_id]
    )
    target_node: Mapped["GraphNode"] = relationship(
        back_populates="incoming_edges", foreign_keys=[target_id]
    )
