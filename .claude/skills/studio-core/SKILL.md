---
name: studio-core
description: The shared 8-stage workflow for the AI creative studio — intake, research, concepts, production, QA, delivery and learning for ad creative and short videos made for a client business. Use for any client job in this repo, together with the niche skill for the folder you are working in.
---

# Studio core workflow

This studio sells done-for-you ad creative (static ads, short product and motion videos) to businesses in a few narrow niches. Every job runs through the same eight stages. The niche skill (`niche-horeca`, `niche-iot-hardware`, `niche-local-retail`) adds market-specific knowledge on top; it never replaces a stage here.

Always work inside one client folder: `niches/<niche>/clients/<client>/`. If it does not exist, create it with `python scripts/new-client.py <niche> "<Client Name>"`. Never write client files anywhere else.

## Stage 1 — Validate (only before the first paid client in a niche)

Do not build automation for a niche that has no paying client. Work from `niches/<niche>/prospects.csv`:

1. Fill 20 rows: company, website, country, contact, and `weakness_noted` (one concrete line: "spec-sheet photos only, no video", "same ad running since March").
2. Pick the best 10. For each, make 3 sample pieces using stages 3–6, watermarked "SAMPLE — not for publication".
3. Record a 60–90 second screen walkthrough per prospect and send it with the outreach message from the niche skill.
4. Update `sample_status`, `outreach_date`, `reply`, `next_step` as things happen.

Gate: two paid pilots before investing in tooling for the niche.

## Stage 2 — Intake

Inputs: whatever the client sent, saved into `assets/` (originals, never edited in place) and summarised in `brief.md`.

Fill every field of `brief.md`. Then write a **Missing inputs** list: anything a stage below will need that the client has not given (approved claims, price, logo files, product dimensions, usage rights for photos, consent for any person shown). Write a **Revision risks** list: places the client is likely to change their mind (tone, colours, which product variant).

Decision line at the end of the brief: `ACCEPT`, `ACCEPT AFTER INPUTS`, or `DECLINE` with one reason. Decline if the job needs a claim you cannot verify, a real person without consent, or a budget under the expected production cost plus your time.

## Stage 3 — Research

Write `research.md` with sources linked:

- The client's own product page and listings: what they say, what is missing.
- Customer language: reviews (their own, marketplaces, Google Maps), forums, Reddit. Quote short phrases buyers actually use; mark each with its source.
- Competitors: their active ads (Meta Ad Library: facebook.com/ads/library), offers, formats. Note what every competitor repeats, so the client can say something different.
- Output: 5–10 **angles**, each = one pain point or desired outcome + the buyer phrase that proves it + the proof the client can actually back.

## Stage 4 — Concepts

Write `concepts.md`: for the 3–5 strongest angles, a headline, one line of body copy, the visual idea, the format list (feed 4:5, 1:1, story/reel 9:16), and for video a 15–30 s script with scene-by-scene shots.

Language: the buyer's language (niche skill says which). Every factual claim in copy must trace to `brief.md` approved claims or the client's own published material; if not, rewrite it as a non-claim or add it to Missing inputs.

Gate: the client (or, during validation, you) approves concepts before any paid generation.

## Stage 5 — Production

Before generating, write the estimated cost per asset into `log.csv` and check the total against the brief's budget cap. Explore cheap, finish premium.

| Need | First choice | Notes |
| --- | --- | --- |
| Static ad layout with real product photo | HTML/canvas layout or the Design canvas, exported PNG | Cheapest and exact: the product is the real photo |
| New product scene from a reference photo | GPT Image / Nano Banana / Flux / Seedream | Check label, print, colour and geometry against the original |
| Text-heavy graphic (poster, price card) | Ideogram / Recraft | Still proofread every letter |
| Fixing one detail in an otherwise good image | Qwen image edit / Nano Banana edit | Edit, do not regenerate |
| Cheap video exploration | Lower-cost Kling / Wan / Pixverse settings | Decide the idea here, not in premium models |
| Final hero video shot | Kling / Seedance | Arrive with the shot planned |
| Talking-person ad | Voice (ElevenLabs / fal) → reference image + script + audio → Seedance or similar | Script, exact audio and reference image together, so the model cannot improvise words |
| Motion graphics, captions, product motion video | ffmpeg / Remotion / Python frame rendering | Word-level transcript drives caption timing |

Save each final asset to `outputs/` named `<YYYY-MM-DD>_<concept>_<format>.<ext>` (e.g. `2026-11-10_winter-gift_9x16.mp4`). Save the exact prompt or JSON request for every generated asset next to it as `.prompt.txt` or `.json`.

## Stage 6 — QA and repair

Check every asset against `brief.md` before anyone else sees it:

1. **Product truth.** Shape, colour, logo, label, print text and typeface match the client's real product photo. AI models routinely restyle printed text and logos — compare side by side, letter by letter.
2. **Claims.** Every number, certification and promise appears in the approved claims.
3. **Spelling and diacritics** (Romanian: ă â î ș ț).
4. **Format.** Size, duration, safe zones (keep text out of the top ~14% and bottom ~20% of 9:16 for Reels/Stories UI), file size.
5. **People.** Written consent on file in `brief.md` for every real person; AI-generated or AI-altered people are disclosed (Meta's AI label or a caption line) and never presented as customers or reviewers.
6. **Readability.** Text contrast at least 4.5:1; headline readable on a phone at arm's length.

Fix with targeted edits, at most 3 attempts per asset; after that, escalate to the human with what failed. Log each repair in `log.csv`.

## Stage 7 — Delivery

Deliver every approved format in `outputs/` (or the client's shared folder) with a short `DELIVERY.md`: what each file is, where to use it, primary text and headline for the ad manager, and any placeholder the client must fill (e.g. `[PREȚ] lei`).

If the client gives ad-account access, upload through the Meta Marketing API with write calls only (create ad, upload creative, pause). Read performance from the client's exports or a synced data store, never by looping read calls against the API — bulk calls risk breaking the API terms and getting the account restricted.

## Stage 8 — Learn

Append to `memory.md`: what the client approved, rejected and changed, and why. Append to `log.csv` for every asset: date, concept, format, model, cost, attempts, approved (y/n), result notes. When the client shares ad results, record spend, CTR, cost per result next to the concept. Before the next job for this client, read `memory.md` first.

Once a month per niche, read all clients' `log.csv` and write what you learned (winning angles, models that preserved product detail, where margin leaked) into the niche's `notes.md`.

## Guardrails (never skipped)

- No real person in an ad without their written consent recorded in `brief.md`.
- No AI person presented as a real customer, reviewer or testimonial.
- No claim, price, discount, certification or stock statement that the client has not approved in writing.
- No reproduction of another brand's logo, character or ad design.
- Client approves every asset before it runs.
