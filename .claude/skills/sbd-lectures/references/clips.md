# Clips: `animations/scenes.py`

manim Community scenes on the course navy, formulas in `MathTex`, words in Libre
Franklin. One file for every lecture; the Makefile groups scenes per lecture
(`SCENES_11`, `SCENES_12`, …) and `SCENES` concatenates them.

## Render

The venv lives in `animations/.venv` (rebuild with `uv sync` in `animations/`).
LaTeX comes from TinyTeX, which is not on the PATH:

```bash
cd animations
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
.venv/bin/manim -qm --disable_caching scenes.py Lloyd          # deck quality, 1280x720
.venv/bin/manim -ql --disable_caching scenes.py Lloyd          # quick look
```

Output lands in `~/.cache/sbd-manim-media/videos/scenes/720p30/` (`manim.cfg`;
the media dir stays out of iCloud, and configparser keeps an inline `# comment` as
part of a value, so `manim.cfg` has none). Then remux into the deck:

```bash
ffmpeg -v error -y -i ~/.cache/sbd-manim-media/videos/scenes/720p30/Lloyd.mp4 \
  -c copy -movflags +faststart lectures/media/Lloyd.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 lectures/media/Lloyd.mp4
```

`make clips` does render + remux for every scene in `SCENES`.

**Several scenes at once:** give each process its own `--media_dir`. They share
the Tex cache otherwise, and one of them dies with "can't open file ….dvi".
Render in the background; a 50-second clip takes a minute or two at `-qm`.

## Helpers in `scenes.py`

- `Stage` — base class. New scenes set `WAIT_SCALE = 1.0` and `PLAY_SCALE = 1.0`
  and time their own waits; the scales only stretch the older reels.
- `self.caption(mob)` — the one caption slot. Fades the previous caption out,
  then the new one in, and raises if the caption would leave the frame. Put
  every sentence that explains the clip through it, at one fixed position (a
  `slot` point centred at x = 0 under the plot), so captions never stack.
- `label(text, size, color)` — Libre Franklin text, set at four times the size
  and scaled down. Below about 26 pt Pango hints the font's spaces to nothing
  ("start:three", "whichisw"); do not replace it with a bare `Text`.
- `km_axes(...)` — plain axes in the muted colour, no tips.
- `lloyd(P, cent)` and `kmeans_best(P, k)` — plain Lloyd and the best of 25
  random starts, so a clip shows what `kmeans(nstart = 25)` would return and
  every count on screen is computed, not typed.
- Palette constants: `NAVY` stage, `CREAM` main ink, `GOLD` the thing to look at,
  `SKY` the second group, `MUTED` axes and secondary text.

## Layout

Frame is 14.2 × 8 units, origin at the centre. A plot on the left
(`to_edge(LEFT, buff≈0.7–1.0)`, about 6–7 units wide), a panel on the right
starting at x ≈ 1.0, the caption slot at y ≈ −3.0 … −3.2 centred at x = 0.
Right-panel lines must end before x ≈ 6.9; anything longer gets a smaller size
or fewer words. Check with frames, not by eye from the code.

## Failure catalogue (lecture 11, 2 Nov 2026)

What the first k-means clips got wrong, and Niccolò saw in class:

| Defect | Cause | Fix |
|---|---|---|
| Captions printed over each other | each `FadeIn(label(...))` added text, nothing removed it | `self.caption()` |
| Spaces missing ("whichisw") | Pango hinting at small sizes | `label()` at 4× then `scale(0.25)` |
| Text cut at the right edge | a note placed `next_to` a box near the edge | panel column with a fixed left edge, shorter text |
| A gold star that never moves | the "bad start" left one cluster empty, so its centroid sat alone | simulate starts first; keep one that converges to the intended groups with no empty cluster |
| Clips of 33–36 s | one idea shown once | write each step's number on screen: the W of every half-step, the drop at every k, the counts per cluster |
| Black band right and below in the player | reveal's 95% cap on `<video>` | fixed in the theme |
| Caption under the clip overprinted by the footer | 1000×562 embed plus two caption lines | embed at 880×495 |

## Reviewing frames

`scripts/contact-sheet.sh <clip.mp4> <out.png> t1 t2 …` extracts frames at the
given seconds and tiles them two by two. Pick times right after each caption
change and at the end. Look for: two texts overlapping, text at the frame
edge, an object whose purpose the caption does not explain, numbers that
disagree with the slide.
