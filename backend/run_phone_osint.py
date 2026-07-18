#!/usr/bin/env python3
"""
Standalone-Runner für die PHANTOM Phone-OSINT-Transforms.
Führt die Phone-Transforms gegen eine einzelne Nummer aus,
ohne den vollen Docker-Stack (Postgres/Redis/FastAPI).

Usage:
    python run_phone_osint.py "+49XXXXXXXXXX"
"""
import asyncio
import json
import os
import sys
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.transforms.base import Entity, EntityType
from app.transforms.phone.phoneinfoga import PhoneInfogaTransform
from app.transforms.phone.platform_checker import PlatformRegistrationTransform
from app.transforms.phone.social_linker import SocialProfileLinkerTransform
from app.transforms.phone.cnam_lookup import CNAMLookupTransform
from app.transforms.phone.leak_check import LeakCheckTransform

# API-Keys aus der Umgebung (optional). Ohne Keys laufen die
# Transforms mit reduzierter Funktionalität.
API_KEYS = {
    "NUMVERIFY_API_KEY": os.getenv("NUMVERIFY_API_KEY", ""),
    "OPENCNAM_SID": os.getenv("OPENCNAM_SID", ""),
    "OPENCNAM_AUTH_TOKEN": os.getenv("OPENCNAM_AUTH_TOKEN", ""),
    "HIBP_API_KEY": os.getenv("HIBP_API_KEY", ""),
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
}

TRANSFORMS = [
    PhoneInfogaTransform(),
    PlatformRegistrationTransform(),
    SocialProfileLinkerTransform(),
    CNAMLookupTransform(),
    LeakCheckTransform(),
]


async def main(number: str):
    entity = Entity(type=EntityType.PHONE_NUMBER, value=number)
    print(f"\n{'='*60}\nPHANTOM Phone-OSINT  →  {number}\n{'='*60}")

    for tf in TRANSFORMS:
        print(f"\n── {tf.name} ──")
        result = await tf.execute(entity, API_KEYS)
        print(f"   ({result.duration_ms} ms)")
        if result.error:
            print(f"   FEHLER: {result.error}")
        if result.metadata:
            print("   metadata:")
            print("   " + json.dumps(result.metadata, indent=2, default=str).replace("\n", "\n   "))
        if not result.entities:
            print("   → keine Entities gefunden")
        for e in result.entities:
            props = {k: v for k, v in e.properties.items() if v not in ("", [], None)}
            print(f"   • [{e.type.value}] {e.label or e.value}")
            for k, v in props.items():
                print(f"        {k}: {v}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_phone_osint.py \"+49XXXXXXXXXX\"")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
