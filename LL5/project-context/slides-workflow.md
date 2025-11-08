# Presentations Workspace Strategy for Lightning Lessons

## Strategy Overview
- Maintain a dedicated Slidev workspace under `projects/maven/presentations/` to keep presentation assets separate from lesson code while preserving proximity for context sharing.
- Organize one subdirectory per lightning lesson (`LL1`–`LL5`) so each deck, assets, and build outputs remain isolated and reproducible.
- Treat the slide workspace as a consumer of Markdown outlines stored in `crewai-ll-series/project-context`, enabling agents to load lesson context without duplicating codebases.
- Ensure every deck can be built both as a live HTML presentation and as a downloadable PDF for student distribution.

## Recommended Directory Structure
- `projects/maven/presentations/`
  - `package.json` / `pnpm-workspace.yaml` managing shared Slidev dependencies
  - `shared/` (optional) for reusable theme assets, CSS, or components
  - `LL1/`
    - `slides.md`
    - `assets/`
    - `dist/html/`, `dist/pdf/`
  - `LL2/` … `LL5/` following the same pattern
- `projects/maven/crewai-ll-series/`
  - `LL#/project-context/LL#-slides.md` (slide outlines consumed by the Slidev workspace)

## Implementation Steps
1. **Create Presentations Workspace**
   - Make the parent directory `projects/maven/presentations/`.
   - Move the existing `cursor-slidedev` project contents into this location, keeping Git history if possible (e.g., `git mv`).
2. **Establish Shared Dependencies**
   - At `projects/maven/presentations/`, initialize `package.json` (or keep the existing one) with Slidev and Playwright exports.
   - Optional: configure a workspace manager (pnpm/yarn/npm workspaces) to manage per-lesson packages if needed.
3. **Create Lesson Subdirectories**
   - For each lightning lesson, scaffold a folder (`LL1`–`LL5`) containing a minimal `slides.md`, local assets folder, and `dist/` directories (gitignored) for outputs.
   - Add lesson-specific `package.json` scripts if you prefer per-lesson commands (e.g., `"dev": "slidev --open"`, `"build": "slidev build --out dist/html"`, `"export": "slidev export --output dist/slides.pdf"`).
4. **Integrate Markdown Outlines**
   - Decide on a sync method: manual copy, `curl` the raw GitHub file, or a helper script that reads `../crewai-ll-series/LL#/project-context/LL#-slides.md` and transforms it into Slidev format.
   - Document the sync in a `README` so future agents know how to refresh content.
5. **Build & Export**
   - Live presentation: run `npx slidev --root LL5` (or equivalent) from the presentations workspace to serve HTML.
   - Distribution: run `npx slidev build --root LL5 --out dist/html` and `npx slidev export --root LL5 --output dist/slides.pdf` to generate shareable files per lesson.
6. **Automate Optional Enhancements**
   - Add a root-level script (`npm run build:all`) that iterates through lessons to rebuild HTML/PDF.
   - Include CI or pre-release hooks to refresh PDFs before publishing course materials.
7. **Cross-Workspace Context**
   - When opening a new Cursor window for slides, reference this document and the lesson-specific outline to provide rapid context for the agent without importing lesson source code.

## Workflow Summary
- Author lesson content and observability code in `crewai-ll-series`.
- Record presentation narrative in `LL#/project-context/LL#-slides.md`.
- Open a separate Cursor session on `projects/maven/presentations/LL#` to convert the outline into Slidev decks and export deliverables.
- Store generated PDFs/HTML in each lesson directory (gitignored or committed per distribution policy) for easy sharing with students.

## Sources
- Internal context: `LL5/project-context/LL5-demo-plan.md`, `LL5/project-context/LL5-slides.md`

## Assumptions
- Slidev remains the chosen presentation framework for all lightning lessons.
- Agents can access both the code and slides workspaces within WSL2 without permission issues.
- PDF exports are distributed to students; HTML builds stay local for the live demo.

## Open Questions
- Should we script automated syncing from slide outlines to Slidev format, or keep it manual for editorial control?
- Do we commit generated PDFs to version control or publish them via a separate artifact repository/LMS?
- Is a shared slide theme required across lessons, and if so, where should it live (`shared/` vs. per-lesson)?

## Audit
- timestamp: 2025-11-07T00:20:00Z
- persona: product-mgr
- action: create-slides-workflow-doc
- tools: none
- llm: gpt-5-codex (temperature=0.2, max_tokens=2048)

