---
name: ikf-sales-proposal
description: Create editable IKF commercial proposal HTML/PDF drafts from IKF's existing DOCX proposal families for Branding Kit, Website, AMC, Hosting, SEO, PPC, and Social Media Management. Use when an IKF sales proposal needs client details, selected services, commercial tables, IKF brand pages, source-DOCX section order, editable bullets/tables, client-logo assets, and browser/PDF review.
---

# IKF Sales Proposal

## Purpose

Create and adapt IKF sales proposals using the bundled proposal editor. Treat `assets/template/editable-proposal.html` as a DOCX-derived editable proposal app, not an empty page that AI rewrites from scratch. The editor already contains the default sections, commercial table skeletons, terms, brand pages, and edit controls needed by sales.

Do not invent a generic proposal, marketing narrative, recommendation section, metadata panel, or arbitrary service card layout.

## Required Inputs

Ask for missing essentials before generating:

- Client company name.
- Website/domain or enough detail to research the company.
- Selected services: Branding Kit, Website, AMC, Hosting, SEO, PPC, SMM.
- Commercial inputs for every selected service: price, units, retainer, click rate, monthly quantity, duration, taxes, or known exclusions.
- Any special terms, exclusions, package names, geography, or mandate details.

If commercial inputs are missing or ambiguous, ask before drafting. Do not fill prices from defaults unless the user explicitly confirms them.

## Source Proposal Examples

The bundled DOCX files are source examples for default content and hierarchy, not rigid proposal family modes.

- PPC, SEO, Social Media Management proposal: source for SEO, SMM, Performance Marketing, digital commercial tables, and digital terms.
- Branding Kit, Website, AMC, Hosting, SEO proposal: source for Website, Website Process, AMC/Hosting, website commercial tables, and website terms.

Do not force the user into a family. Make all components available and include/remove only the blocks needed for the proposal.

## Editor Model

The core deliverable is a custom proposal editor with AI assistance, not full autopilot.

- `assets/template/editable-proposal.html` is the canonical base editor.
- Each major DOCX section is represented as an editable component with default source content.
- Sales users can add/remove bullets, add/remove table rows, remove sections, select included components, edit client names, swap logos, paste tables from Excel, and export HTML/PDF.
- AI should help select components, prepare client-specific fields, suggest small edits, replace logo categories, verify stale references, and sanity-check commercial placement.
- AI should not rewrite fixed scope, terms, process, AMC, SEO, SMM, PPC, or website default prose unless the user explicitly asks.

Component examples:

- `scope-digital`, `seo`, `smm`, `ppc`, `commercial-digital`, `terms-digital`
- `scope-website`, `website`, `website-process`, `amc-hosting`, `commercial-website`, `terms-website`

Commercial tables are components too. Keep pricing in the Commercial Proposal component only.

The `They Believe In Us` page is an editable logo grid backed by `assets/client-logos/manifest.js` and `assets/client-logos/`. AI-compatible logo replacement means selecting a category such as manufacturing, education, healthcare, finance, real estate, etc. and applying that category to the grid. Users can also search, replace individual logo cells, add slots, remove slots, or upload a one-off image manually.

## Non-Negotiable Layout Rules

- Preserve IKF brand pages when available: cover image, About Us/Expertise image, and They Believe In Us logo image.
- Do not replace brand/logo pages with editable text boxes.
- Do not add “Prepared for”, industry, website metadata panels, chips, or AI recommendation sections unless the source family contains them.
- Keep commercials only in the `Commercial Proposal` section. Never place pricing tables inside scope, SEO plan, SMM deliverables, or PPC strategy sections.
- Keep section headings obvious and sparse. Use DOCX-style hierarchy: blue uppercase section labels, short section titles, compact bullets, and blue/yellow commercial tables.
- Use source proposal vocabulary where available: “Scope of Work”, “Search Engine Optimisation”, “Social Media Management”, “Performance Marketing”, “Commercial Proposal”, “Terms & Conditions”.

## Workflow

1. Read this skill file and identify the needed proposal components from selected services.
2. Read or inspect the relevant assets:
   - `assets/template/editable-proposal.html`
   - `assets/brand-pages/`
   - `assets/client-logos/manifest.json` when a proposal needs industry-specific client logos
   - `scripts/generate_proposal.py`
3. Start from the editor template. Do not create a proposal from a blank HTML file.
4. Research the client only for factual context; do not add a recommendation section unless requested.
5. Finalize included components before editing or generating.
6. Ask for any missing commercial inputs.
7. Use the editor directly for manual sales-ready output, or use `scripts/generate_proposal.py` only as a helper to prefill client/family details.
8. Patch the output only for known client-specific edits, not structural invention.
9. Open/preview the generated HTML when possible.
10. Verify the output against the selected component list and commercial placement.

## Editable Behavior

Generated HTML must support direct sales edits:

- Text blocks and table cells use `contenteditable`.
- Bullet lists include visible edit controls: Add Bullet, Add Sub-Bullet, Delete Last Bullet.
- Commercial tables include Add Row and Delete Last Row controls.
- Commercial tables accept tabular paste from Excel/Sheets. Click the target starting cell and paste; tab/newline clipboard data is distributed across rows and columns.
- The client proof page uses editable logo cells, category replacement, per-cell file replacement, add-slot, and remove controls.
- Edit controls are visible on screen and hidden in print/PDF.
- “Save HTML” stores an edited copy and “Export PDF” uses browser print.

## Output Location

Create proposal outputs in the current workspace under `client proposals/` unless the user specifies another folder.

Filename:

`IKF_Commercial_Proposal_<Client>_<YYYY-MM-DD>.html`

## Verification

Before final response:

- Search the generated HTML for stale placeholders such as `ABC`, `Client Name`, `TODO`, and unrelated old client names.
- Confirm selected services and section order match the chosen proposal family.
- Confirm no pricing appears before `Commercial Proposal`.
- Confirm brand pages/images render via `assets/brand-pages/`.
- Confirm any logo grid or client proof section uses real images from `assets/client-logos/`, not typed placeholders.
- Confirm Add Bullet/Add Sub-Bullet controls exist for editable lists.
- Confirm row controls exist only for commercial tables.
- Confirm print styles hide editing controls.
- If browser preview is unavailable, say so briefly.
