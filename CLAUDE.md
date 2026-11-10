# AI creative studio — umbrella

A done-for-you ad creative service (static ads, product and motion videos) sold to businesses in a few narrow niches. AI does the production; a human owns intake, taste, approvals and client relationships.

## Status

Validation phase. No niche has two paid pilots yet, so: do the work by hand with the skills, keep tracking in CSV and markdown, and do not build dashboards, databases or automation until a niche passes its gate (see `studio-core`, stage 1).

## How to work here

1. Find the niche folder for the task: `niches/horeca/`, `niches/iot-hardware/`, `niches/local-retail/`.
2. Use the `studio-core` skill for the workflow and the niche's skill (`niche-horeca`, `niche-iot-hardware`, `niche-local-retail`) for market knowledge.
3. Client work happens only in `niches/<niche>/clients/<client>/`. New client: `python scripts/new-client.py <niche> "<Client Name>"`.
4. Before any job for an existing client, read its `memory.md` and `brief.md`.
5. Never skip QA (studio-core stage 6) or the guardrails at the end of `studio-core`.

## Niches

| Niche | Folder | Skill | Role |
| --- | --- | --- | --- |
| HoReCa equipment and supplies | `niches/horeca/` | `niche-horeca` | Fastest test: warm contacts in Romania |
| IoT and electronics hardware | `niches/iot-hardware/` | `niche-iot-hardware` | Bigger opportunity: technical edge, global |
| Local retail and gift shops | `niches/local-retail/` | `niche-local-retail` | Portfolio and testing ground; Lighthouse is the first client |

## Adding a niche (only when a niche earns it)

1. `mkdir -p niches/<slug>/clients` and copy `niches/horeca/CLAUDE.md`, `prospects.csv`, `notes.md` as a starting point; edit them.
2. Copy `.claude/skills/niche-horeca/` to `.claude/skills/niche-<slug>/` and rewrite every section for the new market. Keep the same headings so all niche skills stay comparable.
3. Add the niche to the table above.

## Conventions

- Dates `YYYY-MM-DD`. Output files `<date>_<concept>_<format>.<ext>`.
- Money in EUR unless the client quotes in RON; say which.
- Client originals in `assets/` are never edited in place.
