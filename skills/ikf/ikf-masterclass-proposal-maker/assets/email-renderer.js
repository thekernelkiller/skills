let data = $input.first().json.output ?? $input.first().json;

if (typeof data === 'string') {
  data = JSON.parse(data);
}

if (data.output) {
  data = typeof data.output === 'string' ? JSON.parse(data.output) : data.output;
}

const form = (() => {
  try {
    return $('Loop Over Items').item.json;
  } catch (error) {
    return $input.first().json;
  }
})();

data = {
  ...form,
  ...data,
  email_address: data.email_address || form['Email Address'],
  company_name: data.company_name || form['Company Name'],
  contact_name: data.contact_name || form['Full Name'],
  contact_first_name: data.contact_first_name || String(form['Full Name'] || '').split(' ')[0],
  designation: data.designation || form.Designation,
};

const pillars = [
  ['01', 'Leadership & Strategy', 'Rethinking decision-making, priorities, and growth choices through an AI-native leadership lens.'],
  ['02', 'Sales & Marketing', 'Using AI-native thinking to improve lead quality, campaign planning, customer communication, and market insight.'],
  ['03', 'HR & Recruitment', 'Improving hiring, employee communication, role clarity, training workflows, and people decisions.'],
  ['04', 'Finance & Accounts', 'Strengthening reporting, analysis, controls, documentation, and management visibility.'],
  ['05', 'Customer Service & Experience', 'Identifying opportunities to improve response quality, service consistency, and customer understanding.'],
  ['06', 'Operations', 'Applying AI-native thinking to process bottlenecks, coordination, productivity, and daily execution.'],
  ['07', 'Procurement & Purchase', 'Improving vendor analysis, purchase planning, negotiation preparation, and procurement workflows.'],
  ['08', 'Production & Manufacturing', 'Exploring AI opportunities around planning, quality, wastage, maintenance, documentation, and shop-floor insight.'],
  ['09', 'Projects, Engineering & Digital Transformation', 'Building practical transformation roadmaps across projects, engineering teams, systems, and digital initiatives.'],
];

function esc(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function pct(id) {
  return Math.max(0, Math.min(100, Number((data.relevance_scores || {})[id] || 0)));
}

function p(text, styles = '') {
  return `<p style="margin:0 0 16px 0;${styles}">${esc(text)}</p>`;
}

function section(label, title, body) {
  return `
    <tr><td style="padding:0 32px 32px 32px;">
      ${label ? `<div style="font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:#6c3fc7;font-weight:700;margin:0 0 5px 0;">${label}</div>` : ''}
      <div style="font-size:24px;line-height:1.2;color:#1a1f5e;margin:0 0 14px 0;padding:0 0 10px 0;border-bottom:1.5px solid #dddcf0;font-weight:700;">${title}</div>
      ${body}
    </td></tr>`;
}

function pillarRows() {
  const cells = pillars.map(([id, title, desc]) => {
    const score = pct(id);
    const remaining = Math.max(0, 100 - score);
    return `
      <td width="33.33%" valign="top" style="width:33.33%;padding:0 6px 12px 6px;">
        <table role="presentation" width="100%" height="210" cellpadding="0" cellspacing="0" style="width:100%;height:210px;border-collapse:separate;background:#f7f6ff;border:1px solid #dddcf0;border-radius:8px;table-layout:fixed;">
          <tr>
            <td valign="top" height="142" style="height:142px;padding:12px 12px 0 12px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                <tr>
                  <td width="32" valign="top" style="padding:0 8px 0 0;">
                    <div style="width:26px;height:26px;border-radius:50%;background:#1a1f5e;color:#fff;font-size:11px;line-height:26px;text-align:center;font-weight:700;">${id}</div>
                  </td>
                  <td valign="top">
                    <div style="font-size:13px;line-height:1.25;color:#1a1f5e;font-weight:700;margin:0 0 5px 0;">${esc(title)}</div>
                    <div style="font-size:12px;line-height:1.38;color:#55556e;margin:0;">${esc(desc)}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td valign="bottom" height="58" style="height:58px;padding:0 12px 12px 12px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                <tr>
                  <td>
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#dedbf5;">
                      <tr>
                        <td width="${score}%" style="height:7px;line-height:7px;font-size:0;background:#6c3fc7;">&nbsp;</td>
                        <td width="${remaining}%" style="height:7px;line-height:7px;font-size:0;background:#dedbf5;">&nbsp;</td>
                      </tr>
                    </table>
                  </td>
                  <td width="34" align="right" style="font-size:12px;color:#6c3fc7;font-weight:700;">${score}%</td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>`;
  });

  const rows = [];
  for (let i = 0; i < cells.length; i += 3) {
    rows.push(`<tr>${cells.slice(i, i + 3).join('')}</tr>`);
  }
  return rows.join('');
}

const painPoints = (Array.isArray(data.pain_points) ? data.pain_points : []).map(item =>
  `<li style="margin:0 0 6px 0;padding-left:2px;color:#5a4200;">${esc(item)}</li>`
).join('');

const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${esc(data.subject_line || 'IKF AI Native Thinking Masterclass Proposal')}</title>
</head>
<body style="margin:0;padding:0;background:#eceaf6;font-family:Calibri,Arial,sans-serif;color:#1a1a2e;font-size:14px;">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">${esc(data.preview_text || '')}</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;background:#eceaf6;">
    <tr><td align="center">
      <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="width:640px;max-width:640px;border-collapse:collapse;background:#fff;table-layout:fixed;">
        <tr><td><img src="https://res.cloudinary.com/dvsroizwe/image/upload/v1778483838/ChatGPT_Image_May_11_2026_12_45_04_PM_v8fpob.png" alt="AI Native Thinking Masterclass for Enterprises" width="640" style="display:block;width:640px;max-width:640px;height:auto;border:0;"></td></tr>
        <tr><td style="background:#1a1f5e;padding:34px 32px 30px 32px;">
          <div style="font-size:32px;line-height:1.15;color:#fff;margin:0 0 6px 0;font-weight:700;">AI Native Thinking Masterclass</div>
          <div style="font-size:16px;line-height:1.45;color:#c0bfee;margin:0;font-style:italic;">Prepared for ${esc(data.company_name)}</div>
        </td></tr>
        <tr><td style="background:#f7f6ff;border-bottom:1px solid #dddcf0;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;"><tr>
            ${['25+ years in business', '1500+ clients served', '20+ industries', '100+ leadership forums', 'Pune, India'].map((x, i, arr) => `<td align="center" valign="middle" style="padding:15px 8px;color:#1a1f5e;font-size:13px;line-height:1.3;font-weight:700;letter-spacing:.1px;${i === arr.length - 1 ? '' : 'border-right:1px solid #dddcf0;'}">${x}</td>`).join('')}
          </tr></table>
        </td></tr>
        <tr><td style="height:32px;line-height:32px;font-size:0;background:#ffffff;">&nbsp;</td></tr>

        ${section('Impact of AI-Native Thinking', `Recommendation For ${esc(data.contact_name)}`, `
          <div style="background:#fffcef;border:1.5px solid #e8c840;border-radius:10px;padding:22px 24px;color:#5a4200;font-size:16px;line-height:1.72;">
            <div style="color:#6b4d00;font-size:15px;line-height:1.35;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 12px 0;">${esc(data.transformation_heading)}</div>
            ${p(data.transformation_context)}
            <p style="margin:0 0 16px 0;">AI-native thinking will help you focus on:</p>
            <ul style="margin:0 0 16px 20px;padding:0;color:#5a4200;">${painPoints}</ul>
            ${p(data.transformation_path)}
            <p style="margin:0;font-weight:700;">${esc(data.transformation_outcome)}</p>
          </div>
        `)}

        ${section('3 Month Program Structure', '9-Pillar AI-Native Thinking Framework', `
          <p style="font-size:13px;line-height:1.65;color:#55556e;margin:-4px 0 14px 0;">Impact of each individual session for your profession.</p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">${pillarRows()}</table>
          <p style="color:#88889a;font-size:13px;line-height:1.45;font-style:italic;margin:12px 0 0 0;">${esc(data.program_note)}</p>
        `)}

        ${section('', 'Membership Investment', `
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate;border:2px solid #6c3fc7;border-radius:10px;overflow:hidden;">
            <tr><td style="background:#6c3fc7;color:#fff;padding:16px 18px;"><div style="font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#d4cef8;">Investment per participant</div><div style="font-size:17px;font-weight:700;">IKF AI Native Thinking Masterclass</div></td></tr>
            <tr><td style="padding:20px 22px;"><table role="presentation" width="100%"><tr><td valign="top" width="36%"><div style="font-size:34px;line-height:1;font-weight:700;color:#1a1f5e;">₹15,000 <span style="font-size:16px;line-height:1.2;font-weight:700;color:#1a1f5e;">per participant</span></div><div style="color:#55556e;font-size:13px;margin:4px 0 12px;">+ GST applicable</div><p style="color:#55556e;font-size:14px;line-height:1.6;margin:0;">Membership is valid for one individual participant only and is non-transferable. Department heads accompanying the registered participant for a relevant session are charged <b>₹1,500 + GST</b> per session.</p></td><td valign="top" style="color:#55556e;font-size:14px;line-height:1.5;">✓ 3-month structured transformation journey<br>✓ 9 physical masterclasses across key business functions<br>✓ 3 online review and Q&A sessions<br>✓ Approximately 3 hours per session<br>✓ Session notes, frameworks, worksheets, assignments, and implementation exercises<br>✓ No recordings; sessions are designed for active participation and discussion</td></tr></table></td></tr>
          </table>
        `)}

        ${section('Scope of Engagement', 'Inclusions and Exclusions', `
          <table role="presentation" width="100%"><tr>
            <td valign="top" width="50%" style="padding-right:7px;"><div style="background:#eaf3de;color:#3b6d11;padding:9px 14px;font-weight:700;">What Is Included</div><div style="border:1px solid #dddcf0;border-top:0;padding:12px 14px;color:#55556e;font-size:14px;line-height:1.5;">✓ All concepts, frameworks, and discussion content (shareable)<br>✓ Prompting frameworks and business productivity guidance<br>✓ Industry-specific AI use cases and practical examples<br>✓ Open Q&A and leadership discussion</div></td>
            <td valign="top" width="50%" style="padding-left:7px;"><div style="background:#fff5f5;color:#a32d2d;padding:9px 14px;font-weight:700;">What Is Not Included</div><div style="border:1px solid #dddcf0;border-top:0;padding:12px 14px;color:#55556e;font-size:14px;line-height:1.5;">✗ Presentation file / slide deck (not provided to participants)<br>✗ AI paid subscriptions - ChatGPT Plus, Claude Pro, etc. (arranged by client)<br>✗ AI implementation, development, or deployment work<br>✗ Custom AI workflow builds or technical integrations</div></td>
          </tr></table>
        `)}

        ${section('Financials', 'Payment Terms', `<table role="presentation" width="100%"><tr><td valign="top" style="background:#1a1f5e;border-radius:8px;padding:20px 22px;color:#c0bfee;"><div style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#8887cc;font-weight:700;">Advance - At Registration</div><div style="font-size:36px;line-height:1;color:#fff;font-weight:700;margin:4px 0 6px;">100%</div><div style="font-size:14px;line-height:1.5;">Required to confirm participation in the masterclass.</div></td></tr></table><p style="color:#88889a;font-size:13px;line-height:1.45;font-style:italic;margin:12px 0 0;">Payment via NEFT / RTGS / Cheque in favour of I Knowledge Factory Pvt. Ltd. Bank details shared upon acceptance.</p>`)}

        ${section('To Proceed', 'How to Confirm This Engagement', [1,2,3,4].map((n, i) => {
          const steps = ['Confirm participant names, designations, email addresses, and phone numbers', 'Issue a Purchase Order or written confirmation of acceptance', 'Process 100% advance payment to confirm participation', 'Registrations are non-transferable, non-shareable, and non-refundable'];
          return `<table role="presentation" width="100%"><tr><td width="34" valign="top"><div style="width:26px;height:26px;border-radius:50%;background:#1a1f5e;color:#fff;font-size:12px;line-height:26px;text-align:center;font-weight:700;">${n}</div></td><td style="color:#55556e;font-size:14px;line-height:1.65;padding-bottom:10px;">${steps[i]}</td></tr></table>`;
        }).join(''))}

        ${section('About I Knowledge Factory Pvt. Ltd', 'Who We Are', `
          <p style="font-size:16px;line-height:1.75;color:#55556e;margin:0 0 12px 0;">I Knowledge Factory Pvt. Ltd. (IKF) is a business transformation company with over 25 years of experience, having partnered with 1,500+ organizations across 20+ industries, including Tata Group, Kirloskar Group, Mahindra Group, Kalyani Group, Force Motors, and Pidilite Industries.</p>
          <p style="font-size:16px;line-height:1.75;color:#55556e;margin:0 0 12px 0;">From the early internet era to digital transformation and now the age of AI, IKF has continuously evolved to help businesses adapt to technological change, strengthen customer engagement, and create sustainable business value. Headquartered in Pune, IKF continues to work with business leaders to navigate and capitalize on emerging technology shifts.</p>
          <div style="background:#f0efff;border-left:4px solid #6c3fc7;border-radius:0 8px 8px 0;padding:14px 18px;color:#3c3489;font-size:16px;line-height:1.65;font-style:italic;">AI adoption does not start with tools. It starts with leadership thinking. We understand business first. Then we implement AI.</div>
        `)}

        <tr><td style="background:#1a1f5e;padding:30px 44px;text-align:center;color:#e0dfff;">
          <div style="color:#c0bfee;font-size:18px;line-height:1.6;font-style:italic;margin:0 auto 18px;">AI will not replace leadership. But leaders who leverage AI will redefine organisational growth.</div>
          <div style="font-size:14px;line-height:1.6;"><a href="https://www.ikf.solutions" target="_blank" style="color:#e0dfff;text-decoration:none;">www.ikf.solutions</a> | <a href="mailto:masterclass@ikf.co.in" style="color:#e0dfff;text-decoration:none;">masterclass@ikf.co.in</a> | <a href="tel:+919503939911" style="color:#e0dfff;text-decoration:none;">+91 95039 39911</a></div>
          <table role="presentation" width="100%" style="margin-top:20px;"><tr><td width="50%" valign="top" style="border:1px solid rgba(255,255,255,0.22);padding:18px;color:#d9d9f2;font-size:14px;line-height:1.7;text-align:left;">I Knowledge Factory Pvt Ltd<br>6th Floor, International Business Bay (IBB),<br>Opp. Kumar Pacific Mall, Shankar Sheth Road,<br>Guru Nanak Nagar, Pune, Maharashtra - 411042<br>GSTIN No.: 27AAACI9588A1ZF</td><td width="50%" valign="top" style="border:1px solid rgba(255,255,255,0.22);padding:18px;color:#d9d9f2;font-size:14px;line-height:1.7;text-align:left;"><b>Bank Details:</b><br>Account Name: I Knowledge Factory Pvt Ltd<br>Bank Name: ICICI Bank Ltd<br>Branch: Erandwane, Pune<br>Account Type: Current Account<br>Account Number: 646105050465<br>IFSC Code: ICIC0006461</td></tr></table>
        </td></tr>
        <tr><td style="color:#55556e;background:#f7f6ff;border-top:1px solid #dddcf0;text-align:center;padding:10px 18px;font-size:12px;line-height:1.5;font-style:italic;">This proposal is confidential and prepared exclusively for ${esc(data.contact_name)} / ${esc(data.company_name)}.</td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`;

return [{
  json: {
    ...data,
    html,
  },
}];
