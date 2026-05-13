#!/usr/bin/env python3
import argparse
import datetime as dt
import html
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "template" / "editable-proposal.html"


def esc(value):
    return html.escape(str(value or ""), quote=False)


def slug(value):
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip())
    return value.strip("_") or "Client"


def selected_services(raw):
    aliases = {
        "seo": "seo",
        "search": "seo",
        "search_engine_optimization": "seo",
        "search_engine_optimisation": "seo",
        "ppc": "ppc",
        "performance": "ppc",
        "performance_marketing": "ppc",
        "smm": "smm",
        "social": "smm",
        "social_media": "smm",
        "social_media_management": "smm",
        "branding": "branding_kit",
        "branding_kit": "branding_kit",
        "website": "website",
        "web": "website",
        "amc": "amc",
        "hosting": "hosting",
    }
    result = []
    for item in raw.split(","):
        key = re.sub(r"[^a-z0-9]+", "_", item.strip().lower()).strip("_")
        mapped = aliases.get(key, key)
        if mapped and mapped not in result:
            result.append(mapped)
    return result


def bullet(items, nested=False):
    lines = []
    for item in items:
        if isinstance(item, tuple):
            text, children = item
            lines.append(f'<li contenteditable="true">{esc(text)}<ul>{bullet(children, True)}</ul></li>')
        else:
            lines.append(f'<li contenteditable="true">{esc(item)}</li>')
    return "\n".join(lines) if nested else '<ul class="bullet-list">' + "\n".join(lines) + "</ul>"


def list_tools():
    return """
      <div class="list-tools edit-only">
        <button type="button" class="secondary" onclick="addBullet(this)">Add Bullet</button>
        <button type="button" class="secondary" onclick="addSubBullet(this)">Add Sub-Bullet</button>
        <button type="button" class="secondary" onclick="deleteBullet(this)">Delete Last Bullet</button>
      </div>
    """


def row_tools():
    return """
      <div class="row-tools edit-only">
        <button type="button" class="secondary" onclick="addTableRow(this)">Add Row</button>
        <button type="button" class="secondary" onclick="deleteTableRow(this)">Delete Last Row</button>
      </div>
    """


def section(name, label, title, content):
    return f"""
    <section class="section" data-section="{esc(name)}">
      <h2 contenteditable="true">{esc(label)}</h2>
      <h1 contenteditable="true">{esc(title)}</h1>
      {content}
    </section>
    """


def page(content, extra_class="content-page"):
    return f'<main class="page {extra_class}">{content}</main>'


def image_page(section_name, src, title=None):
    title_html = ""
    if title:
        title_html = f'<div class="cover-title" contenteditable="true">{title}</div>'
    return f"""
    <main class="page brand-page" data-section="{esc(section_name)}">
      <img src="{esc(src)}" alt="{esc(section_name)}">
      {title_html}
    </main>
    """


def title_for(client, services):
    if set(services) == {"seo", "ppc", "smm"}:
        return f"Performance Marketing, SEO and Social Media Management For <span class=\"client\">{esc(client)}</span>"
    labels = {
        "branding_kit": "Branding Kit",
        "website": "Website Development",
        "seo": "SEO",
        "hosting": "Web Hosting",
        "amc": "AMC",
        "ppc": "Performance Marketing",
        "smm": "Social Media Management",
    }
    selected = [labels[s] for s in services if s in labels]
    return f"{esc(', '.join(selected))} for <span class=\"client\">{esc(client)}</span>"


def scope_of_work(services):
    labels = {
        "branding_kit": "Branding Kit",
        "website": "Website Designing and Development",
        "amc": "Annual Website Maintenance",
        "hosting": "Website Hosting",
        "seo": "Search Engine Optimisation",
        "ppc": "Performance Marketing",
        "smm": "Social Media Management",
    }
    ordered = [s for s in ["branding_kit", "website", "amc", "hosting", "seo", "smm", "ppc"] if s in services]
    return section("Scope Of Work", "Scope of Work", "Scope of Work", bullet([labels[s] for s in ordered]) + list_tools())


def seo_section():
    items = [
        ("Website Analysis & Keyword Research", [
            "Keyword Research, Keyword Finalization in mutual discussion with Client",
        ]),
        ("On Page Optimization", [
            "Baseline Keyword Ranking",
            "HTTPS (SSL) Certificate",
            "URL Canonicalization",
            "Set-up Google Search Console",
            "Website Pages Meta Tag Optimization (Title, Description, Keywords) as per the finalized keywords",
            "URL Structure Optimization",
            "Header Tag Optimization suggestions",
            "Website Content Suggestion and Optimization as per the Finalized Keywords",
            "XML Sitemap Monitoring",
            "Robots.txt Optimization",
            "Page Redirection Suggestion",
            "Duplicate Content Checks",
            "Call to Action Check",
            "Navigation Check",
            "Google Analysis Tracking",
            "Image Optimization",
            "Internal Linking to Improve Website Navigation and page visibility",
            "Web Pages Speed Optimization",
            "CSS Optimization",
            "JS Optimization",
            "Footer Optimization Suggestion",
            "Schema Markup Suggestions",
            "Blog Topics Suggestions",
        ]),
        ("Off Page Optimization", [
            "Social Bookmarking",
            "Image Submission*",
            "Infographic Submission*",
            "PPT Submission*",
            "Document Sharing*",
            "Video Submission*",
            "If client opts for these activities, then content is to be provided by client",
        ]),
        ("Blogging Activities", [
            "The blog writing will commence after 1st month of engagement.",
            "Blogs to be written: 2 blogs, 400-500 words each, per month after 1st month of engagement.",
            "Technical content for blog writing will be provided by the client.",
            "Blog topics to be finalised on mutual basis with client involvement.",
            "If a blog is not approved within the same month of submission, it will be carried forward to the following month. It will not be considered or replaced beyond that period.",
        ]),
        ("Reports and Statistics", ["Monthly Progress Report"]),
        ("Exclusions & Limitations", [
            "Website Development & Fixes: We do not make direct changes to the website code.",
            "Website Hosting, Maintenance: We are not responsible for downtime, hosting issues, or server-side problems unless managed by IKF.",
            "Content Writing: Website content creation is not included unless specified.",
            "UI/UX or Design Changes: No design/UI fixes will be done; suggestions may be provided where applicable.",
            "Access Restrictions: Delays or inaccuracies may occur if admin access is not provided on time.",
            "Result Guarantees: SEO is a long-term process and results depend on industry competition, algorithm changes, website structure, etc.",
            "Legacy URL/Redirect Management is not part of scope unless AMC is handled by IKF.",
            "Blog uploading or formatting blogs on CMS will not be handled unless covered under AMC.",
            "Designing banners is not part of IKF's scope and will be charged at actuals if required.",
        ]),
    ]
    content = """
      <h3 contenteditable="true">On Page Optimization</h3>
      <p contenteditable="true">On-Page SEO involves optimizing various elements within the website to improve search engine visibility and user experience.</p>
      <h3 contenteditable="true">Off Page Optimization</h3>
      <p contenteditable="true">Off-Page SEO focuses on building credibility, authority, and backlinks to improve the website's ranking and online presence.</p>
      <h3 contenteditable="true">Plan</h3>
    """ + bullet(items) + list_tools()
    return section("SEO", "Search Engine Optimization (SEO)", "Search Engine Optimization (SEO)", content)


def smm_section():
    content = """
      <h3 contenteditable="true">Platforms</h3>
    """ + bullet(["Instagram", "Facebook", "LinkedIn"]) + """
      <h3 contenteditable="true">Social Media Deliverables</h3>
    """ + bullet([
        "Develop a monthly content calendar featuring a mix of promotional posts, industry news, and engaging multimedia content.",
        "Static Image Posts: Visually appealing creatives with compelling captions. Deliverables as per mandate.",
        "Reels: Engaging short-form videos, maximum up to 20 seconds. Deliverables as per mandate.",
        "Story Updates: Stories provided by the client are ready for upload and will remain in their current state unless further instructions are outlined in the mandate.",
        "Comment & Message Management: Prompt responses to user queries, comments, and DMs. ORM will be done once during any working day.",
        "User-Generated Content Sharing: Featuring customer-generated content via Stories when tagged by the user.",
    ]) + """
      <h3 contenteditable="true">Exclusions</h3>
    """ + bullet([
        "Customization of Stories with engagement activity like polls, quizzes, ask-me-anything, etc.",
        "Manually sending follow requests to users for the page.",
        "Requesting users to tag the page when they check in at a location.",
        "Asking users who share positive reviews on social media to post the same on Google My Business.",
        "Past inquiries, messages, or comments received before the mandate start date will not be covered.",
    ]) + """
      <h3 contenteditable="true">Page & Profile Optimization</h3>
    """ + bullet([
        "Profile & Cover Image Management: Designing a banner once every six months.",
        "About Section & CTA Optimization.",
        "Hashtag Strategy Implementation.",
        "Pinned Posts as per mutually agreed strategy.",
        "Highlights creation and cover design reviewed once every six months, maximum 8 highlights.",
    ]) + """
      <h3 contenteditable="true">Analytics & Reporting</h3>
    """ + bullet([
        "Monthly Performance Report for posts and reels designed by IKF, shared by the 5th of the following month.",
        "Monthly review strategy and meeting to take place online only.",
        "Customized reporting beyond IKF standard format will be charged at actuals.",
        "No reporting of UGC to be shared by IKF.",
        "Visiting Client Premises for monthly review is excluded.",
    ]) + """
      <h3 contenteditable="true">Working Hours</h3>
      <p contenteditable="true">Our regular working hours are Monday to Friday, 10:00 AM to 6:00 PM. We observe weekly offs on Saturdays and Sundays.</p>
      <h3 contenteditable="true">Key Measurable Criteria</h3>
    """ + bullet([
        "Improvisation in the existing digital presence across the platforms.",
        "Reaching the targeted audience and geographies.",
        "Increase in followers, brand building, and page engagements through paid campaigns as applicable.",
    ]) + """
      <div class="two-col">
        <div>
          <h3 contenteditable="true">Our Responsibilities</h3>
    """ + bullet([
        "Get a better understanding of the requirement, timeline and deliverables.",
        "Prepare the action plan and share the milestones.",
        "Coordinate with Client for Social Media Strategy.",
        "Execute - Approve - Post.",
    ]) + """
        </div>
        <div>
          <h3 contenteditable="true">Client Responsibilities</h3>
    """ + bullet([
        "Provide timely feedback and approvals on creatives and copies.",
        "Provide Brand Guidelines Document.",
        "Provide content in open files, DOC and DOCX, specifications, PDF documents, and images as required.",
        "Provide high resolution product images, specifications, logos and demo videos if any.",
        "Approval on the monthly content bank.",
        "Providing access of all the desired channels.",
    ]) + """
        </div>
      </div>
    """ + list_tools()
    return section("SMM", "Social Media Management", "Social Media Management", content)


def ppc_section():
    content = """
      <h3 contenteditable="true">Objective</h3>
    """ + bullet([
        "Increase brand reach and awareness across target audiences.",
        "Generate quality leads.",
        "Optimize media spends through real-time data and performance tracking.",
        "Establish a full-funnel strategy across awareness, consideration, and conversion stages.",
    ]) + """
      <h3 contenteditable="true">Channel-Wise Strategy & Deliverables</h3>
    """ + bullet([
        "Campaign Strategy: Google & Meta Ads.",
        "Funnel-based approach: Awareness to Consideration to Conversion.",
        "Custom audiences based on interest, behaviour, lookalikes, and retargeting pools.",
        "Dynamic ad formats testing for performance.",
        "Campaign strategy and targeting plan.",
        "Creative design at actuals.",
        "Ad copywriting aligned with CTA and audience funnel stage.",
        "Pixel setup and custom events tracking if applicable.",
        "Ongoing A/B testing and optimization.",
        "Monthly performance reporting.",
    ]) + """
      <div class="two-col">
        <div>
          <h3 contenteditable="true">Our Responsibilities</h3>
    """ + bullet([
        "Development of a tailored ad strategy based on business goals and target audience.",
        "Research and identification of target audience segments.",
        "Creation of high-quality ad creatives and ad copywriting.",
        "Setup and daily management of ad campaigns.",
        "A/B testing of ad creatives and targeting options.",
        "Efficient allocation and management of ad spend.",
        "Advanced targeting and retargeting strategies.",
        "Monthly performance reports and recommendations.",
        "Competitor analysis.",
        "Custom Audiences and Lookalike Audiences if applicable.",
    ]) + """
        </div>
        <div>
          <h3 contenteditable="true">Client Responsibilities</h3>
    """ + bullet([
        "Approval of the plan, milestones and targeting.",
        "Providing expectations, benchmarking and requirements for targeting.",
        "Providing timely feedback and approvals on targeting, conversion status and outcome feedback.",
        "Access to Meta Business Manager, Google Ads, and LinkedIn Campaign Manager as per platform scope.",
        "Creative assets or brand guidelines if available.",
    ]) + """
        </div>
      </div>
    """ + list_tools()
    return section("Performance Marketing", "Performance Marketing", "Performance Marketing", content)


def commercial_section(args, services):
    rows = []
    if "seo" in services:
        rows.append(["SEO", args.seo_scope or "50 SEO keywords", args.seo_price or "₹50,000", args.seo_amount or "₹50,000 per month"])
    if "ppc" in services:
        rows.append(["PPC", "Clicks as consumed", args.ppc_rate or "₹10 per click", "As per actual clicks"])
    if "smm" in services:
        rows.append(["Social Media Management", args.smm_scope or "50 posts per month: 25 reels, remaining text and static posts", args.smm_rate or "Included", args.smm_amount or "Included"])
    table_rows = "\n".join(
        f'<tr><td contenteditable="true">{esc(a)}</td><td contenteditable="true">{esc(b)}</td><td class="money" contenteditable="true">{esc(c)}</td><td class="money" contenteditable="true">{esc(d)}</td></tr>'
        for a, b, c, d in rows
    )
    content = f"""
      <table>
        <thead>
          <tr class="table-title"><th colspan="4">Commercial Proposal</th></tr>
          <tr><th>Service</th><th>Scope</th><th>Rate</th><th>Amount</th></tr>
        </thead>
        <tbody>{table_rows}</tbody>
      </table>
      {row_tools()}
    """
    return section("Commercial Proposal", "Commercial Proposal", "Commercial Proposal", content)


def terms_section():
    content = """
      <h3 contenteditable="true">Payment Terms</h3>
    """ + bullet([
        "100% monthly payment advance against the Invoice.",
        "Monthly advance payment on or before 5th day of every month on raise of invoice.",
        "Invoice not paid by due date will carry interest @ 18% P.A.",
        "If payment done using credit card, additional charges if any to be borne by client.",
        "GST @ 18.00% applicable.",
        "Payment to be drawn in favor of I Knowledge Factory Pvt. Ltd.",
        "GSTIN: 27AAACI9588A1ZF",
        "PAN: AAACI9588A",
        "Contract Duration: 12 months",
    ]) + """
      <h3 contenteditable="true">General Terms</h3>
    """ + bullet([
        "I Knowledge Factory Pvt. Ltd. will carry out work within 7 days where an agreement is provided by email or PO along with advance payment.",
        "This commercial is valid for 7 days from the proposal date.",
        "I Knowledge Factory Pvt. Ltd. cannot take responsibility for copyright infringements caused by materials submitted by the client.",
        "Any additional platforms will be charged additionally at Rs. 5,000 per month per platform.",
        "Any additional creative assets not included in the units mentioned above will be charged at standard per-unit rate.",
        "Maximum 2-3 iterations per post; additional changes will be charged Rs. 500 per post.",
        "Creatives will be shared in PNG or JPG format only.",
        "Open files of social media creative assets will not be shared.",
        "Monthly meetings are to take place only on virtual basis.",
        "Blogs are 400-500 words each; any blog beyond 500 words is counted as an additional blog or charged at Rs. 7 per word.",
        "Designing banners is not part of IKF's scope and will be charged at actuals if required.",
    ]) + """
      <h3 contenteditable="true">Images & Visual Assets Policy</h3>
    """ + bullet([
        "IKF maintains a corporate Shutterstock account for licensed stock assets.",
        "Stock images remain the property of Shutterstock, are licensed and not sold, and cannot be resold, redistributed or transferred to third parties.",
        "AI-generated visuals are created using third-party AI platforms that permit commercial usage. Ownership exclusivity is not guaranteed.",
        "Editable prompts, source files or generation history are not included.",
        "This engagement is strictly for social media marketing. Client receives commercial usage rights for social media only.",
    ]) + """
      <h3 contenteditable="true">Validity, Termination and Refund Policy</h3>
    """ + bullet([
        "Engagement duration is valid for 12 months from receipt of PO.",
        "Agency reserves the right to hold the work if payments are delayed.",
        "Client would be charged for the period where there was delay due to no response, no approval or no raw content from the Client.",
        "Termination communication should be made via email at least 30 days prior to service expiry or the next billing cycle.",
        "All retainer-based services, including PPC, are planned, staffed and executed monthly. Once the service period has commenced, fees paid for that month are non-refundable.",
        "Outstation travel, accommodation and incidental charges are at actuals.",
        "Video production and anything beyond the proposal scope will be charged at actuals.",
        "IKF will have reasonable right to publicize its involvement in the project, except information prohibited by confidentiality clause.",
        "These terms and conditions supersede any previously stated terms and conditions in the proposal.",
    ]) + list_tools()
    return section("Terms & Conditions", "Terms & Conditions", "Terms & Conditions", content)


def build_body(args, services):
    title = title_for(args.client, services)
    body = [
        image_page("Cover", "assets/brand-pages/cover-base.jpeg", title),
        image_page("About Us", "assets/brand-pages/about-us-expertise.jpeg"),
        image_page("They Believe In Us", "assets/brand-pages/they-believe-in-us.jpeg"),
    ]
    content_sections = [scope_of_work(services)]
    if "seo" in services:
        content_sections.append(seo_section())
    if "smm" in services:
        content_sections.append(smm_section())
    if "ppc" in services:
        content_sections.append(ppc_section())
    content_sections.append(commercial_section(args, services))
    content_sections.append(terms_section())
    body.append(page("\n".join(content_sections)))
    return "\n".join(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--website", default="")
    parser.add_argument("--industry", default="")
    parser.add_argument("--services", required=True, help="Comma-separated service keys")
    parser.add_argument("--seo-price", default="")
    parser.add_argument("--seo-scope", default="")
    parser.add_argument("--seo-amount", default="")
    parser.add_argument("--ppc-rate", default="")
    parser.add_argument("--smm-scope", default="")
    parser.add_argument("--smm-rate", default="")
    parser.add_argument("--smm-amount", default="")
    parser.add_argument("--output-dir", default="client proposals")
    args = parser.parse_args()

    services = selected_services(args.services)
    if not services:
        raise SystemExit("No valid services selected.")

    title_text = f"IKF Commercial Proposal - {args.client}"
    html_text = TEMPLATE.read_text()
    html_text = html_text.replace("{{TITLE}}", esc(title_text))
    html_text = html_text.replace("{{BODY}}", build_body(args, services))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source_brand = ROOT / "assets" / "brand-pages"
    target_brand = out_dir / "assets" / "brand-pages"
    target_brand.mkdir(parents=True, exist_ok=True)
    for asset in source_brand.iterdir():
        if asset.is_file():
            shutil.copy2(asset, target_brand / asset.name)
    out_file = out_dir / f"IKF_Commercial_Proposal_{slug(args.client)}_{dt.date.today().isoformat()}.html"
    out_file.write_text(html_text)
    print(out_file.resolve())


if __name__ == "__main__":
    main()
