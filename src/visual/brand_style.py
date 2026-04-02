"""
Identidade visual por categoria (selo, gradiente, vibe).
"""

from __future__ import annotations

from typing import TypedDict


class BrandStyle(TypedDict):
    label: str
    gradient_top: tuple[int, int, int]
    gradient_bottom: tuple[int, int, int]
    accent: tuple[int, int, int]
    badge_bg: tuple[int, int, int]
    vibe: str


def topic_to_label(topic: str) -> str:
    m = {
        "ai": "AI",
        "big_tech": "BIG TECH",
        "cybersecurity": "SECURITY",
        "startups": "STARTUP",
        "regulation": "POLICY",
        "gadgets": "GADGETS",
        "social_media": "SOCIAL",
        "software": "DEV",
        "other": "TECH",
    }
    return m.get(topic, "TECH")


def get_style(topic: str) -> BrandStyle:
    """Retorna paleta e rótulo para o selo do template."""
    if topic == "ai":
        return BrandStyle(
            label="AI",
            gradient_top=(35, 25, 60),
            gradient_bottom=(12, 18, 45),
            accent=(130, 110, 255),
            badge_bg=(88, 70, 200),
            vibe="futurista clean",
        )
    if topic == "big_tech":
        return BrandStyle(
            label="BIG TECH",
            gradient_top=(28, 28, 30),
            gradient_bottom=(10, 10, 12),
            accent=(240, 240, 245),
            badge_bg=(55, 55, 58),
            vibe="corporativo",
        )
    if topic == "startups":
        return BrandStyle(
            label="STARTUP",
            gradient_top=(55, 30, 12),
            gradient_bottom=(25, 12, 6),
            accent=(255, 160, 60),
            badge_bg=(200, 95, 30),
            vibe="energético",
        )
    if topic == "cybersecurity":
        return BrandStyle(
            label="SECURITY",
            gradient_top=(8, 22, 18),
            gradient_bottom=(4, 10, 12),
            accent=(80, 220, 180),
            badge_bg=(12, 90, 75),
            vibe="alerta técnico",
        )
    if topic == "gadgets":
        return BrandStyle(
            label="GADGETS",
            gradient_top=(22, 28, 38),
            gradient_bottom=(8, 12, 20),
            accent=(100, 180, 255),
            badge_bg=(40, 100, 160),
            vibe="produto",
        )
    return BrandStyle(
        label="TECH",
        gradient_top=(18, 22, 38),
        gradient_bottom=(6, 8, 18),
        accent=(180, 200, 255),
        badge_bg=(50, 70, 130),
        vibe="editorial",
    )
