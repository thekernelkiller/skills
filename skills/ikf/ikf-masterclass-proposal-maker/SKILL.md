---
name: ikf-masterclass-proposal-maker
description: Create and personalize IKF AI-Native Thinking Accelerator proposal HTML files from the locked base template. Use when creating or updating a client-specific IKF masterclass or 3-month accelerator proposal, including client web research, required-input checks, business-problem personalization, copying the base template, replacing every client reference, updating the 9-pillar framework and single pricing block, verifying stale references, and opening the edited proposal in Chrome for preview.
---

# IKF Masterclass Proposal Maker

## Core Rules

- Use the bundled asset `assets/IKF AI Masterclass - base template.html` as the source template.
- Treat the base template as locked. Do not edit it.
- Always duplicate the base template and make changes only in the new client file.
- Preserve layout, structure, styling, spacing, and design unless the user explicitly requests a design or layout change.
- Do not add the removed cover metadata block (`Prepared for` / `Prepared by`) unless the user explicitly asks for it.
- Set the cover subtitle to `Prepared for <Client Company Name>`; do not use the contact person's name there.
- Treat the commercial offer as one accelerator membership price, not multiple masterclass formats.
- Keep default payment terms as 100% advance payment to confirm participation unless the user provides different terms.
- Use Calibri unless the user explicitly asks for a different font.
- Open the edited file in Chrome for the user to preview.

## Required Inputs

Before editing, make sure these are known:

- Client contact name
- Client company name
- Contact email
- Contact phone number
- Contact designation
- Website/domain, or an email address that can provide the domain
- Problems or business challenges they are facing
- Department presence or relevance inputs, when provided by the intake form
- Pricing, if different from the default `₹15,000 + GST per participant`
- Payment terms, if they differ from the template

If any required detail is missing, ask for it before editing. If the website/domain is missing but email is provided, derive the domain from the email when possible.

## Workflow

1. Identify the bundled base template at this skill's `assets/IKF AI Masterclass - base template.html`.
2. Create a new filename using the client/contact, for example `IKF_AI_Masterclass_Proposal_ClientName.html`.
3. Duplicate the base template into that new file.
4. Research the client before personalizing content.
5. Use the client website as the primary source; use reliable public sources only when the website lacks enough context.
6. Update all client-specific fields and prose, including contact name, designation, email, phone, company, website, industry, and stated business problems.
7. Update the personal transformation section using the contact name, designation, researched business context, and the user's stated problems.
8. Include a concise bullet list of the person's pain points inside the personal transformation section, between the context paragraph and the transformation paragraph. Use 3-5 bullets, phrased as business challenges in the user's language when possible.
9. Keep the 9-pillar accelerator framework intact unless the user asks to alter the program structure. Personalize examples inside the pillars to the client context where appropriate.
10. Assign each pillar a relevance score from 0-100% using department presence, the contact's designation, stated pain points, and researched business context. Higher scores should reflect direct pain-point alignment or a department that exists in the organisation. Lower scores should still remain visible unless the user asks to hide them.
11. Update the single pricing block only. Do not recreate half-day/full-day/two-day format cards.
12. Keep the standard venue and delivery language unless the user provides specific location, remote, multi-city, or special logistics terms.
13. Update payment terms only from user-provided facts.
14. Keep all non-client-specific IKF content unchanged unless the user asks otherwise.
15. Open the edited file in Chrome for preview.
16. Return a clickable local file link to the edited file.

## Personalization Checklist

Replace every occurrence of prior or placeholder client details, including:

- Contact name
- Company name
- Cover subtitle, which must use the company name
- Short company name
- Domain, website, email, phone number, and designation
- Problems/challenges provided by the user
- Industry and business context
- Personal transformation block title and body
- Pain-point bullet list, populated from the user's provided challenges
- "What you are facing" and "what the accelerator can help you become" narrative
- 9-pillar relevance percentages, with scores updated in both the visible text and the `--rel` bar width style
- Accelerator membership price and participant terms
- Inclusion examples that mention client industry
- Travel and venue section, only when special logistics are provided
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
- Search for old format labels such as `Half Day`, `Full Day`, `Two Days`, `Available Masterclass Formats`, `₹50,000`, `₹75,000`, and `₹1,25,000`.
- Verify the 9-pillar framework is present and numbered 01 through 09.

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
