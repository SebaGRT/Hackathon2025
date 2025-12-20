#!/usr/bin/env python3
"""
Generate PWA icons for SafeSite application.
This script creates simple PNG icons for the PWA manifest.
"""

import os
from pathlib import Path


def create_svg_icon(size):
    """Create an SVG icon with the SafeSite logo concept"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{size}" height="{size}" fill="#3b82f6" rx="{size * 0.15}"/>

  <!-- Shield icon -->
  <g transform="translate({size * 0.2}, {size * 0.15})">
    <!-- Shield outline -->
    <path d="M {size * 0.3} {size * 0.05}
             L {size * 0.05} {size * 0.15}
             L {size * 0.05} {size * 0.35}
             C {size * 0.05} {size * 0.45}, {size * 0.15} {size * 0.55}, {size * 0.3} {size * 0.65}
             C {size * 0.45} {size * 0.55}, {size * 0.55} {size * 0.45}, {size * 0.55} {size * 0.35}
             L {size * 0.55} {size * 0.15}
             Z"
          fill="white" opacity="0.95"/>

    <!-- Checkmark -->
    <path d="M {size * 0.2} {size * 0.33}
             L {size * 0.27} {size * 0.4}
             L {size * 0.42} {size * 0.23}"
          stroke="#3b82f6"
          stroke-width="{size * 0.04}"
          stroke-linecap="round"
          stroke-linejoin="round"
          fill="none"/>
  </g>

  <!-- Text 'S' -->
  <text x="{size * 0.5}"
        y="{size * 0.85}"
        font-family="Arial, sans-serif"
        font-size="{size * 0.25}"
        font-weight="bold"
        fill="white"
        text-anchor="middle">S</text>
</svg>'''


def create_apple_touch_icon():
    """Create Apple touch icon (180x180)"""
    size = 180
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background with rounded corners for iOS -->
  <rect width="{size}" height="{size}" fill="#3b82f6"/>

  <!-- Shield icon -->
  <g transform="translate({size * 0.2}, {size * 0.15})">
    <path d="M {size * 0.3} {size * 0.05}
             L {size * 0.05} {size * 0.15}
             L {size * 0.05} {size * 0.35}
             C {size * 0.05} {size * 0.45}, {size * 0.15} {size * 0.55}, {size * 0.3} {size * 0.65}
             C {size * 0.45} {size * 0.55}, {size * 0.55} {size * 0.45}, {size * 0.55} {size * 0.35}
             L {size * 0.55} {size * 0.15}
             Z"
          fill="white" opacity="0.95"/>

    <path d="M {size * 0.2} {size * 0.33}
             L {size * 0.27} {size * 0.4}
             L {size * 0.42} {size * 0.23}"
          stroke="#3b82f6"
          stroke-width="{size * 0.04}"
          stroke-linecap="round"
          stroke-linejoin="round"
          fill="none"/>
  </g>

  <text x="{size * 0.5}"
        y="{size * 0.85}"
        font-family="Arial, sans-serif"
        font-size="{size * 0.25}"
        font-weight="bold"
        fill="white"
        text-anchor="middle">S</text>
</svg>'''


def main():
    """Generate all PWA icons"""
    # Define output directory
    base_dir = Path(__file__).parent
    output_dir = base_dir / "seguridad" / "static" / "pwa"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Icon sizes for PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    print("Generating PWA icons...")
    print("=" * 50)

    # Generate standard PWA icons
    for size in sizes:
        svg_content = create_svg_icon(size)
        svg_path = output_dir / f"icon-{size}x{size}.svg"

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"✓ Created {svg_path.name}")

    # Generate Apple touch icon
    apple_svg = create_apple_touch_icon()
    apple_path = output_dir / "apple-touch-icon.svg"

    with open(apple_path, "w", encoding="utf-8") as f:
        f.write(apple_svg)

    print(f"✓ Created {apple_path.name}")

    # Generate favicon
    favicon_svg = create_svg_icon(32)
    favicon_path = output_dir / "favicon.svg"

    with open(favicon_path, "w", encoding="utf-8") as f:
        f.write(favicon_svg)

    print(f"✓ Created {favicon_path.name}")

    print("=" * 50)
    print("\n✅ All PWA icons generated successfully!")
    print(f"\nIcons location: {output_dir}")
    print("\nNote: SVG files have been created. For production, you may want to")
    print("convert these to PNG using a tool like ImageMagick or an online converter:")
    print("  for i in 72 96 128 144 152 192 384 512; do")
    print("    convert icon-${i}x${i}.svg icon-${i}x${i}.png")
    print("  done")
    print("\nOr use the SVG files directly (modern browsers support them).")


if __name__ == "__main__":
    main()
