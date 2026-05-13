---
name: ikf-sales-proposal
description: Create editable IKF commercial proposal HTML/PDF drafts from IKF's existing DOCX proposal families for Branding Kit, Website, AMC, Hosting, SEO, PPC, and Social Media Management. Use when an IKF sales proposal needs client details, selected services, commercial tables, IKF brand pages, source-DOCX section order, editable bullets/tables, client-logo assets, and browser/PDF review.
---

# IKF Sales Proposal

## Purpose

Create ready-to-review IKF sales proposal HTML files that follow the existing Word proposal families. Do not invent a generic proposal, marketing narrative, recommendation section, metadata panel, or arbitrary service card layout.

## Required Inputs

Ask for missing essentials before generating:

- Client company name.
- Website/domain or enough detail to research the company.
- Selected services: Branding Kit, Website, AMC, Hosting, SEO, PPC, SMM.
- Commercial inputs for every selected service: price, units, retainer, click rate, monthly quantity, duration, taxes, or known exclusions.
- Any special terms, exclusions, package names, geography, or mandate details.

If commercial inputs are missing or ambiguous, ask before drafting. Do not fill prices from defaults unless the user explicitly confirms them.

## Proposal Families

Choose the closest source family before writing:

- `seo-ppc-smm`: use when services include SEO, PPC/Performance Marketing, and Social Media Management. Section order is Cover, About Us, They Believe In Us, Scope of Work, SEO, SMM, Performance Marketing, Commercial Proposal, Terms & Conditions.
- `brandkit-website-amc-hosting-seo`: use when services include Branding Kit, Website, AMC, Hosting, and SEO. Section order is Cover, About Us, They Believe In Us, Scope of Work, Website, Client Responsibilities, Website Process, AMC/Hosting, SEO, Commercial Proposal, Terms & Conditions.

If the user selects a mixed service combination that does not match a known family, choose the nearest family and state the assumption before generating. Keep the family section order; omit only service sections that are genuinely unselected.

## Non-Negotiable Layout Rules

- Preserve IKF brand pages when available: cover image, About Us/Expertise image, and They Believe In Us logo image.
- Do not replace brand/logo pages with editable text boxes.
- Do not add “Prepared for”, industry, website metadata panels, chips, or AI recommendation sections unless the source family contains them.
- Keep commercials only in the `Commercial Proposal` section. Never place pricing tables inside scope, SEO plan, SMM deliverables, or PPC strategy sections.
- Keep section headings obvious and sparse. Use DOCX-style hierarchy: blue uppercase section labels, short section titles, compact bullets, and blue/yellow commercial tables.
- Use source proposal vocabulary where available: “Scope of Work”, “Search Engine Optimisation”, “Social Media Management”, “Performance Marketing”, “Commercial Proposal”, “Terms & Conditions”.

## Workflow

1. Read this skill file and identify the proposal family from selected services.
2. Read or inspect the relevant assets:
   - `assets/template/editable-proposal.html`
   - `assets/brand-pages/`
   - `assets/client-logos/manifest.json` when a proposal needs industry-specific client logos
   - `scripts/generate_proposal.py`
3. Research the client only for factual context; do not add a recommendation section unless requested.
4. Finalize the section outline before editing or generating.
5. Ask for any missing commercial inputs.
6. Generate with `scripts/generate_proposal.py`.
7. Patch the output only for known client-specific edits, not structural invention.
8. Open/preview the generated HTML when possible.
9. Verify the output against the family section order and commercial placement.

## Editable Behavior

Generated HTML must support direct sales edits:

- Text blocks and table cells use `contenteditable`.
- Bullet lists include visible edit controls: Add Bullet, Add Sub-Bullet, Delete Last Bullet.
- Commercial tables include Add Row and Delete Last Row controls.
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
