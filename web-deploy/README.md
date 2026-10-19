# OpenMontage web previews

This repository now has two independent browser services:

1. **Studio** (`studio_web/`) turns a short creative brief into a prompt. The user opens ChatGPT or Gemini's official website, signs in there, then pastes the JSON response back into Studio. No API key or provider password is collected by this app.
2. **Storyboard** (`storyboard_web/`) imports a Studio project JSON file and lets you revise scene text and export the updated JSON.

Projects are saved in each user's browser. The Storyboard app is intentionally a separate service and domain, so transfer a project with **Export project JSON** in Studio and **Import project JSON** in Storyboard. Storyboard now includes a browser-only Video Maker at `/video`. Import the storyboard JSON, then attach one image or video clip to each scene. Clips can be generated manually in Gemini from the copied scene prompt, without an API key; the browser then renders a downloadable WebM with optional background music and narration captions. Rendering runs locally in a modern Chrome or Edge tab and uses memory while rendering. It does not call provider APIs or collect provider passwords. Studio and Storyboard remain separate services, so transfer a project with **Export project JSON** in Studio and **Import project JSON** in Storyboard.

## Deploy separately on Render

Connect this repository to Render, then create two Web Services. For both, use the `main` branch, Python runtime, `free` plan, Frankfurt region, and automatic deploys.

### Studio service

- Name: `openmontage-studio`
- Build command: `python -m py_compile studio_web/app.py`
- Start command: `python studio_web/app.py`
- No provider API environment variables are needed.

### Storyboard service

- Name: `openmontage-storyboard`
- Build command: `python -m py_compile storyboard_web/app.py`
- Start command: `python storyboard_web/app.py`
- No API secrets are required.

Each service has an independent `/health` endpoint. Studio uses browser storage for local project drafts; browser storage is not a backup, so export project JSON to keep a copy.
