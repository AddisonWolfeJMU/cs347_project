import json
from pathlib import Path
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

# -------------------------------------------------------------------
# Load manifest.json once at import
# -------------------------------------------------------------------

def load_manifest():
    manifest_path = Path(settings.BASE_DIR) / "backend" / "static" / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(
            f"Vite manifest.json not found at: {manifest_path}\n"
            "Did you run `npm run build` inside the frontend folder?"
        )
    with open(manifest_path, "r") as f:
        return json.load(f)

manifest = load_manifest()


# -------------------------------------------------------------------
# Resolve asset entry
# -------------------------------------------------------------------
def resolve_vite_asset(entry_name: str):
    if entry_name not in manifest:
        raise RuntimeError(
            f"Entry '{entry_name}' not found in manifest.json.\n"
            f"Available entries: {list(manifest.keys())}"
        )
    return "/static/" + manifest[entry_name]["file"]


# -------------------------------------------------------------------
# Template tags
# -------------------------------------------------------------------

@register.simple_tag
def vite_js(entry_name):
    """Injects <script type='module'> for a Vite JS entry."""
    src = resolve_vite_asset(entry_name)
    return mark_safe(f'<script type="module" src="{src}"></script>')


@register.simple_tag
def vite_css(entry_name):
    """Injects <link rel='stylesheet'> for a Vite CSS entry (if exists)."""
    css_files = manifest.get(entry_name, {}).get("css", [])
    if not css_files:
        return ""
    href = "/static/" + css_files[0]
    return mark_safe(f'<link rel="stylesheet" href="{href}">')

