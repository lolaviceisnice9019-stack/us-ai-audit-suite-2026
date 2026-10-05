"""Regulation catalog: US AI obligations relevant in 2026.

Each entry is a check with a stable ID, jurisdiction, statute, effective date,
the concrete requirement, and the evidence an auditor should demand.

Dates and scopes below were compiled from public legal reporting current to
October 2026 (White House EO of Dec 11 2025; White House National Policy
Framework of Mar 20 2026; Colorado SB 24-205 as amended; Texas HB 149;
California SB 53, AB 2013, SB 942 as amended; Utah SB 149; NYC Local Law 144;
Illinois AIVIA/HB 3773). This catalog is a compliance aid, not legal advice.
"""

from __future__ import annotations

REGULATIONS: list[dict] = [
    # ---------------- Colorado AI Act (SB 24-205, delayed to 2026-06-30) ----
    {
        "id": "CO-AIA-01",
        "jurisdiction": "Colorado",
        "law": "Colorado AI Act (SB 24-205)",
        "effective": "2026-06-30",
        "severity": "high",
        "requirement": (
            "Developer/deployer of a HIGH-RISK AI system (one that makes or is a "
            "substantial factor in a consequential decision: employment, housing, "
            "credit, education, healthcare, insurance, legal, government services) "
            "must use reasonable care to protect consumers from algorithmic "
            "discrimination."
        ),
        "evidence_prompt": (
            "Describe any AI feature that influences consequential decisions, the "
            "impact assessment performed, and discrimination mitigation measures."
        ),
    },
    {
        "id": "CO-AIA-02",
        "jurisdiction": "Colorado",
        "law": "Colorado AI Act (SB 24-205)",
        "effective": "2026-06-30",
        "severity": "high",
        "requirement": (
            "Deployers of high-risk AI must complete an impact assessment before "
            "deployment, review it at least annually and within 90 days of any "
            "intentional and substantial modification."
        ),
        "evidence_prompt": (
            "Provide the most recent impact assessment date and the review cadence."
        ),
    },
    {
        "id": "CO-AIA-03",
        "jurisdiction": "Colorado",
        "law": "Colorado AI Act (SB 24-205)",
        "effective": "2026-06-30",
        "severity": "medium",
        "requirement": (
            "Consumers interacting with an AI system must be clearly and "
            "conspicuously disclosed that they are interacting with AI, unless "
            "obvious to a reasonable person."
        ),
        "evidence_prompt": (
            "Show where in the product UI the AI-interaction disclosure appears."
        ),
    },
    {
        "id": "CO-AIA-04",
        "jurisdiction": "Colorado",
        "law": "Colorado AI Act (SB 24-205)",
        "effective": "2026-06-30",
        "severity": "high",
        "requirement": (
            "For adverse consequential decisions, consumers must receive a "
            "statement of reasons, an opportunity to correct incorrect data, and "
            "an appeal route with human review where technically feasible."
        ),
        "evidence_prompt": (
            "Describe the adverse-action notice and the human appeal channel."
        ),
    },
    # ---------------- Texas TRAIGA (HB 149, effective 2026-01-01) -----------
    {
        "id": "TX-TRAIGA-01",
        "jurisdiction": "Texas",
        "law": "Texas Responsible AI Governance Act (HB 149)",
        "effective": "2026-01-01",
        "severity": "critical",
        "requirement": (
            "Prohibited practices: developing or deploying AI with the INTENT to "
            "unlawfully discriminate against a protected class, to incite "
            "self-harm or criminal activity, or to produce child sexual abuse "
            "material. Liability is intent-based; the AG enforces with civil "
            "penalties of $10k-$200k per violation after a 60-day cure period."
        ),
        "evidence_prompt": (
            "List prohibited-use policies, acceptable-use enforcement, and any "
            "intent-review process for high-risk features."
        ),
    },
    {
        "id": "TX-TRAIGA-02",
        "jurisdiction": "Texas",
        "law": "Texas Responsible AI Governance Act (HB 149)",
        "effective": "2026-01-01",
        "severity": "medium",
        "requirement": (
            "Limits on capturing or using biometric identifiers via AI systems "
            "for identification without consent; healthcare providers must "
            "disclose AI use in treatment or diagnosis to patients."
        ),
        "evidence_prompt": (
            "Describe any biometric processing and any healthcare-facing AI "
            "disclosures, or state that neither applies."
        ),
    },
    # ---------------- California SB 53 (TFAIA, effective 2026-01-01) --------
    {
        "id": "CA-SB53-01",
        "jurisdiction": "California",
        "law": "Transparency in Frontier AI Act (SB 53)",
        "effective": "2026-01-01",
        "severity": "info",
        "requirement": (
            "SCOPE CHECK: SB 53 binds 'frontier developers' — organizations that "
            "trained a foundation model using >10^26 integer/floating-point "
            "operations. 'Large frontier developers' (>$500M annual revenue) owe "
            "a public frontier AI framework; all frontier developers owe "
            "pre-deployment transparency reports."
        ),
        "evidence_prompt": (
            "State whether the organization has trained, or begun training, any "
            "model above the 10^26 compute threshold. If not, mark N/A."
        ),
    },
    {
        "id": "CA-SB53-02",
        "jurisdiction": "California",
        "law": "Transparency in Frontier AI Act (SB 53)",
        "effective": "2026-01-01",
        "severity": "high",
        "requirement": (
            "If in scope: publish a transparency report before/concurrently with "
            "deploying a frontier model (release date, modalities, languages, "
            "intended uses, restrictions, user contact mechanism); report "
            "critical safety incidents to Cal OES within 15 days (24 hours if "
            "imminent threat); maintain whistleblower channels. Penalties up to "
            "$1M per violation."
        ),
        "evidence_prompt": (
            "Provide the transparency report URL and incident-reporting runbook, "
            "or mark N/A if out of scope per CA-SB53-01."
        ),
    },
    # ---------------- California AB 2013 (effective 2026-01-01) -------------
    {
        "id": "CA-AB2013-01",
        "jurisdiction": "California",
        "law": "AI Training Data Transparency Act (AB 2013)",
        "effective": "2026-01-01",
        "severity": "medium",
        "requirement": (
            "Developers of generative AI systems or services released or "
            "substantially modified after Jan 1 2022 must post documentation on "
            "training data: sources, how data is used, number of data points, "
            "whether protected by copyright, whether personal information is "
            "included, and cleaning/processing methods."
        ),
        "evidence_prompt": (
            "Provide the training-data documentation page, or state that no "
            "generative AI is developed (consuming third-party APIs only)."
        ),
    },
    # ---------------- California SB 942 (AI Transparency Act, ~2026-08) -----
    {
        "id": "CA-SB942-01",
        "jurisdiction": "California",
        "law": "California AI Transparency Act (SB 942, as amended)",
        "effective": "2026-08-02",
        "severity": "medium",
        "requirement": (
            "Covered providers of generative AI systems (>1M monthly users, "
            "producing audio/visual content) must embed latent disclosures "
            "(provenance metadata) in AI-generated content, offer a free AI "
            "detection tool, and provide a manifest disclosure option."
        ),
        "evidence_prompt": (
            "State monthly user counts for any genAI audio/visual feature and "
            "the provenance/watermarking approach (e.g., C2PA)."
        ),
    },
    # ---------------- Utah AI Policy Act ------------------------------------
    {
        "id": "UT-AIPA-01",
        "jurisdiction": "Utah",
        "law": "Utah Artificial Intelligence Policy Act",
        "effective": "in force",
        "severity": "medium",
        "requirement": (
            "Providers of services in regulated occupations (e.g., health, "
            "financial, legal advice) must clearly and conspicuously disclose "
            "genAI interaction when asked; other businesses must disclose when "
            "asked if interacting with genAI. Deception liability under existing "
            "consumer-protection law."
        ),
        "evidence_prompt": (
            "Confirm the product discloses genAI interactions on request and, if "
            "in a regulated occupation, proactively."
        ),
    },
    # ---------------- NYC Local Law 144 -------------------------------------
    {
        "id": "NYC-LL144-01",
        "jurisdiction": "New York City",
        "law": "NYC Local Law 144",
        "effective": "in force",
        "severity": "high",
        "requirement": (
            "Automated employment decision tools (AEDT) used to substantially "
            "assist hiring/promotion of NYC candidates require an annual "
            "independent bias audit published before use, plus candidate notice "
            "10 business days before use."
        ),
        "evidence_prompt": (
            "State whether any AI feature screens or ranks job candidates; if "
            "yes, provide the bias-audit summary URL and date."
        ),
    },
    # ---------------- Illinois AIVIA / HB 3773 ------------------------------
    {
        "id": "IL-AI-01",
        "jurisdiction": "Illinois",
        "law": "AI Video Interview Act / HB 3773 (IHRA amendment)",
        "effective": "2026-01-01",
        "severity": "medium",
        "requirement": (
            "Employers using AI analysis of video interviews must notify and "
            "obtain consent, explain how the AI works, and limit sharing. "
            "HB 3773 bars using AI in ways that have a discriminatory effect in "
            "employment decisions and requires notice of AI use in employment "
            "decisions."
        ),
        "evidence_prompt": (
            "Describe any AI-in-hiring usage affecting Illinois candidates and "
            "the notice/consent flow."
        ),
    },
    # ---------------- Federal layer -----------------------------------------
    {
        "id": "FED-EO14365-01",
        "jurisdiction": "Federal",
        "law": "EO 14365 + National Policy Framework (Dec 11 2025 / Mar 20 2026)",
        "effective": "policy",
        "severity": "info",
        "requirement": (
            "STATUS CHECK: the Dec 2025 EO and the Mar 2026 Framework seek "
            "federal preemption of 'unduly burdensome' state AI laws via an AI "
            "Litigation Task Force, funding conditions, and an FCC disclosure "
            "standard. They are NOT binding law on private companies; state laws "
            "remain in effect unless Congress acts or courts intervene. Track "
            "this — do not treat it as a compliance holiday."
        ),
        "evidence_prompt": (
            "Confirm a named owner monitors federal preemption developments "
            "quarterly."
        ),
    },
    {
        "id": "FED-FTC-01",
        "jurisdiction": "Federal",
        "law": "FTC Act §5 (unfair/deceptive practices)",
        "effective": "in force",
        "severity": "high",
        "requirement": (
            "AI capability claims must be truthful and substantiated; deceptive "
            "AI practices (fake reviews, impersonation, undisclosed AI agents in "
            "commerce) are actionable. The FTC's 2024 Operation AI Comply "
            "signaled active enforcement."
        ),
        "evidence_prompt": (
            "List all public AI capability claims and their substantiation."
        ),
    },
    {
        "id": "FED-TIDA-01",
        "jurisdiction": "Federal",
        "law": "TAKE IT DOWN Act (May 2025)",
        "effective": "in force (platform duty 2026-05)",
        "severity": "high",
        "requirement": (
            "Covered platforms must operate a notice-and-removal process for "
            "nonconsensual intimate imagery, including AI-generated deepfakes, "
            "removing reported content within 48 hours. Criminalizes publication "
            "of such imagery."
        ),
        "evidence_prompt": (
            "If the product hosts user-generated content, describe the NCII "
            "takedown flow and 48-hour SLA; else mark N/A."
        ),
    },
    # ---------------- Voluntary baseline ------------------------------------
    {
        "id": "NIST-RMF-01",
        "jurisdiction": "Federal (voluntary)",
        "law": "NIST AI Risk Management Framework 1.0",
        "effective": "voluntary",
        "severity": "medium",
        "requirement": (
            "Adopt GOVERN/MAP/MEASURE/MANAGE practices: documented AI risk "
            "ownership, system inventory, measured evaluation results, and "
            "incident response. SB 53 and several state frameworks treat NIST "
            "AI RMF or ISO/IEC 42001 alignment as the reference standard."
        ),
        "evidence_prompt": (
            "Provide the AI system inventory and the named risk owner."
        ),
    },
]
