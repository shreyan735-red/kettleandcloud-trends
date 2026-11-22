---
date: 2026-11-22T15:33:19.471Z
project: kettleandcloud-trends
session: ed78c852
schema_version: 1
next_steps_count: 3
has_blockers: false
keywords: stickfigure studio, stickman video, artifact, animation, video export
headline: Goal: stick-figure video creation tool as a claude.ai Artifact (Stickfigure Studio) at https://claude.ai/artifact/G16nUC
---

# Session Handoff Snapshot
> **Generated:** 11/22/2026, 3:33:19 PM

## 🎯 High-Level Objective
* **Goal:** Goal: stick-figure video creation tool as a claude.ai Artifact (Stickfigure Studio) at https://claude.ai/artifact/G16nUCD9jcELDnge6MvBtv. Intent: let the user pose figures, keyframe scenes, add sound/camera/props, and export shareable MP4/WebM videos (incl. 9:16 Shorts) without other software. Unrelated to the kettleandcloud-trends repo code; the source lives only in the scratchpad.

## 📌 Current State & Next Steps
* **Status:** Done: v2 live and tested headless (playback, props, auto-walk, aspect, backdrops, undo/redo, export start). Not verified: the Animate with Claude flow inside a real viewer (sample is unavailable headless); a full export file round-trip; the downloads save prompt.
* **Next Action:** Wait for user feedback on v2; fix anything they report and republish the same file path

### Remaining Queue
- [ ] Candidate features if asked: GIF export, voiceover via tts, drag-to-reorder frames, multi-select of frames, limb stretch/IK
- [ ] If the scratchpad is lost, rebuild from the artifact via Artifact read on the URL

## 🛠️ Modified Files Delta
* /tmp/claude-0/-home-user-kettleandcloud-trends/657f9016-265c-55a4-8eb2-6e287186245b/scratchpad/stickfigure-studio.html: complete artifact source (v2); republish the same path to keep the URL
* repo: no changes, nothing committed

## 🚫 Failed Approaches (DO NOT RETRY)
* Approach: rely on the publish skeleton's [hidden] rule in local tests → Result: modal with display:grid stayed visible and blocked clicks → Lesson: include [hidden]{display:none!important} in the page CSS
* Approach: scrollIntoView on the current filmstrip card → Result: scrolled the whole page vertically → Lesson: set the filmstrip's scrollLeft manually

## 🙋 User Decisions (made by the human)
- **Asked for a stickman video creation artifact, then asked to improve it 10x with more features**

## Summary
v1 published: posing, keyframes, tween playback, bubbles/captions, WebM/MP4 export. User asked to "improve 10x". v2 = full rewrite, republished to the same URL with capabilities downloads + sample. Design: plain HTML artifact; canvas world units via setTransform; 10-bone skeleton with parent-relative angles (legs parented to hip so the torso bends at the waist); shortest-angle lerp + smoothstep; per-frame cam {x,y,z}/shake/fx flash|dip/sfx; props are actors kind=prop, can attach to handR/handL following the forearm angle; aspect 16:9/9:16/1:1 swaps the globals W/H/GROUND and rescales poses; procedural backdrops (park, city, night, room, stage, desert, space) + uploaded image (downscaled JPEG dataURL); WebAudio-synth sfx + music in IndexedDB; export = captureStream(30) + MediaRecorder with an audio MediaStreamDestination, saved via the downloads capability; AI = sample.json with a strict schema and validation in buildFromAI; autosave localStorage key sfs-project, migrate() upgrades v1 data. Headless Playwright run: no errors.

---
*A short hint surfaces on session start; full context loads only if your next prompt matches a keyword above, or via manual `/handoff-resume`. The same record is available as a sibling `.json` file for external tools.*