#!/usr/bin/env python3
"""
Eng Brand Machine 🚀
Aggregates top engineering trends + generates Miro content recommendations.
Hackathon POC - 2026
"""

import requests
import feedparser
from datetime import datetime
from collections import defaultdict
import html as html_lib

# ─── CONFIG ────────────────────────────────────────────────────────────────────

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL        = "https://hacker-news.firebaseio.com/v0/item/{}.json"
DEVTO_API_URL      = "https://dev.to/api/articles"

RSS_FEEDS = [
    # Engineering blogs
    ("Stack Overflow Blog",   "https://stackoverflow.blog/feed/"),
    ("GitHub Blog",           "https://github.blog/feed/"),
    ("Cloudflare Blog",       "https://blog.cloudflare.com/rss/"),
    ("Netflix Tech Blog",     "https://netflixtechblog.com/feed"),
    ("Engineering at Meta",   "https://engineering.fb.com/feed/"),
    ("Martin Fowler",         "https://martinfowler.com/feed.atom"),
    ("ByteByteGo",            "https://blog.bytebytego.com/feed"),
    # Tech news
    ("InfoQ",                 "https://feed.infoq.com/"),
    ("The New Stack",         "https://thenewstack.io/feed/"),
    ("DZone",                 "https://feeds.dzone.com/home"),
    ("Smashing Magazine",     "https://www.smashingmagazine.com/feed/"),
    # Newsletters (Cooperpress)
    ("JavaScript Weekly",     "https://javascriptweekly.com/rss/"),
    ("Node Weekly",           "https://nodeweekly.com/rss/"),
    ("Frontend Focus",        "https://frontendfoc.us/rss/"),
    ("DB Weekly",             "https://dbweekly.com/rss/"),
    ("Golang Weekly",         "https://golangweekly.com/rss/"),
    # Community
    ("Lobste.rs",             "https://lobste.rs/rss"),
    # Design/frontend
    ("CSS-Tricks",            "https://css-tricks.com/feed/"),
]

# Reddit subreddits — fetched via JSON API (no auth needed, just User-Agent)
SUBREDDITS = [
    ("r/programming",          "programming"),
    ("r/MachineLearning",      "MachineLearning"),
    ("r/webdev",               "webdev"),
    ("r/devops",               "devops"),
    ("r/netsec",               "netsec"),
    ("r/javascript",           "javascript"),
    ("r/Python",               "Python"),
    ("r/rust",                 "rust"),
    ("r/golang",               "golang"),
    ("r/kubernetes",           "kubernetes"),
    ("r/aws",                  "aws"),
    ("r/softwarearchitecture", "softwarearchitecture"),
    ("r/ExperiencedDevs",      "ExperiencedDevs"),
    ("r/LocalLLaMA",           "LocalLLaMA"),
    ("r/datascience",          "datascience"),
    ("r/reactjs",              "reactjs"),
    ("r/frontend",             "frontend"),
    ("r/sysadmin",             "sysadmin"),
]

REDDIT_HEADERS = {"User-Agent": "EngBrandMachine/1.0 (hackathon project)"}

TOPIC_KEYWORDS = {
    "🤖 AI / ML":        ["ai", "machine learning", "llm", "gpt", "neural", "ml", "deep learning",
                           "openai", "claude", "gemini", "model", "transformer", "rag", "vector",
                           "embedding", "agent", "copilot", "diffusion", "inference", "fine-tun"],
    "☁️ Cloud / Infra":  ["cloud", "aws", "azure", "gcp", "kubernetes", "k8s", "serverless",
                           "lambda", "container", "docker", "terraform", "infra", "platform"],
    "🔐 Security":       ["security", "vulnerability", "exploit", "cve", "auth", "zero-day",
                           "breach", "encryption", "firewall", "hack", "phishing", "malware", "zero trust"],
    "⚡ Performance":    ["performance", "latency", "throughput", "optimization", "benchmark",
                           "profiling", "cache", "fast", "speed", "scalab"],
    "🦀 Languages":      ["rust", "go", "golang", "python", "javascript", "typescript", "java",
                           "swift", "kotlin", "wasm", "webassembly", "zig", "elixir", "ruby"],
    "🛠️ DevOps / SRE":  ["devops", "ci/cd", "cicd", "pipeline", "deployment", "gitops",
                           "monitoring", "observability", "logging", "sre", "platform engineer"],
    "🗄️ Databases":      ["database", "postgres", "mysql", "mongodb", "redis", "sql", "nosql",
                           "vector db", "sqlite", "elasticsearch", "kafka", "streaming", "graph db"],
    "🌐 Web / Frontend": ["react", "vue", "angular", "nextjs", "svelte", "css", "frontend",
                           "browser", "web", "html", "graphql", "rest", "http", "wasm"],
    "📱 Mobile":         ["ios", "android", "mobile", "swift", "flutter", "react native"],
    "🏗️ Architecture":   ["architecture", "microservices", "design pattern", "ddd", "event",
                           "distributed", "system design", "monolith", "refactor", "domain"],
    "🧪 Testing / QA":   ["test", "testing", "qa", "unit test", "e2e", "coverage", "playwright",
                           "cypress", "jest", "quality"],
    "🎨 Dev Experience": ["dx", "developer experience", "tooling", "ide", "vscode", "editor",
                           "productivity", "workflow", "developer tool"],
}

# ─── MIRO RECOMMENDATION TEMPLATES ────────────────────────────────────────────
# Each template maps a topic to a Miro content idea.
# We'll pick the best ones based on what's actually trending.

MIRO_CONTENT_TEMPLATES = {
    "🤖 AI / ML": [
        {
            "title": "How to Map Your AI Agent Architecture in Miro",
            "description": "A step-by-step guide showing engineering teams how to visualize LLM pipelines, RAG architectures, and multi-agent systems on a Miro board — making complex AI stacks legible to every stakeholder.",
            "demo": "Live Miro board with a RAG pipeline diagram: data ingestion → chunking → vector DB → retriever → LLM → output. Clickable nodes link to real code.",
            "format": "Blog Post + Free Template",
            "cta": "Download the AI Architecture Template →",
            "tags": ["ai", "llm", "rag", "agent-architecture", "miro-templates", "machine-learning"],
            "seo_description": "Map your RAG pipeline and multi-agent AI architecture in Miro — a step-by-step guide for engineering teams building LLM systems.",
            "read_time": "6 min read",
            "hero_prompt": "A glowing RAG pipeline architecture diagram on a dark background, luminous arrows flowing from document corpus through vector database to large language model, isometric tech illustration, purple and cyan color palette, ultra-detailed",
            "body": """
<p>Your AI architecture document is already out of date. The moment you finished that Confluence page describing your RAG pipeline, a teammate added a re-ranking step, swapped the vector database, and introduced a second agent loop. Keeping everyone — product, design, leadership — aligned on what your AI system <em>actually</em> does has become a full-time job that nobody signed up for.</p>

<h2>Why the Existing Approach Fails</h2>
<p>Most teams default to one of two paths: dense technical diagrams buried in Notion that only the original author can decode, or live whiteboard sessions that evaporate the moment the meeting ends. Neither scales. With LLM architectures evolving weekly — new models, new orchestration frameworks, new retrieval strategies — your diagrams need to be living documents, not frozen snapshots.</p>
<p>The real problem isn't complexity. It's that your documentation toolchain was designed for static content in a world that demands dynamic collaboration.</p>

<h2>The Miro Framework: Map Your AI Stack in 5 Steps</h2>
<ol>
  <li><strong>Start with the data journey.</strong> Draw every stage from raw data ingestion to output: source → chunking → embedding → vector store → retriever → LLM → response. Don't skip preprocessing — it's where most production bugs hide.</li>
  <li><strong>Layer in your infrastructure.</strong> Add swim lanes for model serving, monitoring, and feedback loops. Use a consistent color code: green for stable/live, yellow for in-flight, red for known issues or technical debt.</li>
  <li><strong>Link to code, not just diagrams.</strong> Every node in Miro holds a hyperlink. Attach the GitHub file, PR, or experiment run directly so engineers jump from diagram to implementation in one click.</li>
  <li><strong>Annotate decisions, not just mechanics.</strong> Use sticky notes for "why we chose this" — model selection rationale, chunking strategy trade-offs, latency budgets. Your future self will thank you.</li>
  <li><strong>Run async design reviews.</strong> Share the board, enable comments, and let people question and suggest changes without scheduling yet another meeting.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "A multi-agent system diagram showing three specialized AI agents (retriever, reasoner, synthesizer) exchanging messages via a shared memory store, dark background with luminous connection arrows, isometric perspective, cyan and violet color scheme"
</div>

<h2>Practical Workflow: Keeping the Board Alive</h2>
<p>Assign one engineer per sprint as the "architecture steward." Their job: 15 minutes before the sprint retro, update the Miro board with any changes. Use Miro's comment notifications to automatically loop in stakeholders. For multi-agent systems, create a separate frame per agent with clear input/output contracts visible at a glance.</p>
<p>Teams that implement this consistently report two outcomes: product managers stop asking "how does the AI actually work?" in stand-up, and new engineers onboard to the AI stack in days, not weeks. When something breaks at 2 AM, your on-call engineer can navigate the architecture map directly to the failing component instead of grep-ing through Slack history.</p>
<p>The best AI systems aren't just well-built — they're well-explained. <em>Download the free Miro AI Architecture Template and have your RAG pipeline mapped in under an hour.</em></p>
""",
        },
        {
            "title": "AI System Design Reviews, Async — A Miro Playbook",
            "description": "How ML teams at fast-moving companies run async architecture reviews using Miro: annotating architecture diagrams, leaving context-rich comments, and shipping decisions 2x faster.",
            "demo": "Before/after: messy Notion doc vs a Miro board with swimlanes for model training, serving, and monitoring pipelines.",
            "format": "Case Study + Video Walkthrough",
            "cta": "Watch the 3-min demo →",
            "tags": ["ai", "ml", "async", "system-design", "miro-templates", "machine-learning"],
            "seo_description": "Run async AI architecture reviews in Miro — how ML teams annotate diagrams, resolve decisions faster, and ship with shared understanding.",
            "read_time": "5 min read",
            "hero_prompt": "ML system architecture with training pipeline, model serving layer, and monitoring dashboard as glowing swim lanes on dark background, async comment bubbles floating above components, collaborative visualization, indigo and teal palette",
            "body": """
<p>ML teams move fast and break things — but when your model serving pipeline breaks at scale, "move fast" becomes "spend three days untangling who made what decision and why." Async design reviews in Miro change this. Instead of a 90-minute all-hands architecture call, you share a board, give people 48 hours to annotate, and walk into a 30-minute sync already 80% aligned.</p>

<h2>Why Synchronous ML Design Reviews Don't Work</h2>
<p>ML system design involves too many specializations for synchronous review to be efficient. Your data engineers care about the ingestion pipeline. Your ML engineers care about training infrastructure. Your platform engineers care about serving latency. Your product team cares about what any of this means for the feature they're shipping next week. Getting all of these stakeholders in a room at the same time, for long enough to reach meaningful decisions, is a coordination tax that compounds sprint over sprint.</p>
<p>The alternative — email threads with architecture diagrams attached — produces 47-message threads where the final decision is buried in a reply-all that half the team missed.</p>

<h2>The Miro Async Review Framework</h2>
<ol>
  <li><strong>Publish the board 48 hours before any sync.</strong> Share a Miro board with the architecture diagram and a structured comment guide: "Please annotate with your concerns, questions, and +1s."</li>
  <li><strong>Use swim lanes for each stakeholder perspective.</strong> Data engineering, ML research, platform, and product each get a lane. Reviewers add their annotations to their lane — no cross-talk, clear ownership.</li>
  <li><strong>Color-code by decision type.</strong> Green sticky = decision made, Yellow = open question, Red = blocker, Blue = nice-to-have future consideration.</li>
  <li><strong>The sync is for red items only.</strong> Everything green and blue is resolved async. The 30-minute sync is laser-focused on blockers. Teams report shipping decisions 2x faster with this model.</li>
  <li><strong>Archive every review.</strong> Create a new Miro frame for each review cycle. Your architecture history is now searchable, visual, and connected to the decisions that shaped it.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "Before-and-after comparison: left side shows a cluttered Notion document with nested bullets, right side shows a clean Miro board with swim lanes, color-coded sticky notes, and clear decision indicators, split-screen visualization"
</div>

<h2>Team Adoption: Starting With One Review</h2>
<p>Don't try to transform your entire review process overnight. Pick one upcoming architecture decision — the next model upgrade, a new data pipeline, a serving layer change — and run it async in Miro. Invite the five people who need to sign off. Give them 48 hours. See how the sync goes. The first time you finish a design review in 25 minutes instead of 90, the team will ask why you ever did it any other way.</p>
<p>Async-first ML teams ship better systems because the review process doesn't bottleneck on calendar availability. <em>Watch the 3-minute demo and run your first async architecture review this sprint.</em></p>
""",
        },
    ],
    "☁️ Cloud / Infra": [
        {
            "title": "Kubernetes Architecture Diagrams That Actually Stay Up to Date",
            "description": "Most K8s architecture docs go stale in days. This post shows how platform teams use Miro's live embed + diagram features to keep cluster topology, service maps, and resource flows always current.",
            "demo": "An interactive Miro board with K8s namespace layout, pod communication, and HPA configs. Arrows update with sticky note annotations from the on-call engineer.",
            "format": "Tutorial + Template",
            "cta": "Grab the K8s Miro Template →",
            "tags": ["kubernetes", "cloud", "infrastructure", "k8s", "miro-templates", "platform-engineering"],
            "seo_description": "Keep Kubernetes architecture diagrams accurate and up-to-date with Miro — live annotations, team collaboration, and always-current cluster topology.",
            "read_time": "5 min read",
            "hero_prompt": "Kubernetes cluster architecture diagram with glowing nodes representing pods, services, ingress, and namespaces, floating in a dark space environment, connected by illuminated network paths, technical illustration, teal and blue palette",
            "body": """
<p>Kubernetes documentation has a half-life measured in sprint cycles. You update the architecture diagram, merge the PR, and by the time the next on-call rotation starts, three new services have been added, a namespace was restructured, and the HPA configs everyone agreed on last quarter have been quietly changed. The diagram in your wiki is now a liability, not an asset.</p>

<h2>Why Static K8s Docs Always Go Stale</h2>
<p>The root cause is a mismatch between how Kubernetes moves and how documentation tools work. Wikis and Confluence are document stores — they're great for stable reference material, terrible for representing infrastructure that changes daily. When the cost of updating a diagram is high (find the tool, open the file, re-export, re-upload, update the link), people stop updating it. That's not a discipline problem; it's a tooling problem.</p>
<p>Additionally, K8s architecture involves multiple stakeholder perspectives simultaneously: cluster topology matters to SREs, service communication maps matter to backend engineers, and resource quota summaries matter to platform teams. No single static diagram serves all three audiences.</p>

<h2>The Miro Framework: Living K8s Architecture in 4 Layers</h2>
<ol>
  <li><strong>Layer 1 — Cluster topology.</strong> One frame per cluster (production, staging, dev). Show namespaces as swim lanes, node groups as colored regions. Sticky notes carry current node counts and instance types.</li>
  <li><strong>Layer 2 — Service communication map.</strong> Draw your services, their ports, and the protocols between them. Color edges by traffic type: internal gRPC, external HTTP, async event streams. Link each service to its Helm chart.</li>
  <li><strong>Layer 3 — HPA and resource configs.</strong> A simple table frame per namespace: service name, CPU request/limit, memory request/limit, current HPA min/max. Update it in the Miro board, then copy to your YAML. One source of truth.</li>
  <li><strong>Layer 4 — On-call annotations.</strong> During incidents, on-call engineers drop timestamped sticky notes directly on the affected component. After the post-mortem, those notes become permanent annotations — institutional memory baked into the diagram.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "Kubernetes namespace swim lane layout showing pods, services, ingress controllers and config maps as glowing icons, dark terminal background with teal highlights, real-time annotation sticky notes overlaid on affected components"
</div>

<h2>Team Adoption: The Friday Update Ritual</h2>
<p>The platform teams who stick with this approach all share one habit: a recurring 15-minute calendar block every Friday afternoon titled "Update the K8s board." It's not a meeting — it's a solo ritual. The engineer who touched the cluster that week spends 15 minutes reflecting changes in Miro. After three sprints, the board becomes the team's most-visited resource, displacing the wiki entirely.</p>
<p>Pair this with a Miro board link in your runbook template, and every incident starts with a visual overview of the affected system — not a frantic search for documentation that may or may not be accurate.</p>
<p>Platform teams spend too much time answering "how does our infrastructure work?" questions. <em>Grab the Kubernetes Architecture Template and let the diagram answer for you.</em></p>
""",
        },
    ],
    "🛠️ DevOps / SRE": [
        {
            "title": "Visualize Your CI/CD Pipeline in Miro — A Template for Every Team",
            "description": "From GitHub Actions to complex multi-repo pipelines: how DevOps and platform engineers use Miro to document, onboard, and improve their delivery workflows.",
            "demo": "Miro board: trigger → build → test → staging deploy → canary → prod. Each stage has linked runbooks and post-mortem notes embedded inline.",
            "format": "Free Template Pack (5 pipelines)",
            "cta": "Download the CI/CD Template Pack →",
            "tags": ["devops", "cicd", "pipelines", "sre", "miro-templates", "platform-engineering"],
            "seo_description": "Visualize your CI/CD pipeline in Miro — from GitHub Actions to multi-repo deployments. A template guide for DevOps and platform engineers.",
            "read_time": "7 min read",
            "hero_prompt": "CI/CD pipeline flowchart visualization on a dark terminal-inspired background, stages glowing in sequence from code commit through build test deploy to production, green checkmarks and orange warning indicators, cyberpunk aesthetic",
            "body": """
<p>Your CI/CD pipeline is your team's most critical shared system — and the one with the least documentation. Ask three engineers to describe the full delivery workflow and you'll get three different answers, each missing pieces the others take for granted. For new teammates, understanding the pipeline means weeks of tribal knowledge accumulation, not hours of reading.</p>

<h2>Why Pipeline Docs Are Always Wrong</h2>
<p>Most CI/CD documentation lives in two places: README files that describe the pipeline as it was designed six months ago, and the YAML config itself — which is accurate but impenetrable to anyone who doesn't already know what they're looking at. The missing layer is a visual representation that bridges intention and implementation: "here's what we're trying to do and why each stage exists."</p>
<p>The consequences of bad pipeline documentation surface predictably: failed deployments that take hours to debug because nobody knows which stage introduced the regression, onboarding that drags for weeks, and post-mortems that reveal the team had conflicting mental models of how their own deployment works.</p>

<h2>The Miro Framework: Pipeline Visualization in 5 Stages</h2>
<ol>
  <li><strong>Map the happy path first.</strong> Draw the end-to-end flow: trigger (commit/PR/tag) → build → test → artifact publish → staging deploy → smoke test → canary → full production. Resist adding exceptions until the main path is clear.</li>
  <li><strong>Add gate logic.</strong> Mark every decision point: what does a failed test gate do? What triggers a rollback? Use diamond shapes for gates and color them by severity (green = auto-proceed, yellow = manual approval, red = auto-block).</li>
  <li><strong>Embed runbooks inline.</strong> Each pipeline stage gets a linked Miro card with: what it does, what can go wrong, and the runbook link for when it does. On-call engineers thank you at 3 AM.</li>
  <li><strong>Show the multi-repo picture.</strong> For complex systems with multiple repos or services, add a frame per service and show how they chain together with dependency arrows. Critical path is immediately visible.</li>
  <li><strong>Annotate your environment strategy.</strong> Add a swim lane per environment (dev, staging, canary, prod) and show which pipeline stages touch which environment. Compliance reviewers love this view.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "CI/CD pipeline with glowing stage nodes: code commit, automated tests, Docker build, staging deployment, canary release, production — connected by animated arrows on dark background, green checkmarks and red failure states visible, DevOps visualization"
</div>

<h2>Team Adoption: Making It Part of the Post-Mortem</h2>
<p>The most effective teams integrate pipeline board updates into their post-mortem process. Every incident that touches the delivery pipeline ends with a board annotation: what stage failed, what the fix was, and what guardrail was added. Over six months, the board becomes an institutional memory of every hard lesson the team has learned — visual, searchable, and immediately actionable for the next on-call engineer.</p>
<p>Schedule a 30-minute "pipeline review" in your quarterly planning cycle. Pull up the Miro board, walk through each stage, and ask: "Is this still accurate? Is this still the right approach?" It's the most valuable 30 minutes of the quarter for your platform team.</p>
<p>Delivery pipelines that are understood are pipelines that get improved. <em>Download the CI/CD Template Pack and give your whole team a shared mental model of how your software ships.</em></p>
""",
        },
    ],
    "🔐 Security": [
        {
            "title": "Collaborative Threat Modeling on Miro: A Developer's Guide",
            "description": "Security doesn't have to happen in silos. This guide shows dev teams how to run STRIDE threat modeling sessions in Miro — mapping trust boundaries, attack surfaces, and mitigations together in real time.",
            "demo": "Live threat model for a typical SaaS app: user → API gateway → auth service → DB. Each node color-coded by risk level, with mitigation sticky notes.",
            "format": "Workshop Guide + Template",
            "cta": "Run your first threat model session →",
            "tags": ["security", "threat-modeling", "stride", "devsecops", "miro-templates", "appsec"],
            "seo_description": "Run collaborative STRIDE threat modeling sessions in Miro — map attack surfaces, trust boundaries, and mitigations with your whole engineering team.",
            "read_time": "8 min read",
            "hero_prompt": "STRIDE threat model diagram on a dark background, nodes representing API gateway, auth service, and database with red threat arrows and green mitigation shields overlaid, security visualization, dark mode, red and green palette",
            "body": """
<p>Security reviews are too often a checkbox at the end of a project — a rushed 30-minute meeting where a security engineer skims an architecture doc they've never seen before and signs off under deadline pressure. The result: real threats get missed, mitigations are bolted on as afterthoughts, and the security team gets blamed when something breaks in production. The problem isn't lack of expertise. It's lack of shared context.</p>

<h2>Why Siloed Security Reviews Fail</h2>
<p>Traditional threat modeling — STRIDE, PASTA, attack trees — is powerful on paper and painful in practice. The tools are often heavyweight (dedicated software with steep learning curves), the output is hard to share (dense Word documents nobody reads), and the process is designed for security specialists, not the development teams who need to act on the findings.</p>
<p>When security happens in a silo, developers see it as a blocker, not a collaborator. Threat models sit in a security team's shared drive, disconnected from the architecture diagrams developers actually use. Mitigations get forgotten. The same vulnerabilities get introduced sprint after sprint.</p>

<h2>The Miro STRIDE Framework: 6 Steps to Collaborative Threat Modeling</h2>
<ol>
  <li><strong>Start with your data flow diagram.</strong> Draw every component, data store, external actor, and trust boundary on a Miro board. This is the shared foundation everyone in the room works from.</li>
  <li><strong>Apply STRIDE categories.</strong> For each component and data flow, add color-coded sticky notes: Spoofing (red), Tampering (orange), Repudiation (yellow), Information Disclosure (purple), Denial of Service (blue), Elevation of Privilege (pink).</li>
  <li><strong>Run the async review phase.</strong> Share the board 48 hours before the session. Let engineers, product managers, and the security team add their own threat notes asynchronously. You walk into the meeting with richer input than any single expert could generate alone.</li>
  <li><strong>Score and prioritize threats.</strong> In the live session, use Miro voting to score threats by likelihood × impact. The board updates in real time, giving you a prioritized risk register by the end of the meeting.</li>
  <li><strong>Map mitigations to components.</strong> For each high-priority threat, add a green sticky with the mitigation strategy and the engineering owner. This becomes your security backlog.</li>
  <li><strong>Link to code and tickets.</strong> Connect each mitigation sticky to the relevant Jira ticket or GitHub issue. The threat model stays connected to actual remediation work.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "STRIDE threat model showing SaaS components — API gateway, auth service, user database — with colored threat annotation sticky notes (red, orange, yellow, purple, blue, pink) and green mitigation shields, dark security dashboard aesthetic"
</div>

<h2>Team Adoption: Threat Modeling as a Sprint Ritual</h2>
<p>The teams that make threat modeling stick don't treat it as a project milestone — they treat it as a recurring sprint ritual. Every time a new feature introduces a data flow, API, or third-party integration, a 45-minute threat modeling session is automatically scheduled. The Miro board template is already there; you just add a new frame for the new feature.</p>
<p>After three months, something shifts in the team culture: developers start thinking about trust boundaries during design, not after implementation. Security stops being a gate and becomes a design input. And when an auditor asks "how do you manage security risk?", you open the Miro board instead of scrambling for documentation.</p>
<p>Security built collaboratively is security that actually holds. <em>Run your first STRIDE threat modeling session in Miro — the template takes 5 minutes to set up.</em></p>
""",
        },
    ],
    "🏗️ Architecture": [
        {
            "title": "System Design on a Whiteboard, Scaled to Your Whole Org",
            "description": "How engineering orgs use Miro to replace one-off whiteboard sessions with living architecture docs that the whole team can read, comment on, and evolve over time.",
            "demo": "A C4 model (Context → Container → Component) built in Miro, with drill-down navigation between levels and inline ADR (Architecture Decision Record) stickies.",
            "format": "Deep Dive Post + C4 Template",
            "cta": "Explore the C4 Model Template →",
            "tags": ["architecture", "c4-model", "system-design", "adr", "miro-templates", "engineering"],
            "seo_description": "Build a living C4 architecture model in Miro with embedded Architecture Decision Records — system design docs your whole org can read and evolve.",
            "read_time": "7 min read",
            "hero_prompt": "Multi-level C4 architecture diagram zooming from system context to containers to components, nested glowing boxes connected with arrows, dark background with glowing borders, architectural blueprint aesthetic, indigo and white palette",
            "body": """
<p>Your system architecture exists in three places simultaneously: in the heads of your senior engineers, in the whiteboard photos from last quarter's design session, and in the code itself — none of which a new engineer, product manager, or executive can actually use to understand how your system works. The gap between "we have architecture docs" and "anyone can understand our architecture" is where most engineering organizations permanently live.</p>

<h2>Why One-Off Whiteboards Don't Scale</h2>
<p>Whiteboard sessions are great for reaching alignment in the moment. They're terrible for preserving that alignment over time. The photo fades from everyone's Slack history. The decisions get lost in meeting notes nobody reads. Six months later, a new engineer makes the same architectural mistake you already solved, because the reasoning behind the current design was never captured in a place they could find it.</p>
<p>Architecture Decision Records (ADRs) solve the "why" problem in text, but they create a new problem: the context that makes an ADR meaningful — the diagram it references, the alternative it rejected — lives in a completely different system. The connection breaks as soon as someone changes the architecture.</p>

<h2>The Miro C4 Framework: Four Levels of Clarity</h2>
<ol>
  <li><strong>Level 1 — System Context.</strong> One frame showing your system as a single box, surrounded by the people and external systems that interact with it. Audience: everyone, including non-technical stakeholders. Answer: "What does this system do and who uses it?"</li>
  <li><strong>Level 2 — Container Diagram.</strong> Zoom in to show the major deployable units: web app, API, database, background workers, external services. Audience: developers and architects. Answer: "How is the system divided and how do the parts communicate?"</li>
  <li><strong>Level 3 — Component Diagram.</strong> For each container, show its internal components and their responsibilities. Audience: the engineers building that container. Answer: "How is this container structured internally?"</li>
  <li><strong>ADR Stickies.</strong> At every level, pin Architecture Decision Record stickies to the relevant component: "Why we chose PostgreSQL over MongoDB," "Why we went with a monolith first," "Why we're using event sourcing here." Decisions stay permanently connected to their context.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "C4 architecture model showing three nested zoom levels — system context, containers, and components — as glowing rectangular frames on dark background, drill-down navigation arrows between levels, architectural blueprint aesthetic with indigo highlights"
</div>

<h2>Team Adoption: Architecture as a Living Document</h2>
<p>The most successful implementations treat the Miro C4 board as a first-class engineering artifact — not documentation, but design infrastructure. The rule is simple: if you're proposing an architectural change, you update the board before the PR is merged. The PR description includes a link to the Miro board showing the before and after state.</p>
<p>This creates a virtuous cycle: the board is always accurate because changes require it to be updated; the board is trusted because it's always accurate; engineers consult the board because they trust it. Within a quarter, your senior engineers stop being the single point of contact for "how does our system work?" questions.</p>
<p>Great architecture isn't just built — it's explained. <em>Start with the C4 Model Template and give your organization the architectural clarity it has been missing.</em></p>
""",
        },
    ],
    "🌐 Web / Frontend": [
        {
            "title": "Frontend Architecture Maps: How to Onboard Engineers in Half the Time",
            "description": "Miro as the missing layer between your code and your docs — showing how frontend teams map component hierarchies, data flow, and routing so new engineers hit the ground running.",
            "demo": "React app architecture: routing tree, state management layers (Zustand/Redux), API boundaries — all in one scrollable Miro board with code links.",
            "format": "Blog Post + Template",
            "cta": "See the Frontend Architecture Template →",
            "tags": ["frontend", "react", "architecture", "onboarding", "miro-templates", "web-development"],
            "seo_description": "Cut frontend onboarding time in half with a Miro architecture map — component hierarchies, data flow, and routing all in one collaborative board.",
            "read_time": "6 min read",
            "hero_prompt": "React frontend architecture map showing component hierarchy tree, state management layers, and API boundaries as glowing connected nodes on dark background, colorful lines connecting components, modern web development visualization",
            "body": """
<p>The first week for a new frontend engineer follows a predictable arc: clone the repo, spend two hours getting the dev environment running, then spend two more hours trying to understand why there are four different state management patterns in the same codebase, who owns which components, and where the API calls actually live. By day three, they're productive. By week two, they're slowing down senior engineers with questions that a good architecture map would have answered immediately.</p>

<h2>Why Frontend Architecture Is Hardest to Document</h2>
<p>Backend systems have decades of tooling for architecture visualization — ERDs, service maps, flow diagrams. Frontend architecture has almost none, despite being just as complex. A modern React application involves routing trees, state management layers, component hierarchies, API boundaries, and build pipeline configuration — and the relationships between all of these are implicit in the code, not visible anywhere else.</p>
<p>The result: frontend architecture lives entirely in senior engineers' heads. When they leave, the knowledge leaves with them. When you hire, onboarding takes weeks that should take days. And when you need a significant refactor, you're flying blind — unable to see the full blast radius before making the change.</p>

<h2>The Miro Framework: Frontend Architecture in 4 Views</h2>
<ol>
  <li><strong>The routing tree.</strong> Draw every route in your application as a tree. Mark which routes are public vs. authenticated, which are lazy-loaded, and which share layouts. New engineers can see the entire navigation structure at a glance.</li>
  <li><strong>State management topology.</strong> Map your state: global store (Zustand, Redux, Jotai), server state (React Query, SWR), local component state, and URL state. Draw which components read from and write to each state source. This is the view that prevents the "why is this component re-rendering?" debug session.</li>
  <li><strong>API boundaries and data flow.</strong> Show which components fetch data, which transform it, and which display it. Draw the API endpoints they call. This view is gold during onboarding and indispensable during debugging.</li>
  <li><strong>Component ownership map.</strong> Organize components by team or feature area. Mark which are shared design system components, which are feature-specific, and which are currently being refactored. Prevents accidental coupling between feature teams.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "React application architecture map with component hierarchy tree on the left, state management topology in the center, and API boundary diagram on the right, connected by glowing data flow arrows, dark mode visualization, blue and purple palette"
</div>

<h2>Team Adoption: The Living Frontend Docs Habit</h2>
<p>Frontend architecture boards work best when updated continuously rather than in big batches. The habit to build: any PR that adds a new route, introduces a new state pattern, or changes a major component boundary includes a Miro board update in the PR checklist. It takes five minutes per PR and means the board is always accurate.</p>
<p>Use the board in sprint planning to identify coupling risks before they become bugs. Use it in architecture reviews to give stakeholders a visual before committing to a refactor. And use it in onboarding — new frontend engineers report that a good architecture board cuts their ramp-up time in half.</p>
<p>Great frontend teams build great documentation habits. <em>Get the Frontend Architecture Template and give your next new hire the map they wish they had on day one.</em></p>
""",
        },
    ],
    "🗄️ Databases": [
        {
            "title": "Database Schema Design in Miro: From ERD to Production",
            "description": "How data teams and backend engineers use Miro to collaboratively design schemas, map data lineage, and communicate database decisions across product and infra — all before writing a single migration.",
            "demo": "An ERD for a multi-tenant SaaS built live in Miro, with sharding strategy annotated, and query performance notes per table.",
            "format": "Tutorial + ERD Template",
            "cta": "Download the Schema Design Template →",
            "tags": ["databases", "erd", "data-modeling", "postgres", "miro-templates", "backend"],
            "seo_description": "Design database schemas collaboratively in Miro — build ERDs, map data lineage, and communicate data decisions before writing a single migration.",
            "read_time": "6 min read",
            "hero_prompt": "Entity-relationship diagram (ERD) for a multi-tenant SaaS glowing on dark background, table boxes with columns connected by crow-foot notation arrows, data lineage flowing between tables and analytics pipelines, dark mode visualization, amber and teal",
            "body": """
<p>Database schema decisions are permanent in a way that most engineering choices aren't. You can refactor code, rewrite services, re-architect your backend — but a poorly designed schema that's been live in production for a year generates migration debt that follows a team for a decade. And yet, in most organizations, schema design happens in a developer's local environment, reviewed in a GitHub PR that nobody outside engineering can meaningfully comment on, and documented nowhere.</p>

<h2>Why Schema Design Happens Too Late</h2>
<p>The standard workflow — write the migration, open the PR, get it reviewed by one engineer who approves it in 10 minutes — treats schema design as an implementation detail rather than an architectural decision. Product managers, data analysts, and data engineers who will live with the schema for years have no input. The people who know the business domain best aren't in the room when the modeling decisions are made.</p>
<p>This creates predictable failure modes: schemas that don't support the query patterns that emerge six months later, normalization choices that make reporting queries impossibly slow, and multi-tenant data isolation decisions that weren't fully thought through until the first security audit.</p>

<h2>The Miro Framework: Collaborative Schema Design in 5 Steps</h2>
<ol>
  <li><strong>Start with an entity map, not a schema.</strong> Before opening your database client, draw the domain entities on a Miro board — just boxes and relationship lines. Invite product managers and data engineers to this view. They'll catch modeling mistakes before any SQL is written.</li>
  <li><strong>Layer in the ERD.</strong> Once entity relationships are agreed on, formalize them into an ERD with actual column names, types, and constraints. Use Miro's table shapes or the built-in ERD diagramming tool.</li>
  <li><strong>Annotate query patterns.</strong> For each major table, add sticky notes showing the top 3 queries that will run against it. This drives index design conversations before you're optimizing production queries at 2 AM.</li>
  <li><strong>Map data lineage.</strong> Draw arrows showing how data flows between tables, microservices, and data pipelines. Highlight tables read by analytics, those that feed event streams, and those written by external services.</li>
  <li><strong>Document sharding and tenancy strategy.</strong> For multi-tenant systems, add a frame showing your tenancy model — shared schema, separate schemas, or separate databases per tenant — with trade-offs visible to everyone.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "Database data lineage diagram showing tables flowing data into analytics pipelines and event streams, ERD overlay with crow-foot notation, dark background with glowing amber data flow paths and teal table borders, technical data engineering visualization"
</div>

<h2>Team Adoption: Schema Reviews Before Migrations</h2>
<p>The most impactful change a team can make: require a Miro board review before any significant schema migration is written. Post the board link in the design review channel, give it 48 hours for async comment, then spend 30 minutes in a synchronous review with the data engineer and product manager most affected by the change. The migrations that result from this process are dramatically better than those designed in isolation.</p>
<p>Teams that implement this consistently report a meaningful reduction in major schema revisions — not because they're doing less, but because they catch mistakes early, when they're cheap to fix.</p>
<p>Schema decisions made in public are schema decisions made well. <em>Download the Schema Design Template and start your next data model with the whole team in the room.</em></p>
""",
        },
    ],
    "🧪 Testing / QA": [
        {
            "title": "Test Coverage Maps: Visualize What You're Actually Testing",
            "description": "Beyond line coverage percentages — how engineering teams map their test pyramid, identify blind spots, and align QA strategy using Miro boards in sprint planning.",
            "demo": "A test pyramid in Miro: unit → integration → e2e, with color-coded coverage by feature area and links to failing test suites.",
            "format": "Blog Post + Workshop Template",
            "cta": "Map your test coverage in Miro →",
            "tags": ["testing", "qa", "test-pyramid", "coverage", "miro-templates", "quality-engineering"],
            "seo_description": "Visualize your test pyramid and identify coverage blind spots in Miro — map unit, integration, and e2e tests by feature area with your whole team.",
            "read_time": "5 min read",
            "hero_prompt": "Test pyramid visualization on dark background, three glowing tiers representing unit tests at base, integration tests in middle, and end-to-end tests at apex, color-coded coverage grid showing feature areas in green yellow and red, QA engineering illustration",
            "body": """
<p>Your team has 87% line coverage. The dashboard is green. Then a critical user flow breaks in production because nobody was testing the integration between the payment service and the notification system — a gap that would have been obvious on a test coverage map, but invisible in a coverage percentage. Line coverage metrics tell you what percentage of your code is executed during tests. They don't tell you whether you're testing the right things.</p>

<h2>Why Coverage Numbers Lie</h2>
<p>The coverage number is a proxy metric that the industry has elevated to a north star metric, often to its detriment. Teams optimize for the number — hitting 80%, then 90% — without asking whether the tests they're writing actually protect against the failures that matter. Unit tests on pure functions are cheap to write and inflate coverage metrics without adding much protection. Tests on complex integration paths are hard to write but prevent the failures that actually wake up on-call engineers.</p>
<p>The deeper problem: without a visual map, it's impossible to answer the question "what are we not testing?" You can see coverage per file, per function, per line — but you can't see which user journeys, which integration paths, or which risk areas have no test coverage at all.</p>

<h2>The Miro Framework: Building a Test Coverage Map</h2>
<ol>
  <li><strong>Draw the test pyramid.</strong> Three tiers: unit tests at the base (fast, isolated, many), integration tests in the middle (testing component interactions), end-to-end tests at the apex (complete user flows, fewer). This shared model aligns your whole team on testing philosophy.</li>
  <li><strong>Map coverage by feature area.</strong> Divide your application into feature areas (auth, payment flow, notifications, data export) and assign each a column. For each feature × test tier intersection, assess coverage: green (well-covered), yellow (partial), red (minimal or none).</li>
  <li><strong>Identify the critical paths.</strong> Mark the user journeys that, if broken, would cause the most user pain or business impact. These are your highest-priority coverage targets regardless of what the line coverage number says.</li>
  <li><strong>Add test suite health notes.</strong> For each area, sticky notes capture: flaky tests (name them!), tests that are slow, tests not updated since a major refactor. This is your technical debt backlog for the testing layer.</li>
  <li><strong>Link to failing tests.</strong> Connect red areas to CI dashboard links and open tickets. The map becomes an actionable backlog, not just a diagnostic.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "Test coverage grid visualization showing feature areas as columns and test pyramid tiers as rows, green cells for well-covered areas, yellow for partial, red for gaps, glowing on dark background, QA engineering dashboard aesthetic with clean typography"
</div>

<h2>Team Adoption: Coverage Review in Sprint Planning</h2>
<p>The most effective use of a test coverage map is in sprint planning. Before committing to new feature work, spend 10 minutes reviewing the map: "Are we adding tests for the new feature? What existing coverage gaps does this sprint create the opportunity to close?"</p>
<p>Pair the coverage map with a "testing debt" sprint story every three sprints — a dedicated allocation for closing the highest-priority coverage gaps. Teams that do this see fewer production incidents and faster debugging when incidents do happen, because the test suite reliably narrows the search space.</p>
<p>Testing strategy deserves the same architectural rigor as system design. <em>Map your test coverage in Miro and finally answer the question: what are we not testing?</em></p>
""",
        },
    ],
    "🎨 Dev Experience": [
        {
            "title": "Developer Onboarding Boards That Don't Suck",
            "description": "The best onboarding experience a new engineer can get: a Miro board that maps the entire system, annotated with 'start here' paths, gotchas, and links to code — built by the team, for the team.",
            "demo": "Day 1 onboarding board: team structure → codebase map → dev environment setup → first PR checklist → who to ask for what.",
            "format": "Template + Blog Post",
            "cta": "Get the Engineering Onboarding Template →",
            "tags": ["developer-experience", "onboarding", "dx", "documentation", "miro-templates", "engineering"],
            "seo_description": "Build developer onboarding boards in Miro that new engineers actually use — codebase maps, first-PR checklists, and who-to-ask guides all in one place.",
            "read_time": "5 min read",
            "hero_prompt": "Developer onboarding board showing team structure, codebase map, and first PR checklist as interconnected glowing nodes, warm amber paths guiding a new engineer through their first week on dark background, welcoming tech visualization",
            "body": """
<p>The first PR a new engineer merges should happen in their first week. In most organizations, it happens in their third. The gap isn't talent — it's friction. Friction from a dev environment setup that requires tribal knowledge to get working. Friction from a codebase with no map. Friction from not knowing which Slack channel to ask for help without feeling like you're bothering someone. Good onboarding eliminates friction. Most onboarding just documents it.</p>

<h2>Why Most Onboarding Documentation Doesn't Work</h2>
<p>Engineering onboarding docs share a universal failure mode: they're written by senior engineers who've forgotten what it's like to not know things, last updated during a sprint where someone had too much spare time, and structured around what the team thought was important rather than what a new person needs to know first.</p>
<p>The other failure mode is format. Long markdown docs in a wiki require a level of contextual understanding to parse that the new engineer doesn't yet have. "Set up your local environment by following CONTRIBUTING.md" is useless when you don't know what any of the tools mentioned are or why you need them.</p>

<h2>The Miro Framework: The Engineering Onboarding Board</h2>
<ol>
  <li><strong>The "Start Here" path.</strong> A visual, numbered trail through the board — like a guided tour — that explicitly sequences the information a new engineer needs. Start: team structure and who to ask for what. Then: codebase overview. Then: dev environment setup with screenshots. Then: first PR checklist.</li>
  <li><strong>The codebase map.</strong> A diagram showing the major repositories, their purposes, and how they relate. Link each box to the actual GitHub repo. Color codes: green = stable/mature, yellow = active development, red = known issues / scheduled for refactor. New engineers instantly know which areas to explore and which to approach with caution.</li>
  <li><strong>The "who to ask" guide.</strong> A Miro frame with team members, their areas of ownership, and their preferred contact method. Eliminates the anxiety of "am I asking the right person?" that slows down new engineers for their first month.</li>
  <li><strong>First PR checklist.</strong> A visual checklist of everything needed before opening a PR: linting, tests passing, docs updated, PR template filled out, code review assigned. Interactive checkboxes appreciated.</li>
  <li><strong>Gotchas and institutional knowledge.</strong> A frame just for "things we wish someone had told us" — the surprising behavior in the deployment pipeline, the Slack channel that sounds unrelated but is actually important, the testing shortcut that saves 20 minutes. Crowdsourced from the whole team.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "Developer onboarding journey map with numbered stages — team introduction, codebase tour, environment setup, first PR — connected by warm glowing trail on dark background, sticky notes with tips and gotchas attached to each stage, friendly tech illustration"
</div>

<h2>Team Adoption: The Board Built by the Team, for the Team</h2>
<p>The secret to an onboarding board that stays useful: every new engineer, during their first two weeks, adds at least one thing to the "gotchas" frame that they wish they'd known earlier. This creates a flywheel — the board gets more useful with each hire, and new engineers contribute to the team from their very first week.</p>
<p>Assign the most recent new engineer as the "onboarding board maintainer." They're best positioned to know what's missing or misleading, and the responsibility gives them ownership of a team artifact from day one.</p>
<p>The best onboarding experience is one that new engineers wish they'd had at every previous company. <em>Get the Engineering Onboarding Template and give your next hire the start they deserve.</em></p>
""",
        },
    ],
    "🦀 Languages": [
        {
            "title": "Rust Ownership & Borrowing, Visualized: Teaching Hard Concepts with Miro",
            "description": "How developer advocates and educators use Miro to turn notoriously complex language concepts (ownership, lifetimes, async) into interactive visual explainers that engineers actually bookmark.",
            "demo": "An animated Miro board stepping through a Rust ownership example — stack frames, heap allocations, and borrow checker rules all drawn out live.",
            "format": "Educational Post + Interactive Board",
            "cta": "Open the interactive explainer →",
            "tags": ["rust", "programming", "ownership", "visualization", "miro-templates", "languages"],
            "seo_description": "Teach Rust's ownership and borrowing model with interactive Miro visualizations — turn the borrow checker into an approachable, visual concept for your team.",
            "read_time": "7 min read",
            "hero_prompt": "Rust programming language ownership diagram with stack and heap memory visualized as glowing labeled boxes, ownership arrows moving between scopes, mutable and immutable borrow markers, dark background with rust-orange and steel-blue color scheme",
            "body": """
<p>Rust's ownership system is one of the most powerful ideas in systems programming — and one of the most difficult to teach. The borrow checker enforces rules that are logically consistent and learnable, but deeply counterintuitive to engineers who've spent years working in garbage-collected languages. The result: learning Rust takes longer than it should, not because the concepts are inherently hard, but because most learning resources are primarily textual in a domain where visuals make everything click faster.</p>

<h2>Why Text-Based Rust Education Falls Short</h2>
<p>The Rust book is excellent. The rustlings exercises are well-designed. And yet, engineers routinely report spending days fighting the borrow checker on concepts that, once explained visually, become immediately intuitive. "A value can have only one owner" is an abstract statement. A diagram showing a value moving from one stack frame to another — and disappearing from the first — is a mental model that sticks.</p>
<p>The problem extends beyond individual learning. Teams adopting Rust need shared mental models: what does it mean to "move" a value in a code review? How do you reason about lifetimes in an API design? When is an <em>Arc&lt;Mutex&lt;T&gt;&gt;</em> the right choice? These conversations are faster and more productive when the team shares a visual vocabulary.</p>

<h2>The Miro Framework: Visualizing Rust Concepts</h2>
<ol>
  <li><strong>Ownership diagrams.</strong> For each code example, draw the stack and heap side by side. Show values as labeled boxes. Draw arrows for ownership. When a move happens, redraw the arrow to its new owner and visually erase it from the previous one. The borrow checker's rules become self-evident.</li>
  <li><strong>Borrow visualizations.</strong> Show immutable borrows as read-only arrows (multiple allowed simultaneously). Show mutable borrows as exclusive arrows (only one at a time, blocks immutable borrows). This visual makes the borrow checker's invariants immediately legible.</li>
  <li><strong>Lifetime scope diagrams.</strong> Draw scopes as nested boxes. Show a borrow's lifetime as a colored region that must not outlive the value it borrows. Lifetime annotation syntax suddenly makes sense when you can see what the <em>'a</em> represents spatially.</li>
  <li><strong>Async ownership flow.</strong> For async Rust, draw a timeline showing when ownership moves across await points. Show which values must be Send and why. This is the visualization that unlocks async Rust for engineers who've been stuck.</li>
  <li><strong>Pattern decision tree.</strong> A flowchart for "which smart pointer should I use?" — from simple owned values through <em>Box</em>, <em>Rc</em>, <em>Arc</em>, <em>Mutex</em> — with decision criteria at each fork. Teams use this in code reviews to align on ownership patterns.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "Rust borrow checker visualization showing stack and heap memory as glowing labeled boxes, ownership transfer arrows between scopes, mutable borrow shown as exclusive red arrow, immutable borrows as shared blue arrows, dark background, rust-orange and steel-blue palette"
</div>

<h2>Team Adoption: Visual Rust Reviews</h2>
<p>Engineering teams adopting Rust report that the biggest accelerator isn't better documentation — it's better communication patterns. Starting a "visual Rust review" practice — where complex ownership or lifetime questions get drawn out on the Miro board before being answered in text — dramatically reduces the time senior Rust engineers spend unblocking teammates.</p>
<p>The board also serves as a growing library. Every time a tricky ownership pattern gets solved visually, the diagram stays on the board as a reference. After six months, you have a custom visual Rust guide tailored to the exact patterns your codebase uses.</p>
<p>The borrow checker isn't your enemy — it's a collaborator that rewards clear thinking. <em>Open the interactive Rust Ownership Explainer and see the concepts click in a way they never did in a text editor.</em></p>
""",
        },
    ],
}

DEFAULT_RECS = [
    {
        "title": "Engineering Team Rituals, Visualized: Standups, Retros & More in Miro",
        "description": "How high-performing engineering teams run their core rituals — standup, sprint planning, retros, and incident reviews — asynchronously and visually in Miro, cutting meeting time by 40%.",
        "demo": "A complete sprint board: backlog → in-progress → done, with inline retro stickies, velocity chart, and blocked items highlighted.",
        "format": "Playbook + 5 Templates",
        "cta": "Download the Engineering Rituals Template Pack →",
        "topic": "🔧 Engineering",
        "tags": ["engineering", "team-rituals", "agile", "retros", "miro-templates", "productivity"],
        "seo_description": "Run your engineering team's core rituals — standups, retros, sprint planning, and incident reviews — async and visually in Miro.",
        "read_time": "5 min read",
        "hero_prompt": "Engineering team sprint board with backlog, in-progress, and done swim lanes as glowing columns, retro sticky notes and velocity chart overlaid, dark background with purple sprint highlights and green completion indicators",
        "body": """
<p>Engineering rituals are the connective tissue of a high-performing team — standups, sprint planning, retrospectives, incident reviews. Done well, they align the team, surface blockers, and drive continuous improvement. Done poorly, they waste 20% of the team's week and leave everyone feeling like they could have sent an email. The difference is rarely the ritual itself; it's the tooling and structure around it.</p>

<h2>Why Meeting-Heavy Rituals Don't Scale</h2>
<p>Most engineering teams run their rituals synchronously by default — everyone in a video call at the same time, waiting for their turn to share an update. This works at 5 people. At 15 people, standup takes 25 minutes. At 25 people, you've split into sub-teams and lost the cross-team visibility that made standup valuable in the first place.</p>
<p>The ritual infrastructure hasn't kept pace with team size. A virtual sticky note board gets teams partway there, but without a structured template, each ritual devolves into a blank canvas that someone has to organize from scratch every sprint.</p>

<h2>The Miro Framework: Five Core Engineering Rituals</h2>
<ol>
  <li><strong>Async standup.</strong> A daily Miro frame with three columns: Done Yesterday, Doing Today, Blockers. Engineers update their row asynchronously. Blockers get a red sticky; the Scrum Master scans them in 5 minutes instead of a 20-minute meeting.</li>
  <li><strong>Sprint planning board.</strong> Backlog → Sprint → In Progress → Done. Each card links to the Jira ticket. Story point estimates visible at a glance. Capacity planning via swim lanes per engineer.</li>
  <li><strong>Retrospective template.</strong> Four quadrants: Went Well, Could Improve, Action Items, Kudos. Team adds stickies async before the meeting; the sync session focuses on discussion and actions, not brainstorming. 45 minutes instead of 90.</li>
  <li><strong>Incident review board.</strong> Timeline of the incident, contributing factors, detection lag, and action items — all visible in one frame. Linked to the post-mortem doc. Referenced in the next sprint planning for remediation tickets.</li>
  <li><strong>Velocity and health dashboard.</strong> A simple chart frame updated each sprint: story points completed, escaped defects, on-call incidents. Not for management — for the team to see their own trajectory.</li>
</ol>

<div class="image-callout">
  <strong>🎨 Mid-Post Image Suggestion</strong><br>
  <em>AI prompt:</em> "Agile sprint board with four swim lanes showing team members' work items in backlog, in-progress, review, and done states, colorful sticky notes and a velocity trend chart in the corner, dark background with purple sprint cycle highlights"
</div>

<h2>Team Adoption: The Ritual Refresh</h2>
<p>The most common failure mode for Miro-based rituals: teams set them up with enthusiasm, use them for two sprints, and then revert to the old way when the board gets cluttered and nobody takes ownership of maintaining it. The fix is simple: assign a "board keeper" role that rotates each sprint. Their job is to archive last sprint's board, set up the new one, and ensure everyone knows where to go. 30 minutes of work that keeps the whole team's ritual infrastructure clean.</p>
<p>Teams that run async rituals consistently report meaningful time savings per engineer per week — reclaimed for actual engineering. The rituals become more valuable, not less, because the focused sync time is used for discussion rather than status updates.</p>
<p>The best meetings are the ones that are short because the async work was done first. <em>Download the Engineering Rituals Template Pack and run your next sprint on autopilot.</em></p>
""",
    },
]


def classify_topic(title, description=""):
    text = (title + " " + description).lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return topic
    return "🔧 Engineering"


def fetch_hn_top(limit=30):
    print("  Fetching Hacker News...")
    articles = []
    try:
        ids = requests.get(HN_TOP_STORIES_URL, timeout=8).json()[:limit]
        for item_id in ids[:limit]:
            try:
                item = requests.get(HN_ITEM_URL.format(item_id), timeout=5).json()
                if item and item.get("type") == "story" and item.get("title"):
                    articles.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                        "score": item.get("score", 0),
                        "source": "Hacker News", "source_icon": "🟠",
                        "topic": classify_topic(item.get("title", "")),
                        "comments_url": f"https://news.ycombinator.com/item?id={item_id}",
                        "comments": item.get("descendants", 0),
                        "date": datetime.fromtimestamp(item.get("time", 0)).strftime("%b %d") if item.get("time") else "",
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"  ⚠️  HN error: {e}")
    print(f"  ✅ HN: {len(articles)} articles")
    return articles


def fetch_devto(limit=20):
    print("  Fetching dev.to...")
    articles = []
    endpoints = [
        f"{DEVTO_API_URL}?per_page={limit}&top=7",
        f"{DEVTO_API_URL}?per_page={limit}&tag=programming&top=3",
        f"{DEVTO_API_URL}?per_page=10&tag=devops&top=3",
        f"{DEVTO_API_URL}?per_page=10&tag=ai&top=3",
    ]
    seen = set()
    for url in endpoints:
        try:
            data = requests.get(url, timeout=8, headers={"User-Agent": "EngBrandMachine/1.0"}).json()
            for a in data:
                if a.get("id") not in seen:
                    seen.add(a.get("id"))
                    articles.append({
                        "title": a.get("title", ""),
                        "url": a.get("url", ""),
                        "score": a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 2,
                        "source": "dev.to", "source_icon": "🟣",
                        "topic": classify_topic(a.get("title", ""), a.get("description", "")),
                        "comments_url": a.get("url", ""),
                        "comments": a.get("comments_count", 0),
                        "date": a.get("published_at", "")[:10] if a.get("published_at") else "",
                        "reading_time": a.get("reading_time_minutes", 0),
                    })
        except Exception as e:
            print(f"  ⚠️  dev.to error ({url[:50]}): {e}")
    print(f"  ✅ dev.to: {len(articles)} articles")
    return articles


def fetch_rss_feeds():
    print("  Fetching RSS feeds...")
    articles = []
    for name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries[:8]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                if title and link:
                    articles.append({
                        "title": title, "url": link, "score": 0,
                        "source": name, "source_icon": "🔵",
                        "topic": classify_topic(title, summary),
                        "comments_url": link, "comments": 0,
                        "date": entry.get("published", "")[:10] if entry.get("published") else "",
                    })
                    count += 1
            print(f"    ✅ {name}: {count}")
        except Exception as e:
            print(f"    ⚠️  {name}: {e}")
    return articles


def fetch_reddit(time_filter="week", limit=15):
    """Fetch top posts from each subreddit using the public JSON API — no auth needed."""
    print("  Fetching Reddit (JSON API, no auth)...")
    articles = []
    seen = set()
    for display_name, sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t={time_filter}&limit={limit}"
        try:
            resp = requests.get(url, headers=REDDIT_HEADERS, timeout=8)
            if resp.status_code == 429:
                print(f"    ⚠️  {display_name}: rate limited, skipping")
                continue
            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            count = 0
            for post in posts:
                p = post.get("data", {})
                title = p.get("title", "").strip()
                # Skip low-effort posts, image-only, and meta posts
                if not title or p.get("is_video") or p.get("score", 0) < 50:
                    continue
                url_dest = p.get("url", f"https://reddit.com{p.get('permalink','')}")
                post_id = p.get("id")
                if post_id in seen:
                    continue
                seen.add(post_id)
                articles.append({
                    "title": title,
                    "url": url_dest,
                    "score": p.get("score", 0),
                    "source": display_name,
                    "source_icon": "🔴",
                    "topic": classify_topic(title, p.get("selftext", "")[:300]),
                    "comments_url": f"https://reddit.com{p.get('permalink','')}",
                    "comments": p.get("num_comments", 0),
                    "date": datetime.fromtimestamp(p.get("created_utc", 0)).strftime("%b %d") if p.get("created_utc") else "",
                    "subreddit": display_name,
                    "upvote_ratio": p.get("upvote_ratio", 0),
                })
                count += 1
            print(f"    ✅ {display_name}: {count}")
        except Exception as e:
            print(f"    ⚠️  {display_name}: {e}")
    print(f"  ✅ Reddit total: {len(articles)} posts")
    return articles


def count_topics(articles):
    counts = defaultdict(int)
    for a in articles:
        counts[a["topic"]] += 1
    return sorted(counts.items(), key=lambda x: -x[1])


def generate_miro_recommendations(articles, topic_counts):
    """Pick top 5 Miro content recommendations based on what's actually trending."""
    by_topic = defaultdict(list)
    for a in articles:
        by_topic[a["topic"]].append(a)

    recs = []
    used_topics = set()

    for topic, _count in topic_counts:
        if len(recs) >= 5:
            break
        if topic in MIRO_CONTENT_TEMPLATES and topic not in used_topics:
            template = MIRO_CONTENT_TEMPLATES[topic][0]
            # Pick the top scored article as "inspiration"
            top_arts = sorted(by_topic[topic], key=lambda x: -x["score"])[:2]
            inspired = [a["title"] for a in top_arts if a["title"]]
            recs.append({**template, "topic": topic, "inspired_by": inspired})
            used_topics.add(topic)

    # Pad with default if needed
    while len(recs) < 5:
        recs.append({**DEFAULT_RECS[0], "inspired_by": []})

    return recs[:5]


def generate_html(articles, topic_counts, miro_recs):
    total = len(articles)
    sources = defaultdict(int)
    for a in articles:
        sources[a["source"]] += 1

    # ── Reddit config checkboxes (for the JS-driven interactive panel) ─────────
    sub_checkboxes_html = ""
    for display_name, sub in SUBREDDITS:
        sub_checkboxes_html += f'''<label class="sub-check-label">
          <input type="checkbox" class="sub-check" value="{html_lib.escape(sub)}" checked>
          {html_lib.escape(display_name)}
        </label>'''

    top_articles = sorted(articles, key=lambda x: -x["score"])[:50]
    by_topic = defaultdict(list)
    for a in articles:
        by_topic[a["topic"]].append(a)

    # ── Miro Recommendations Cards ─────────────────────────────────────────────
    rec_cards = ""
    for i, rec in enumerate(miro_recs, 1):
        inspired_html = ""
        if rec.get("inspired_by"):
            items = "".join(f"<li>{html_lib.escape(t)}</li>" for t in rec["inspired_by"][:2])
            inspired_html = f'<div class="inspired"><strong>Inspired by trending:</strong><ul>{items}</ul></div>'

        tags_html = "".join(
            f'<span class="post-tag">#{html_lib.escape(t)}</span>'
            for t in rec.get("tags", [])
        )
        hero_prompt_esc = html_lib.escape(rec.get("hero_prompt", ""))
        seo_desc_esc = html_lib.escape(rec.get("seo_description", ""))
        read_time_esc = html_lib.escape(rec.get("read_time", ""))
        body_html = rec.get("body", "")  # raw HTML, no escaping

        rec_cards += f'''
        <div class="rec-card">
          <div class="rec-num">#{i}</div>
          <div class="rec-topic">{html_lib.escape(rec["topic"])}</div>
          <div class="rec-title">{html_lib.escape(rec["title"])}</div>
          <div class="rec-desc">{html_lib.escape(rec["description"])}</div>
          <div class="rec-demo"><strong>🎬 Demo:</strong> {html_lib.escape(rec["demo"])}</div>
          <div class="rec-meta">
            <span class="rec-format">📄 {html_lib.escape(rec["format"])}</span>
            <span class="rec-cta">{html_lib.escape(rec["cta"])}</span>
          </div>
          {inspired_html}
          <button class="view-draft-btn" onclick="toggleDraft(this)">📝 View Full Post Draft ↓</button>
          <div class="post-draft">
            <div class="post-hero">
              <div class="post-hero-label">🎨 Hero Image Prompt (Midjourney / DALL-E)</div>
              <div class="post-hero-prompt">{hero_prompt_esc}</div>
            </div>
            <div class="post-tags">{tags_html}</div>
            <div class="post-meta-bar">⏱ {read_time_esc} &nbsp;·&nbsp; 🔍 {seo_desc_esc}</div>
            <div class="post-body">{body_html}</div>
            <button class="copy-draft-btn" onclick="copyDraft(this)">📋 Copy Draft to Clipboard</button>
          </div>
        </div>'''

    # ── Topic Cards ────────────────────────────────────────────────────────────
    topic_cards = ""
    for topic, count in topic_counts[:8]:
        topic_arts = sorted(by_topic[topic], key=lambda x: -x["score"])[:5]
        items_html = ""
        for art in topic_arts:
            safe_title = html_lib.escape(art["title"])
            safe_url = html_lib.escape(art["url"])
            score_badge = f'<span class="badge">⬆ {art["score"]}</span>' if art["score"] > 0 else ""
            items_html += f'''
            <div class="article-item">
              <a href="{safe_url}" target="_blank">{safe_title}</a>
              <div class="meta">{art["source_icon"]} {html_lib.escape(art["source"])} {score_badge} {html_lib.escape(art.get("date",""))}</div>
            </div>'''
        topic_cards += f'''
        <div class="topic-card">
          <div class="topic-header">{html_lib.escape(topic)} <span class="count">{count}</span></div>
          {items_html}
        </div>'''

    # ── Hot Stories Table ──────────────────────────────────────────────────────
    hot_rows = ""
    for i, art in enumerate(top_articles[:20], 1):
        hot_rows += f'''
        <tr>
          <td class="rank">{i}</td>
          <td><a href="{html_lib.escape(art["url"])}" target="_blank">{html_lib.escape(art["title"])}</a></td>
          <td><span class="source-badge">{art["source_icon"]} {html_lib.escape(art["source"])}</span></td>
          <td class="score">{art["score"]}</td>
          <td>{html_lib.escape(art["topic"])}</td>
          <td>{html_lib.escape(art.get("date",""))}</td>
        </tr>'''

    # ── Source Bars ────────────────────────────────────────────────────────────
    max_count = max(sources.values()) if sources else 1
    source_bars = ""
    for src, cnt in sorted(sources.items(), key=lambda x: -x[1]):
        pct = int(cnt / max_count * 100)
        source_bars += f'''
        <div class="source-row">
          <div class="source-label">{html_lib.escape(src)}</div>
          <div class="bar-wrap"><div class="bar" style="width:{pct}%">{cnt}</div></div>
        </div>'''

    generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🚀 Eng Brand Machine — Miro Developer Brand</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: #0d1117; color: #c9d1d9; min-height: 100vh; }}

  /* ── Header ── */
  header {{ background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            border-bottom: 1px solid #30363d; padding: 28px 40px; }}
  header h1 {{ font-size: 2.4rem; font-weight: 800;
               background: linear-gradient(90deg, #FFD700, #FF6B6B, #bc8cff);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  header .subtitle {{ color: #8b949e; margin-top: 6px; font-size: 0.95rem; }}
  header .miro-badge {{ display: inline-block; background: #FFD700; color: #111;
                        font-weight: 700; font-size: 0.75rem; border-radius: 20px;
                        padding: 3px 10px; margin-top: 10px; }}

  /* ── Stats bar ── */
  .stats-bar {{ display: flex; gap: 16px; padding: 16px 40px; background: #161b22;
                border-bottom: 1px solid #21262d; flex-wrap: wrap; }}
  .stat {{ background: #21262d; border-radius: 8px; padding: 10px 18px; text-align: center; }}
  .stat .num {{ font-size: 1.6rem; font-weight: 700; color: #FFD700; }}
  .stat .label {{ font-size: 0.72rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }}

  /* ── Main layout ── */
  main {{ padding: 30px 40px; max-width: 1400px; margin: 0 auto; }}
  h2 {{ font-size: 1.25rem; color: #e6edf3; margin: 32px 0 16px; padding-bottom: 8px;
        border-bottom: 1px solid #21262d; }}

  /* ── Miro Recommendations ── */
  .recs-section {{ background: linear-gradient(135deg, #1a1025 0%, #0d1117 100%);
                   border: 1px solid #6e40c9; border-radius: 14px; padding: 28px;
                   margin-bottom: 36px; }}
  .recs-section h2 {{ border-bottom-color: #6e40c9; color: #e6edf3; margin-top: 0; }}
  .recs-intro {{ color: #8b949e; font-size: 0.9rem; margin-bottom: 20px; }}
  .recs-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; }}
  .rec-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px;
               padding: 18px; position: relative; transition: border-color .2s, transform .2s; }}
  .rec-card:hover {{ border-color: #bc8cff; transform: translateY(-2px); }}
  .rec-num {{ position: absolute; top: 14px; right: 14px; background: #6e40c9;
              color: #fff; border-radius: 50%; width: 26px; height: 26px; display: flex;
              align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; }}
  .rec-topic {{ font-size: 0.72rem; color: #bc8cff; font-weight: 600; text-transform: uppercase;
                letter-spacing: 0.5px; margin-bottom: 6px; }}
  .rec-title {{ font-size: 1rem; font-weight: 700; color: #e6edf3; margin-bottom: 10px; line-height: 1.4; }}
  .rec-desc {{ font-size: 0.84rem; color: #8b949e; line-height: 1.55; margin-bottom: 10px; }}
  .rec-demo {{ font-size: 0.82rem; color: #c9d1d9; background: #21262d; border-radius: 6px;
               padding: 8px 10px; margin-bottom: 10px; line-height: 1.5; }}
  .rec-meta {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }}
  .rec-format {{ background: #1f6feb22; color: #58a6ff; border-radius: 4px;
                 padding: 2px 8px; font-size: 0.75rem; }}
  .rec-cta {{ color: #3fb950; font-size: 0.78rem; font-style: italic; }}
  .inspired {{ font-size: 0.75rem; color: #6e7681; border-top: 1px solid #21262d;
               padding-top: 8px; margin-top: 4px; }}
  .inspired ul {{ margin: 4px 0 0 14px; }}
  .inspired li {{ margin-bottom: 2px; }}

  /* ── Blog Post Draft ── */
  .view-draft-btn {{ background: #e8720c; color: #fff; border: none; border-radius: 20px;
                    font-size: 0.82rem; font-weight: 700; padding: 8px 16px; cursor: pointer;
                    margin-top: 12px; width: 100%; transition: background .15s; }}
  .view-draft-btn:hover {{ background: #ff8c2a; }}
  .post-draft {{ display: none; margin-top: 14px; border-top: 1px solid #30363d; padding-top: 14px; }}
  .post-draft.open {{ display: block; }}
  .post-hero {{ background: linear-gradient(135deg, #1a0a2e 0%, #0d1117 100%);
               border: 1px solid #6e40c9; border-radius: 8px; padding: 20px; margin-bottom: 12px; }}
  .post-hero-label {{ font-size: 0.7rem; color: #bc8cff; text-transform: uppercase;
                     letter-spacing: 0.5px; font-weight: 600; margin-bottom: 6px; }}
  .post-hero-prompt {{ font-family: "SFMono-Regular", Consolas, monospace; font-size: 0.78rem;
                      color: #8b949e; line-height: 1.5; }}
  .post-tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }}
  .post-tag {{ background: #161b22; color: #58a6ff; border: 1px solid #1f6feb44;
              border-radius: 12px; font-size: 0.72rem; padding: 2px 8px; }}
  .post-meta-bar {{ font-size: 0.75rem; color: #8b949e; margin-bottom: 12px;
                   border-bottom: 1px solid #21262d; padding-bottom: 8px; }}
  .post-body h2 {{ font-size: 1rem; color: #e6edf3; margin: 16px 0 8px; padding-bottom: 4px;
                  border-bottom: 1px solid #21262d; }}
  .post-body h3 {{ font-size: 0.9rem; color: #c9d1d9; margin: 12px 0 6px; }}
  .post-body p {{ font-size: 0.85rem; color: #8b949e; line-height: 1.6; margin-bottom: 10px; }}
  .post-body ul, .post-body ol {{ font-size: 0.85rem; color: #8b949e; margin: 0 0 10px 20px; line-height: 1.6; }}
  .post-body li {{ margin-bottom: 4px; }}
  .post-body strong {{ color: #c9d1d9; }}
  .post-body em {{ color: #bc8cff; font-style: italic; }}
  .image-callout {{ background: #1a1025; border: 1px solid #6e40c922; border-left: 3px solid #bc8cff;
                   border-radius: 6px; padding: 10px 14px; margin: 12px 0; font-size: 0.82rem;
                   color: #8b949e; line-height: 1.5; }}
  .image-callout strong {{ color: #bc8cff; }}
  .copy-draft-btn {{ background: #1a4a2e; color: #3fb950; border: 1px solid #3fb95044;
                    border-radius: 6px; font-size: 0.82rem; font-weight: 700; padding: 8px 16px;
                    cursor: pointer; margin-top: 10px; width: 100%; transition: background .15s; }}
  .copy-draft-btn:hover {{ background: #1f6b3a; }}

  /* ── Topic cards ── */
  .topics-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; margin-bottom: 30px; }}
  .topic-card {{ background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 16px; transition: border-color .2s; }}
  .topic-card:hover {{ border-color: #58a6ff; }}
  .topic-header {{ font-size: 1rem; font-weight: 700; color: #e6edf3; margin-bottom: 12px;
                   display: flex; justify-content: space-between; align-items: center; }}
  .count {{ background: #1f6feb; color: #fff; border-radius: 12px; padding: 2px 8px;
             font-size: 0.75rem; font-weight: 600; }}
  .article-item {{ padding: 8px 0; border-bottom: 1px solid #21262d; }}
  .article-item:last-child {{ border-bottom: none; }}
  .article-item a {{ color: #58a6ff; text-decoration: none; font-size: 0.87rem; line-height: 1.4; }}
  .article-item a:hover {{ text-decoration: underline; color: #79c0ff; }}
  .meta {{ font-size: 0.73rem; color: #8b949e; margin-top: 3px; }}
  .badge {{ background: #1f6feb22; color: #58a6ff; border-radius: 4px; padding: 1px 5px; font-size: 0.7rem; }}

  /* ── Table ── */
  table {{ width: 100%; border-collapse: collapse; background: #161b22; border-radius: 10px;
           overflow: hidden; border: 1px solid #21262d; margin-bottom: 30px; }}
  thead th {{ background: #21262d; padding: 11px 14px; text-align: left; font-size: 0.78rem;
              text-transform: uppercase; letter-spacing: 0.5px; color: #8b949e; }}
  tbody tr {{ border-top: 1px solid #21262d; transition: background .15s; }}
  tbody tr:hover {{ background: #1c2128; }}
  td {{ padding: 9px 14px; font-size: 0.84rem; }}
  td a {{ color: #58a6ff; text-decoration: none; }}
  td a:hover {{ text-decoration: underline; }}
  .rank {{ color: #8b949e; font-weight: 700; font-size: 1rem; width: 38px; }}
  .score {{ color: #3fb950; font-weight: 600; }}
  .source-badge {{ background: #21262d; border-radius: 4px; padding: 2px 6px; font-size: 0.74rem; white-space: nowrap; }}

  /* ── Sources ── */
  .sources-section {{ background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 20px; margin-bottom: 30px; }}
  .source-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }}
  .source-label {{ min-width: 190px; font-size: 0.84rem; color: #c9d1d9; }}
  .bar-wrap {{ flex: 1; background: #21262d; border-radius: 4px; height: 20px; }}
  .bar {{ background: linear-gradient(90deg, #FFD700, #FF6B6B); border-radius: 4px; height: 20px;
          display: flex; align-items: center; padding-left: 8px; color: #111; font-size: 0.74rem;
          font-weight: 700; min-width: 30px; }}

  /* ── Reddit section ── */
  .reddit-section {{ background: linear-gradient(135deg, #1a0f0f 0%, #0d1117 100%);
                     border: 1px solid #ff4500; border-radius: 14px; padding: 28px; margin-bottom: 36px; }}
  .reddit-section h2 {{ border-bottom-color: #ff4500; color: #e6edf3; margin-top: 0; }}
  .reddit-badge {{ background: #ff450022; color: #ff6b35; border: 1px solid #ff450044; }}
  .reddit-card {{ border-color: #ff450033; }}
  .reddit-card:hover {{ border-color: #ff4500; }}
  .reddit-count {{ background: #ff4500; }}
  .reddit-score {{ color: #ff6b35; font-weight: 700; }}
  .ratio {{ background: #1a2a1a; color: #3fb950; border-radius: 4px;
            padding: 1px 5px; font-size: 0.7rem; margin-left: 6px; }}

  /* ── Reddit config panel ── */
  .reddit-config {{ background: #12080a; border: 1px solid #ff450055; border-radius: 10px;
                    padding: 16px 20px; margin-bottom: 20px; }}
  .reddit-config-title {{ font-size: 0.78rem; font-weight: 700; color: #ff6b35;
                           text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }}
  .sub-checkboxes {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }}
  .sub-check-label {{ display: flex; align-items: center; gap: 5px; font-size: 0.78rem;
                      color: #c9d1d9; background: #1a1010; border: 1px solid #ff450033;
                      border-radius: 16px; padding: 3px 10px; cursor: pointer;
                      transition: border-color .15s, background .15s; user-select: none; }}
  .sub-check-label:hover {{ border-color: #ff4500; background: #220d0d; }}
  .sub-check-label input {{ accent-color: #ff4500; cursor: pointer; }}
  .reddit-controls {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }}
  .reddit-controls input[type=text] {{ background: #1a1010; border: 1px solid #ff450044;
                                        border-radius: 6px; color: #c9d1d9; font-size: 0.83rem;
                                        padding: 6px 10px; outline: none; width: 220px; }}
  .reddit-controls input[type=text]:focus {{ border-color: #ff6b35; }}
  .reddit-controls select {{ background: #1a1010; border: 1px solid #ff450044; border-radius: 6px;
                              color: #c9d1d9; font-size: 0.83rem; padding: 6px 10px; outline: none; cursor: pointer; }}
  .reddit-controls select:focus {{ border-color: #ff6b35; }}
  .fetch-btn {{ background: #ff4500; color: #fff; border: none; border-radius: 6px;
                font-size: 0.85rem; font-weight: 700; padding: 7px 18px; cursor: pointer;
                transition: background .15s, transform .1s; }}
  .fetch-btn:hover {{ background: #ff6b35; }}
  .fetch-btn:active {{ transform: scale(0.97); }}
  .fetch-btn:disabled {{ background: #7a3020; cursor: not-allowed; opacity: 0.7; }}
  .fetch-status {{ font-size: 0.8rem; color: #8b949e; font-style: italic; }}
  .loading-spinner {{ display: inline-block; width: 12px; height: 12px; border: 2px solid #ff450044;
                      border-top-color: #ff4500; border-radius: 50%; animation: spin .7s linear infinite;
                      margin-right: 6px; vertical-align: middle; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

  footer {{ text-align: center; padding: 24px; color: #484f58; font-size: 0.78rem;
            border-top: 1px solid #21262d; margin-top: 20px; }}
</style>
</head>
<body>

<header>
  <h1>🚀 Eng Brand Machine</h1>
  <p class="subtitle">Real-time engineering trends from {len(sources)} sources · {total} articles · {generated_at}</p>
  <span class="miro-badge">✦ Miro Developer Brand Intelligence</span>
</header>

<div class="stats-bar">
  <div class="stat"><div class="num">{total}</div><div class="label">Articles Analyzed</div></div>
  <div class="stat"><div class="num">{len(sources)}</div><div class="label">Live Sources</div></div>
  <div class="stat"><div class="num">{len(topic_counts)}</div><div class="label">Topics Tracked</div></div>
  <div class="stat"><div class="num">{topic_counts[0][0] if topic_counts else "—"}</div><div class="label">Hottest Topic</div></div>
  <div class="stat"><div class="num">{topic_counts[0][1] if topic_counts else 0}</div><div class="label">Articles on #1 Topic</div></div>
</div>

<main>

  <div class="recs-section">
    <h2>✦ Top 5 Content Recommendations for Miro&apos;s Developer Brand</h2>
    <p class="recs-intro">Generated from {total} articles across {len(sources)} sources — each recommendation is anchored to what engineers are actually reading today.</p>
    <div class="recs-grid">
      {rec_cards}
    </div>
  </div>

  <div class="reddit-section">
    <h2>🔴 Reddit — Interactive Subreddit Feed</h2>
    <p class="recs-intro">Select subreddits, set a time filter, and click Fetch to pull live data directly from Reddit's public API.</p>

    <div class="reddit-config">
      <div class="reddit-config-title">⚙ Subreddits to fetch</div>
      <div class="sub-checkboxes" id="sub-checkboxes">
        {sub_checkboxes_html}
      </div>
      <div class="reddit-controls">
        <input type="text" id="custom-sub" placeholder="Add custom: vim, cpp, ..." />
        <select id="time-filter">
          <option value="day">Today</option>
          <option value="week" selected>This Week</option>
          <option value="month">This Month</option>
          <option value="year">This Year</option>
          <option value="all">All Time</option>
        </select>
        <button class="fetch-btn" id="fetch-btn" onclick="fetchReddit()">🔴 Fetch Reddit</button>
        <span class="fetch-status" id="fetch-status"></span>
      </div>
    </div>

    <div id="reddit-results">
      <!-- JS will render results here on load -->
      <div style="text-align:center;padding:40px;color:#484f58;">
        <div class="loading-spinner"></div> Loading Reddit data...
      </div>
    </div>
  </div>

  <h2>🔥 Trending Topics Across Engineering</h2>
  <div class="topics-grid">
    {topic_cards}
  </div>

  <h2>📊 Top Stories Right Now</h2>
  <table>
    <thead>
      <tr><th>#</th><th>Title</th><th>Source</th><th>Score</th><th>Topic</th><th>Date</th></tr>
    </thead>
    <tbody>{hot_rows}</tbody>
  </table>

  <h2>📡 Source Coverage ({len(sources)} sources)</h2>
  <div class="sources-section">{source_bars}</div>

</main>
<footer>Built with ❤️ at the hackathon · Eng Brand Machine · {generated_at}</footer>

<script>
// ── Topic classifier (mirrors Python TOPIC_KEYWORDS) ──────────────────────
const TOPIC_KEYWORDS = {{
  "🤖 AI / ML":        ["ai", "machine learning", "llm", "gpt", "neural", "ml", "deep learning",
                         "openai", "claude", "gemini", "model", "transformer", "rag", "vector",
                         "embedding", "agent", "copilot", "diffusion", "inference", "fine-tun"],
  "☁️ Cloud / Infra":  ["cloud", "aws", "azure", "gcp", "kubernetes", "k8s", "serverless",
                         "lambda", "container", "docker", "terraform", "infra", "platform"],
  "🔐 Security":       ["security", "vulnerability", "exploit", "cve", "auth", "zero-day",
                         "breach", "encryption", "firewall", "hack", "phishing", "malware", "zero trust"],
  "⚡ Performance":    ["performance", "latency", "throughput", "optimization", "benchmark",
                         "profiling", "cache", "fast", "speed", "scalab"],
  "🦀 Languages":      ["rust", "go", "golang", "python", "javascript", "typescript", "java",
                         "swift", "kotlin", "wasm", "webassembly", "zig", "elixir", "ruby"],
  "🛠️ DevOps / SRE":  ["devops", "ci/cd", "cicd", "pipeline", "deployment", "gitops",
                         "monitoring", "observability", "logging", "sre", "platform engineer"],
  "🗄️ Databases":      ["database", "postgres", "mysql", "mongodb", "redis", "sql", "nosql",
                         "vector db", "sqlite", "elasticsearch", "kafka", "streaming", "graph db"],
  "🌐 Web / Frontend": ["react", "vue", "angular", "nextjs", "svelte", "css", "frontend",
                         "browser", "web", "html", "graphql", "rest", "http", "wasm"],
  "📱 Mobile":         ["ios", "android", "mobile", "swift", "flutter", "react native"],
  "🏗️ Architecture":   ["architecture", "microservices", "design pattern", "ddd", "event",
                         "distributed", "system design", "monolith", "refactor", "domain"],
  "🧪 Testing / QA":   ["test", "testing", "qa", "unit test", "e2e", "coverage", "playwright",
                         "cypress", "jest", "quality"],
  "🎨 Dev Experience": ["dx", "developer experience", "tooling", "ide", "vscode", "editor",
                         "productivity", "workflow", "developer tool"],
}};

function classifyTopic(title, body) {{
  const text = (title + " " + (body || "")).toLowerCase();
  for (const [topic, keywords] of Object.entries(TOPIC_KEYWORDS)) {{
    for (const kw of keywords) {{
      if (text.includes(kw)) return topic;
    }}
  }}
  return "🔧 Engineering";
}}

// ── Helpers ───────────────────────────────────────────────────────────────
function setStatus(msg, loading) {{
  const el = document.getElementById("fetch-status");
  el.innerHTML = loading
    ? `<span class="loading-spinner"></span>${{msg}}`
    : msg;
}}

function escHtml(s) {{
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}}

function fmtDate(utc) {{
  if (!utc) return "";
  const d = new Date(utc * 1000);
  return d.toLocaleDateString("en-US", {{ month: "short", day: "numeric" }});
}}

// ── Post draft toggle / copy ──────────────────────────────────────────────
function toggleDraft(btn) {{
  const draft = btn.nextElementSibling;
  draft.classList.toggle('open');
  btn.textContent = draft.classList.contains('open')
    ? '📝 Hide Post Draft ↑'
    : '📝 View Full Post Draft ↓';
}}

function copyDraft(btn) {{
  const body = btn.previousElementSibling.querySelector('.post-body');
  const text = body.innerText;
  navigator.clipboard.writeText(text).then(() => {{
    const orig = btn.textContent;
    btn.textContent = '✅ Copied!';
    setTimeout(() => btn.textContent = orig, 2000);
  }}).catch(() => {{
    btn.textContent = '⚠ Copy failed — select text manually';
  }});
}}

// ── Main fetch + render ───────────────────────────────────────────────────
async function fetchReddit() {{
  const btn = document.getElementById("fetch-btn");
  btn.disabled = true;

  const subs = [...document.querySelectorAll(".sub-check:checked")].map(el => el.value);
  const customRaw = document.getElementById("custom-sub").value.trim();
  if (customRaw) {{
    customRaw.split(",").forEach(s => {{ const t = s.trim(); if (t) subs.push(t); }});
  }}
  if (subs.length === 0) {{
    setStatus("⚠ No subreddits selected.");
    btn.disabled = false;
    return;
  }}

  const filter = document.getElementById("time-filter").value;
  setStatus(`Fetching ${{subs.length}} subreddit${{subs.length > 1 ? "s" : ""}}...`, true);

  const results = await Promise.all(subs.map(sub =>
    fetch(`https://www.reddit.com/r/${{sub}}/top.json?t=${{filter}}&limit=25`, {{
      headers: {{ "Accept": "application/json" }}
    }})
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(d => ({{ sub, posts: d.data?.children || [] }}))
    .catch(() => ({{ sub, posts: [] }}))
  ));

  // Flatten & deduplicate by post id
  const seen = new Set();
  const allPosts = [];
  const bySubreddit = {{}};

  for (const {{ sub, posts }} of results) {{
    bySubreddit[sub] = [];
    for (const child of posts) {{
      const p = child.data;
      if (!p || !p.title || p.is_video || (p.score || 0) < 50) continue;
      if (seen.has(p.id)) continue;
      seen.add(p.id);
      const post = {{
        id: p.id,
        title: p.title,
        url: p.url || `https://reddit.com${{p.permalink}}`,
        comments_url: `https://reddit.com${{p.permalink}}`,
        score: p.score || 0,
        comments: p.num_comments || 0,
        upvote_ratio: p.upvote_ratio || 0,
        date: fmtDate(p.created_utc),
        source: `r/${{sub}}`,
        topic: classifyTopic(p.title, (p.selftext || "").slice(0, 300)),
      }};
      allPosts.push(post);
      bySubreddit[sub].push(post);
    }}
  }}

  allPosts.sort((a, b) => b.score - a.score);

  // ── Render ──────────────────────────────────────────────────────────────
  const top15 = allPosts.slice(0, 15);

  let tableRows = "";
  top15.forEach((p, i) => {{
    const ratio = p.upvote_ratio
      ? `<span class="ratio">${{Math.round(p.upvote_ratio * 100)}}% up</span>`
      : "";
    tableRows += `
    <tr>
      <td class="rank">${{i + 1}}</td>
      <td>
        <a href="${{escHtml(p.url)}}" target="_blank">${{escHtml(p.title)}}</a>
        <div class="meta">
          <a href="${{escHtml(p.comments_url)}}" target="_blank" style="color:#ff6b6b">
            💬 ${{p.comments}} comments
          </a>
        </div>
      </td>
      <td><span class="source-badge reddit-badge">${{escHtml(p.source)}}</span></td>
      <td class="score reddit-score">⬆ ${{p.score}} ${{ratio}}</td>
      <td>${{escHtml(p.topic)}}</td>
      <td>${{escHtml(p.date)}}</td>
    </tr>`;
  }});

  // Per-subreddit cards (top 9 subs by total score)
  const subEntries = Object.entries(bySubreddit)
    .filter(([_, posts]) => posts.length > 0)
    .sort((a, b) => b[1].reduce((s, p) => s + p.score, 0) - a[1].reduce((s, p) => s + p.score, 0))
    .slice(0, 9);

  let subCards = "";
  for (const [sub, posts] of subEntries) {{
    const top3 = posts.slice(0, 3);
    let items = "";
    for (const p of top3) {{
      items += `
      <div class="article-item">
        <a href="${{escHtml(p.url)}}" target="_blank">${{escHtml(p.title)}}</a>
        <div class="meta">⬆ ${{p.score}} · 💬 ${{p.comments}} · ${{escHtml(p.date)}}</div>
      </div>`;
    }}
    subCards += `
    <div class="topic-card reddit-card">
      <div class="topic-header">r/${{escHtml(sub)}} <span class="count reddit-count">${{posts.length}}</span></div>
      ${{items}}
    </div>`;
  }}

  const totalSubs = subEntries.length;
  const html = `
    <h3 style="color:#ff6b35;font-size:0.95rem;margin:16px 0 10px">
      Top Posts Across All Subreddits (${{allPosts.length}} posts · ${{totalSubs}} subs)
    </h3>
    <table>
      <thead>
        <tr><th>#</th><th>Title</th><th>Subreddit</th><th>Score</th><th>Topic</th><th>Date</th></tr>
      </thead>
      <tbody>${{tableRows}}</tbody>
    </table>
    <h3 style="color:#ff6b35;font-size:0.95rem;margin:20px 0 10px">By Subreddit</h3>
    <div class="topics-grid">${{subCards}}</div>
  `;

  document.getElementById("reddit-results").innerHTML = html;

  const filterLabel = document.getElementById("time-filter").selectedOptions[0].text;
  setStatus(`✅ ${{allPosts.length}} posts from ${{totalSubs}} subreddits · ${{filterLabel}}`);
  btn.disabled = false;
}}

document.addEventListener("DOMContentLoaded", fetchReddit);
</script>
</body>
</html>'''


def main():
    print("\n🚀 Eng Brand Machine — Aggregating Engineering Trends\n" + "=" * 58)

    all_articles = []
    all_articles.extend(fetch_hn_top(30))
    all_articles.extend(fetch_devto(20))
    all_articles.extend(fetch_rss_feeds())
    reddit_articles = fetch_reddit()
    all_articles.extend(reddit_articles)

    print(f"\n📊 Total articles: {len(all_articles)}")
    topic_counts = count_topics(all_articles)
    print("\n🏷️  Topics:")
    for t, c in topic_counts:
        print(f"   {t}: {c}")

    miro_recs = generate_miro_recommendations(all_articles, topic_counts)
    print("\n✦ Miro Content Recommendations:")
    for i, r in enumerate(miro_recs, 1):
        print(f"   {i}. [{r['topic']}] {r['title']}")

    reddit_count = len([a for a in all_articles if a["source_icon"] == "🔴"])
    print(f"\n🔴 Reddit posts in dataset: {reddit_count}")

    print("\n🎨 Generating HTML...")
    html = generate_html(all_articles, topic_counts, miro_recs)

    output_path = "/Users/horeaporutiu/eng-brand-machine/index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Saved → {output_path}")
    print(f"   Run: open {output_path}")
    return output_path, len(all_articles), topic_counts, miro_recs

if __name__ == "__main__":
    main()
