"""Cut a rendered figure into overlapping tiles for visual inspection.

Looking at a whole figure at once is how small collisions survive. A 5.4 x 5.5 in
figure shown as one image is roughly a third of print resolution per region, and
a tick label touching a marker, a scale bar resting on a coastline or a label
grazing a curve are all invisible at that size and obvious at 1.5x.

    python figtiles.py figures/fig01.png            # 2x2 tiles, 1.5x zoom
    python figtiles.py figures/fig01.png --grid 3 2 --zoom 2.0

Writes the tiles beside the figure in a `_tiles` folder and prints their paths,
in reading order, so each can be opened and described in turn.
"""

from __future__ import annotations

import sys
from pathlib import Path


def tile(path, grid=(2, 2), zoom=1.5, overlap=0.12, out_dir=None):
    """Write overlapping tiles of an image; return their paths in reading order."""
    from PIL import Image

    path = Path(path)
    image = Image.open(path)
    width, height = image.size
    cols, rows = grid
    out_dir = Path(out_dir) if out_dir else path.parent / f"{path.stem}_tiles"
    out_dir.mkdir(parents=True, exist_ok=True)

    step_x, step_y = width / cols, height / rows
    pad_x, pad_y = step_x * overlap, step_y * overlap
    written = []
    for row in range(rows):
        for col in range(cols):
            box = (
                max(0, int(col * step_x - pad_x)),
                max(0, int(row * step_y - pad_y)),
                min(width, int((col + 1) * step_x + pad_x)),
                min(height, int((row + 1) * step_y + pad_y)),
            )
            piece = image.crop(box)
            piece = piece.resize(
                (int(piece.width * zoom), int(piece.height * zoom)), Image.LANCZOS
            )
            name = out_dir / f"{path.stem}_r{row + 1}c{col + 1}.png"
            piece.save(name)
            written.append(name)
    return written


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    source = argv[0]
    grid, zoom = (2, 2), 1.5
    if "--grid" in argv:
        i = argv.index("--grid")
        grid = (int(argv[i + 1]), int(argv[i + 2]))
    if "--zoom" in argv:
        zoom = float(argv[argv.index("--zoom") + 1])
    for name in tile(source, grid=grid, zoom=zoom):
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
