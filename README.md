# AI creative studio

Umbrella repo for the AI creative service: one folder per niche, one folder per client inside it, and Claude Code skills for the shared workflow and for each niche.

```
ai-creative-studio/
├── CLAUDE.md                     umbrella rules Claude Code reads first
├── .claude/skills/
│   ├── studio-core/              8-stage workflow shared by all niches
│   ├── niche-horeca/             HoReCa equipment and supplies
│   ├── niche-iot-hardware/       IoT and electronics hardware makers
│   └── niche-local-retail/       local shops and gift shops
├── templates/client/             blank client folder
├── scripts/new-client.py         creates a client folder from the template
└── niches/
    ├── horeca/        CLAUDE.md · prospects.csv · notes.md · clients/
    ├── iot-hardware/  CLAUDE.md · prospects.csv · notes.md · clients/
    └── local-retail/  CLAUDE.md · prospects.csv · notes.md · clients/lighthouse-cafe/
```

## Start

```bash
cd ai-creative-studio
git init && git add . && git commit -m "Studio skeleton"
claude            # open Claude Code here
```

Create a client:

```bash
python scripts/new-client.py horeca "Example Distributor SRL"
```

Then in Claude Code, for example: *"Work on niches/horeca/clients/example-distributor-srl — run intake from the files in assets/."*

## First steps (validation)

1. Fill `niches/horeca/prospects.csv` and `niches/iot-hardware/prospects.csv` with 20 companies each.
2. Make 3 sample pieces for the best 10 in one niche and send them.
3. Two paid pilots in a niche = it passes; only then build tooling for it.

Large media (videos) can bloat git. If outputs grow, add `niches/*/clients/*/outputs/*.mp4` to `.gitignore` and keep videos in cloud storage, linking them from `DELIVERY.md`.
