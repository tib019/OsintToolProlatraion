from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.transforms.base import BaseTransform


class TransformRegistry:
    """
    Central registry that maps transform names to their instances and allows
    lookup by entity type.

    Transforms self-register via :meth:`register` (typically called from their
    module's top-level code or from an explicit bootstrap function).
    """

    def __init__(self) -> None:
        self._transforms: dict[str, "BaseTransform"] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, transform: "BaseTransform") -> None:
        """Register a transform instance.

        The transform's ``name`` attribute is used as the key.  Registering
        a transform with a duplicate name overwrites the previous entry.

        Args:
            transform: An instance of :class:`~app.transforms.base.BaseTransform`.
        """
        self._transforms[transform.name] = transform

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    def get_by_name(self, name: str) -> "BaseTransform | None":
        """Return the transform registered under *name*, or ``None``.

        Args:
            name: The unique name of the transform.

        Returns:
            The matching :class:`~app.transforms.base.BaseTransform` instance,
            or ``None`` if no transform with that name exists.
        """
        return self._transforms.get(name)

    def get_for_entity_type(self, entity_type: str) -> list["BaseTransform"]:
        """Return all transforms that accept *entity_type* as input.

        Each transform declares which entity types it supports via its
        ``input_entity_types`` attribute (an iterable of strings).

        Args:
            entity_type: The entity type string, e.g. ``"email"``, ``"phone"``.

        Returns:
            A list of matching transforms, ordered by registration order.
        """
        return [
            t
            for t in self._transforms.values()
            if entity_type in t.input_types
        ]

    def all_transforms(self) -> list["BaseTransform"]:
        """Return every registered transform in insertion order."""
        return list(self._transforms.values())

    def __len__(self) -> int:
        return len(self._transforms)

    def __repr__(self) -> str:
        names = list(self._transforms.keys())
        return f"<TransformRegistry transforms={names}>"


# ---------------------------------------------------------------------------
# Global singleton — import this instance everywhere
# ---------------------------------------------------------------------------

registry = TransformRegistry()
