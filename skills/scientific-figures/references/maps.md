# Maps and geospatial figures

* use a projection appropriate to the extent and the quantity; do not distort
  spatial interpretation through an arbitrary one;
* state the projection in the caption when it matters to interpretation;
* keep geographic context visually subordinate to the data — coastlines and
  boundaries thin and in `C.grey` or `C.light`, no busy basemap;
* draw boundaries only when they carry meaning for the result;
* use perceptually uniform colormaps, with limits and units that a reader can
  act on, and a colorbar label that names the quantity and its unit;
* for signed anomalies centre the diverging norm on zero, or on the reference
  value the result is about;
* show station markers clearly, with a visible edge when they sit on a filled
  field;
* add a scale bar or north arrow only when the reader needs them to interpret
  the result, not by reflex.

When many points overlap, aggregate, bin, use density, or add transparency.
Never shrink markers until the points disappear.

Rasterise dense field layers inside a vector figure so the file stays usable
while text and vectors remain sharp:

```python
ax.pcolormesh(lon, lat, field, rasterized=True)
```

Set `dpi` on `save()` high enough that the rasterised layer stays crisp at final
size; the style already exports at 400 dpi.

For a multi-panel map figure, `figstyle.label_panels(axes, inside=True)` places
the panel letter inside the frame, where map panels usually have no room above.

Equal-aspect map axes ignore the height you asked for, so the figure will show
extra vertical whitespace. Set the figure height from the panel aspect ratio
rather than leaving constrained layout to absorb the gap.
