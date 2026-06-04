---
name: ikf-masterclass-proposal-maker
description: Create and personalize IKF AI Native Thinking Masterclass proposal HTML files from the locked base template. Use when creating or updating a client-specific IKF masterclass or 3-month masterclass proposal, including client web research, required-input checks, business-problem personalization, copying the base template, replacing every client reference, updating personal transformation copy, updating fixed 9-pillar relevance scores, keeping the single pricing block, verifying stale references, and opening the edited proposal in Chrome for preview.
---

# IKF Masterclass Proposal Maker

## Core Rules

- Use the bundled asset `assets/IKF AI Masterclass - base template.html` as the source template.
- Treat the base template as locked. Do not edit it.
- Always duplicate the base template and make changes only in the new client file.
- Preserve layout, structure, styling, spacing, and design unless the user explicitly requests a design or layout change.
- Do not add the removed cover metadata block (`Prepared for` / `Prepared by`) unless the user explicitly asks for it.
- Set the cover subtitle to `Prepared for <Client Company Name>`; do not use the contact person's name there.
- Treat the commercial offer as one masterclass membership price, not multiple masterclass formats.
- Treat the standard commercial, scope, payment, footer, bank, and IKF background content as hardcoded template content unless the user explicitly asks to change it.
- Keep default payment terms as 100% advance payment to confirm participation unless the user provides different terms.
- Include the current base-template section sequence in email proposal templates, including Inclusions and Exclusions, Payment Terms, How to Confirm This Engagement, About I Knowledge Factory Pvt. Ltd, and footer sections. Do not include Travel and Venue, the standalone After the Masterclass / Value Delivered block, or About the Speaker.
- The 9 pillar titles and descriptions are fixed. AI output must only provide relevance scores for the fixed pillars.
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
7. Update the Impact of AI-Native Thinking section using the contact name, researched business context, and the user's stated problems.
8. Include a concise bullet list of the person's pain points inside the personal transformation section, between the context paragraph and the transformation paragraph. Use 3-5 bullets, phrased as business challenges in the user's language when possible.
9. Keep the 9-pillar masterclass framework intact. Do not let AI rename pillar titles or rewrite pillar descriptions in email proposal templates.
10. Assign each pillar a relevance score from 0-100% using department presence, the contact's designation, stated pain points, and researched business context. Higher scores should reflect direct pain-point alignment or a department that exists in the organisation. Lower scores should still remain visible unless the user asks to hide them.
11. Keep the single pricing block as the hardcoded masterclass price unless the user provides a different price. Do not recreate half-day/full-day/two-day format cards.
12. Keep all non-client-specific IKF content unchanged unless the user asks otherwise. This includes the About I Knowledge Factory Pvt. Ltd section, investment details, inclusions/exclusions, payment terms, footer contact details, company address, and bank details.
13. In email proposal templates, keep customisation concentrated in the personal transformation section, client/company references, the `relevance_scores` object for fixed pillar IDs, and the program note.
14. Preserve the current post-pricing sections from the base template in email proposal templates. Keep their standard content hardcoded unless the user explicitly asks to change it. Do not reintroduce the removed Travel and Venue or Value Delivered sections.
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
- Impact of AI-Native Thinking block title and body
- Pain-point bullet list, populated from the user's provided challenges
- "What you are facing" and "what the masterclass can help you become" narrative
- 9-pillar relevance percentages only; titles and descriptions must remain fixed:
  - 01 Leadership & Strategy
  - 02 Sales & Marketing
  - 03 HR & Recruitment
  - 04 Finance & Accounts
  - 05 Customer Service & Experience
  - 06 Operations
  - 07 Procurement & Purchase
  - 08 Production & Manufacturing
  - 09 Projects, Engineering & Digital Transformation
- Masterclass membership price and participant terms, only when explicitly changed
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
