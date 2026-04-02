"""
Entrada principal: pipeline editorial `select_and_post` (padrão) e modos legados.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Garante que `src/` está no path quando executado como script
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import config
from utils.logger import setup_logging

USE_MOCK_FOR_POST_TEST = False

DEFAULT_TEST_CAPTION = (
    "Post de teste do agente — conteúdo fixo para validar a publicação no Instagram. "
    "#Teste #AgentInstagram #Tech"
)

PROJECT_ROOT = config.PROJECT_ROOT
DEFAULT_IMAGE_PATH = PROJECT_ROOT / "assets" / "default_post.png"


def _run_mock_post() -> None:
    from publish.instagram_poster import InstagramPoster
    from utils.safe_log import sanitize_url_for_log

    poster = InstagramPoster()
    caption = DEFAULT_TEST_CAPTION
    print(f"Modo mock: {caption}")

    if config.DEFAULT_POST_IMAGE_URL:
        image_url = config.DEFAULT_POST_IMAGE_URL
        print("Usando DEFAULT_POST_IMAGE_URL.")
    else:
        from content.image_generator import ImageGenerator

        ig = ImageGenerator()
        print(f"Upload local: {DEFAULT_IMAGE_PATH}")
        image_url = ig.upload_local_file_to_cloudinary(str(DEFAULT_IMAGE_PATH))

    if not image_url:
        print("Sem URL de imagem.")
        return
    ok = poster.post_to_instagram(image_url, caption)
    print("OK" if ok else "Falha")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Agente Instagram — seleção editorial multi-fonte e publicação."
    )
    p.add_argument(
        "--mode",
        default="select_and_post",
        choices=(
            "select_and_post",
            "rotate",
            "news",
            "curiosity",
            "trend",
            "mock_post",
        ),
        help="select_and_post = pipeline completo (padrão); rotate = legado 3 tipos; mock_post = só IG",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa fetch+ranking+legendas+prompt de imagem; não gera imagem nem publica.",
    )
    return p


def main() -> None:
    setup_logging()
    args = build_parser().parse_args()

    if USE_MOCK_FOR_POST_TEST:
        _run_mock_post()
        return

    if args.mode == "select_and_post":
        from pipeline.select_and_post import run_select_and_post

        ok = run_select_and_post(dry_run=args.dry_run)
        sys.exit(0 if ok else 1)

    if args.mode == "mock_post":
        _run_mock_post()
        return

    from legacy.rotation import run_legacy

    if args.mode == "rotate":
        run_legacy(None)
    else:
        run_legacy(args.mode)


if __name__ == "__main__":
    main()
