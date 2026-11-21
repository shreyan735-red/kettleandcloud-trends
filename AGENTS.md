# AGENTS.md

<!-- handoff:learnings:begin -->
## Session Learnings (auto-updated by handoff)

### Implicit Rules
- Build a part: python3 audio_parts.py N st.wav; python3 partN.py silent.mp4; ffmpeg mux with -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac; run from stickfigure_video/
- Preview: python3 partN.py --still T out.png
- ElevenLabs flow WMQWI9TmXULbylvOpSZe holds all VO takes; generations_count 1; ~1900 credits used so far
- Captions bottom at y~1500; top titles y 260-390; keep figures' ground <=1250 to avoid caption overlap
- Commit trailer lines required; no model ids in commits

### Key Decisions
- Decision: PIL drawing at 2x supersample piped as rawvideo to ffmpeg libx264 — Reason: no cairo/animation libs installed; PIL+ffmpeg available, fast (~1 min/part with multiprocessing Pool)
- Decision: render.py holds Part 1 + primitives; engine.py imports them and adds shared helpers + run_video/render_frame; part2/3/4.py define SCENES lists — Reason: reuse without refactoring working Part 1
- Decision: one ElevenLabs eleven_v4 take per part, split by ffmpeg silencedetect, placed by segments*.txt (vo_start vo_end place_at) — Reason: one generation cheaper than per-line, placement syncs VO to scenes; captions derived from same file
- Decision: male voice Jack (BVPhWQykET1TSvfGzrUr) Parts 1-3, female Isla Sterling (qSR2T7SqN7Pcd0YpO3Vd) Part 4 — Reason: Part 4 switches to her POV after Part 3 ended his arc
- Decision: SFX/music synthesized in numpy (audio.py, audio_parts.py), loudnorm I=-14 at mux — Reason: no copyright risk, no external assets; raw mix was -23 LUFS, too quiet for Shorts
- Decision: created personal cloud env kettleandcloud-trends (keeps instagram hosts + elevenlabsusercontent.com), session switched network_only — Reason: VO download host was blocked on Default env

<!-- handoff:learnings:end -->
