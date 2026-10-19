# OpenMontage web previews

This repository now has two independent browser services:

1. **Studio** (`studio_web/`) turns a short creative brief into a scene plan. Configure `OPENAI_API_KEY` and a private `STUDIO_ACCESS_CODE` in the Studio service environment before enabling generation. Never commit either value.
2. **Storyboard** (`storyboard_web/`) imports a Studio project JSON file and lets you revise scene text and export the updated JSON.

Projects are saved in each user's browser. The Storyboard app is intentionally a separate service and domain, so transfer a project with **Export project JSON** in Studio and **Import project JSON** in Storyboard. This first online version does not render video or share project storage between the two services.

## Deploy separately on Render

Connect this repository to Render, then create two Web Services. For both, use the `main` branch, Python runtime, `free` plan, Frankfurt region, and automatic deploys.

### Studio service

- Name: `openmontage-studio`
- Build command: `python -m py_compile studio_web/app.py`
- Start command: `python studio_web/app.py`
- Environment variables: set `STUDIO_ACCESS_CODE` to a private passphrase and `OPENAI_API_KEY` to your OpenAI API key. Optionally set `OPENAI_MODEL`.

### Storyboard service

- Name: `openmontage-storyboard`
- Build command: `python -m py_compile storyboard_web/app.py`
- Start command: `python storyboard_web/app.py`
- No API secrets are required.

Each service has an independent `/health` endpoint. Studio uses browser storage for local project drafts; browser storage is not a backup, so export project JSON to keep a copy.
