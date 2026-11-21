# EDIT_MAP.md

> Read first, every session. Every cut, asset and render traces back to this
> file. Replace each `<...>` with something true about *this* project. Source
> footage listed here is read-only: the kit never edits, moves or overwrites it.

## Project
- **What this is, in one line:** 5-second vertical teaser reel, "Slow mornings" for Kettle & Cloud (HyperFrames, project in reel/)
- **Owner:** shreyan
- **Brief:** none

## Source footage
<!-- Read-only. Record what ffprobe reports, not what the file name says. -->
| File | Duration | Resolution / fps | Audio | Notes |
|---|---|---|---|---|
| none | n/a | n/a | n/a | Built from HTML/CSS shapes, no source footage |

## Style
- **Pace:** <e.g. cut every 2–4 s; no jump cuts mid-sentence>
- **Captions:** <font, size, position, max words per line, burned in or sidecar>
- **Look:** <colour, brand elements, intro/outro or none>
- **Never:** <e.g. zoom punch-ins, stock transitions, emoji captions>

## Delivery
<!-- One row per output. A render is checked against its row: frame samples, ffprobe and a loudness measurement. -->
| Target | Resolution | fps | Codec / container | Loudness | Safe zone |
|---|---|---|---|---|---|
| Shorts / Reels | 1080x1920 | 30 | H.264 + AAC / mp4 | -14 LUFS, -1 dBTP | HyperFrames TikTok/Reels/Shorts safe zone |

## Assets
<!-- Music, fonts, stock clips, logos, SFX. An asset without a licence row never enters a render. -->
| Asset | Source | Licence | Attribution needed | Checked |
|---|---|---|---|---|
| whoosh-short.mp3, whoosh.mp3, sparkle.mp3 (reel/assets/sfx) | HyperFrames media-use bundled library (from Pixabay) | Pixabay Content License, https://pixabay.com/service/license-summary/ | no | 2026-11-21 |
| Playfair Display, Inter (fonts) | bundled with HyperFrames | open fonts bundled by the tool | no | 2026-11-21 |

## Evidence
<!-- Every number or claim shown on screen or in subtitles needs a row. No row → [NEEDS PROOF]. -->
| Claim | Source | Checked |
|---|---|---|
| <e.g. "3x faster builds"> | <benchmark link, timestamp in footage> | <date> |

## Learnings
<!-- What a cut or render taught you, with the number that showed it. -->
- <date>: <what was tried> → <result> → <what changes next time>
- 2026-11-21: first render was flat and silent → added gradients, shading, stars, 3 SFX, delivery quality → 1080x1920 30fps 5.0 s, -14.2 LUFS, -2.0 dBFS peak
