---
name: proposal-personalizer
description: Personalize IKF AI Masterclass proposal HTML files from the locked base template. Use when creating or updating a client-specific IKF proposal, including client research, required-input checks, copying the base template, replacing every client reference, updating pricing/format/travel/payment terms, verifying stale references, and opening the edited proposal in Chrome for preview.
---

# Proposal Personalizer

## Core Rules

- Use the bundled asset `assets/IKF AI Masterclass - base template.html` as the source template.
- Treat the base template as locked. Do not edit it.
- Always duplicate the base template and make changes only in the new client file.
- Preserve layout, structure, styling, spacing, and design unless the user explicitly requests a design or layout change.
- Do not add the removed cover metadata block (`Prepared for` / `Prepared by`) unless the user explicitly asks for it.
- Keep default payment terms as 50% advance at booking and 50% balance post-session unless the user provides different terms.
- Use Calibri unless the user explicitly asks for a different font.
- Open the edited file in Chrome for the user to preview.

## Required Inputs

Before editing, make sure these are known:

- Client contact name
- Client company name
- Website/domain, or an email address that can provide the domain
- Recommended format
- Pricing
- Outstation status, travel, and venue handling
- Payment terms, if they differ from the template

If any required detail is missing, ask for it before editing. If the website/domain is missing but email is provided, derive the domain from the email.

## Workflow

1. Identify the bundled base template at this skill's `assets/IKF AI Masterclass - base template.html`.
2. Create a new filename using the client/contact, for example `IKF_AI_Masterclass_Proposal_ClientName.html`.
3. Duplicate the base template into that new file.
4. Research the client before personalizing content.
5. Use the client website as the primary source; use reliable public sources only when the website lacks enough context.
6. Update all client-specific fields and prose.
7. Update recommendation text using the researched business context and the requested format.
8. Update `Available Masterclass Formats` so the recommended format is visually highlighted and all prices match the user-provided pricing.
9. Update travel and venue terms only from user-provided facts.
10. Update payment terms only from user-provided facts.
11. Keep all non-client-specific IKF content unchanged unless the user asks otherwise.
12. Open the edited file in Chrome for preview.
13. Return a clickable local file link to the edited file.

## Personalization Checklist

Replace every occurrence of prior or placeholder client details, including:

- Contact name
- Company name
- Short company name
- Domain, website, and email
- Industry and business context
- Recommendation block title and body
- Masterclass format recommendation and badge
- Inclusion examples that mention client industry
- Travel and venue section
- Outcome statements
- Confirmation steps
- Confidentiality note
- Browser title, toolbar subtitle, email/PDF generated title text

Do not leave traces of any other client in the edited file.

## Verification

After editing, run targeted searches on the new file:

- Search for old client names from the base/template or previous file.
- Search for common stale client terms such as `Setco`, `Rajesh`, `Malpani`, or any client name seen in the source being copied from.
- Search for old domains and old emails if present.
- Search for old pricing values after pricing changes.
- Search for the selected recommendation labels to verify only the intended format is marked recommended.

If stale references remain, fix them and search again.

## Browser Preview

- Use Chrome when available because the workflow expects user preview in Chrome.
- Open the edited file as a local file URL.
- Verify the page loads and the visible title/client details match the current proposal.
- If Chrome tooling is unavailable, use the available browser tool and state that fallback briefly.

## Output

Final response must include:

- The edited file link as a clickable local markdown link.
- A short summary of what changed.
- Any fields still missing or assumptions made.
