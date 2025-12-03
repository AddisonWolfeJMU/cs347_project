import json
from django import template
from pathlib import Path
from django.conf import settings

register = template.Library()

@register.simple_tag
def vite_asset(entry_name):
    # Path to manifest.json produced during Vite build
    manifest_path = Path(settings.BASE_DIR) / "backend" / "static" / "manifest.json"

    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        raise RuntimeError("Vite manifest.json not found. Did you run `npm run build`?")

    # Return full static URL for Django
    return "/static/" + manifest[entry_name]["file"]
