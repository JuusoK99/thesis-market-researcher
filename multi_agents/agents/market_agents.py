"""
Market Segmentation and Positioning Agents for IoT Thesis
Implements IoTVerticalAgent, GeoSegmentationAgent, SegmentAgent, PositioningAgent, and CompanyAgent.
Prompts are sourced from agent-prompts.md.
Each agent receives: user_prompt, prior_context, and rag_context.
Web Crawler and Perplexity API are NOT used automatically; only RAG (LlamaIndex) is used for retrieval.
"""
from typing import Optional, Dict

# Move DISCLAIMER here to avoid circular import
DISCLAIMER = "Disclaimer: The following data is synthetic and generated for illustrative purposes only."

class IoTVerticalAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = (
            "# IoT Vertical Analysis\n"
            "Role: Industry Expert in IoT verticals.\n"
            "Task: Analyze and define the {vertical_name} vertical as an IoT application domain.\n"
            "\n"
            "Context:\n"
            "An IoT vertical is an application domain characterized by:\n"
            "- Similar use cases and business objectives\n"
            "- Comparable technology requirements (sensors, connectivity, data processing)\n"
            "- Common industry standards and regulations\n"
            "- Shared market dynamics and customer types\n"
            "\n"
            "Instructions:\n"
            "- Define the vertical as an application domain with clear boundaries\n"
            "- Identify the core use cases that unite this vertical\n"
            "- Describe the typical technology stack and requirements\n"
            "- List main trends and market drivers specific to this domain\n"
            "- Explain barriers and challenges common across this vertical\n"
            "- Highlight what differentiates this vertical from other IoT domains\n"
            "- Mark data as synthetic if based on public summaries."
        )

    def run(self, user_prompt: str, prior_context: Optional[Dict] = None, rag_context: str = "", vertical_name: str = "") -> str:
        prompt = (
            f"{self.prompt_template.format(vertical_name=vertical_name)}\n\n"
            f"User Prompt: {user_prompt}\n\n"
            f"[RAG Context]\n{rag_context}\n"
        )
        result = self.llm_client(prompt)
        return f"{DISCLAIMER}\n\n{result.strip()}"

class GeoSegmentationAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template_single = (
            "# Geo Segmentation Analysis\n"
            "Role: IoT Market Analyst for {region}.\n"
            "Task: Analyze the IoT market landscape in {region} for {vertical_name}.\n"
            "Instructions:\n"
            "- Provide synthetic estimates for market size and growth.\n"
            "- List regulatory factors, competitor presence, and key challenges.\n"
            "- Mark data as synthetic."
        )
        self.prompt_template_multi = (
            """
# Multi-Geo Segmentation Analysis
Role: IoT Market Geography Analyst

Task: Identify and rank promising geographies for the given IoT vertical, based on available RAG context and general market knowledge.

Context:
You will receive:
- The user prompt
- IoT Vertical Agent output
- RAG context (if available)

Instructions:
- You must analyze at least 5 different countries (minimum 5).
- You may analyze up to 7 countries if appropriate.
- Do not include continent-level markets (e.g. 'North America', 'Western Europe', etc.) — use only country-level geographies.
- Use both retrieved RAG context AND your own world knowledge.
- You are NOT limited to geographies present in RAG.
- If RAG data is missing for a country, infer based on general IoT trends for the given vertical — this is acceptable and expected.
- Prioritize markets that differ in market potential, regulatory complexity, competitive intensity, or strategic relevance.
- Prioritize market diversity.

For each country, provide the following structured output:

### Geography: [Country Name]
- Market Size and Growth: [Qualitative assessment]
- Regulatory Factors: [Summary of relevant factors]
- Competitor Presence: [Summary of key players or competitive intensity]
- Key Challenges: [Top 2–3 challenges]
- Market Potential: [Rating 1–5]
- Summary Recommendation: [Go / Further Analyze / Not Recommended]

Important:
- If RAG data is available for a country, use it.
- If no RAG data is available, rely on your knowledge to provide an estimate.
- Be clear when you are inferring information vs. using retrieved data.

- The Segment Agent will use your output to generate segments per country.

Remember: The following data is synthetic and generated for illustrative purposes only.
"""
        )

    def run(self, user_prompt: str, prior_context: Dict, rag_context: str = "", region: str = "", vertical_name: str = "", geo_mode: str = "single") -> str:
        vertical_result = prior_context.get("vertical_result", "")
        if geo_mode == "multi":
            prompt = (
                f"{self.prompt_template_multi}\n\n"
                f"User Prompt: {user_prompt}\n\n"
                f"[IoT Vertical Result]\n{vertical_result}\n\n"
                f"[RAG Context]\n{rag_context}\n"
            )
        else:
            prompt = (
                f"{self.prompt_template_single.format(region=region, vertical_name=vertical_name)}\n\n"
                f"User Prompt: {user_prompt}\n\n"
                f"[IoT Vertical Result]\n{vertical_result}\n\n"
                f"[RAG Context]\n{rag_context}\n"
            )
        result = self.llm_client(prompt)
        return f"{DISCLAIMER}\n\n{result.strip()}"

class SegmentAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = (
            """
# Segment Synthesis
Role: Strategic Market Segment Analyst.

Task: Combine IoT vertical and geographical analysis to define actionable market segments for IoT vendors.

Context:
- You will receive:
    - The user prompt
    - IoT Vertical Agent output (vertical characteristics and trends)
    - Geo Segmentation Agent output (geography-specific market dynamics)
    - RAG context (retrieved high-quality documents)

IoT Technology Stack Context:
When analyzing segments, consider how different technology positioning affects market opportunities:
- Device Layer: Hardware components, sensors, embedded software
- Connectivity Layer: Network communication and data transmission
- IoT Cloud Layer: Platforms, analytics, application development
- Cross-cutting Systems: Security, business integration, external data sources

Instructions:
- Using the provided context, analyze and define a minimum of 5 actionable market segments in the given geography and IoT vertical.
- Ensure segments differ meaningfully in terms of customer types, use cases, technology requirements, or market characteristics.
- For each segment, explicitly evaluate the following variables:

    1. Market size and growth rate: Overall market volume and projected growth within the selected vertical–geography pair
    2. Profitability potential: Expected ROI and margin levels relative to solution scope, pricing model, and buyer willingness to pay
    3. Regulatory requirements and fit: Certification, compliance, and data regulation conditions (e.g., CE, FCC, GDPR, NIS2)
    4. Competitive intensity: Degree of saturation and strength of rival offerings
    5. Digital maturity: Organization readiness of segment to adopt and scale digital IoT systems
    6. Customer consolidation: Centralization of purchasing decisions affecting sales cycle complexity
    7. Technological readiness: Business systems, external information sources, and existing IoT systems integrability

- For each segment, also consider:
    - Which technology layers are most critical for this segment
    - What level of ecosystem complexity customers can handle
    - Whether customers prefer single-layer solutions or integrated offerings

Segment Differentiation Guidelines:
- Create segments based on different customer types (e.g., enterprise vs. SME vs. municipal)
- Consider varying use case complexity (e.g., basic monitoring vs. advanced analytics vs. predictive maintenance)
- Differentiate by technology maturity levels (e.g., early adopters vs. mainstream vs. laggards)
- Account for different regulatory environments or compliance requirements
- Consider varying budget levels and ROI expectations

- Present each segment clearly, structured under these variable headings.
- If any variable lacks sufficient information, state so explicitly.

- Remember: The following data is synthetic and generated for illustrative purposes only.
"""
        )

    def run(self, user_prompt: str, prior_context: Dict, rag_context: str = "") -> str:
        vertical_result = prior_context.get("vertical_result", "")
        geo_result = prior_context.get("geo_result", "")
        prompt = (
            f"{self.prompt_template}\n"
            f"User Prompt: {user_prompt}\n\n"
            f"[IoT Vertical Result]\n{vertical_result}\n\n"
            f"[Geo Segmentation Result]\n{geo_result}\n\n"
            f"[RAG Context]\n{rag_context}\n"
        )
        result = self.llm_client(prompt)
        return f"{DISCLAIMER}\n\n{result.strip()}"

class PositioningAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = (
            """
# Strategic Positioning\n"
Role: IoT Strategic Positioning Advisor.\n\n"
Task: Recommend the most appropriate IoT system architecture positioning layer for the vendor, based strictly on the provided segment analysis and market variable scores.\n\n"
Context:\n\n"
You will receive:\n"
- The user prompt\n"
- IoT Vertical Agent output\n"
- Geo Segmentation Agent output\n"
- Segment Agent output (market variable explanations + scores)\n"
- RAG context (retrieved high-quality documents)\n"
- Private company capability description (not to be included in report)\n\n"
IoT System Architecture Framework:\n"
This layered architecture illustrates technological positioning options for IoT vendors:\n\n"
1. Device Layer ("Thing"):\n"
   - Thing hardware: Core physical components (sensors, boards)\n"
   - IoT components: Embedded processors, sensors, communication ports\n"
   - Thing software: Embedded software managing device functionality\n\n"
2. Connectivity Layer:\n"
   - Network communication: Communication protocols for data transmission\n\n"
3. IoT Cloud Layer:\n"
   - Thing communication and management: Software managing connected devices\n"
   - Application platform: Development environments for IoT applications\n"
   - Analytics and data management: Processing time-series and sensor data\n"
   - Process management and IoT applications: Task execution and coordination\n\n"
Cross-cutting Systems (spanning all layers):\n"
   - Identity and security: Access control and secure operations\n"
   - Integration with business systems: Connection to ERP, CRM, PLM systems\n"
   - External information sources: Third-party data provider connections\n\n"
Instructions:\n\n"
1. Evaluate each of the following market variables (from the Segment Agent):\n"
    - Market size and growth rate: Overall market volume and projected growth within the selected vertical–geography pair\n"
    - Profitability potential: Expected ROI and margin levels relative to solution scope, pricing model, and buyer willingness to pay\n"
    - Regulatory requirements and fit: Certification, compliance, and data regulation conditions (e.g., CE, FCC, GDPR, NIS2)\n"
    - Competitive intensity: Degree of saturation and strength of rival offerings\n"
    - Digital maturity: Organization readiness of segment to adopt and scale digital IoT systems\n"
    - Customer consolidation: Centralization of purchasing decisions affecting sales cycle complexity\n"
    - Technological readiness: Business systems, external information sources, and existing IoT systems integrability\n\n"
2. Based strictly on the Segment Agent output and market variable scores, recommend one of the following positioning strategies:\n"
    - Device Layer: Focus on hardware components, sensors, or embedded software\n"
    - Connectivity Layer: Focus on network communication and data transmission\n"
    - IoT Cloud Layer: Focus on cloud platforms, analytics, or application development\n"
    - Multi-layer (end-to-end): Full-stack positioning across multiple layers\n"
    - Cross-cutting Systems: Focus on security, integration, or external data services\n\n"
3. Consider how ecosystem complexity and integration needs vary by positioning:\n"
    - Device Layer: Lower ecosystem complexity, focused partnerships\n"
    - Cloud Layer: Higher ecosystem complexity, extensive integration needs\n"
    - Multi-layer: Highest complexity, comprehensive ecosystem management\n\n"
4. Justify your recommendation using only the market variable scores and explanations.\n"
5. Do NOT recommend sales actions, partnerships, or general go-to-market advice.\n"
6. Do NOT suggest leveraging capabilities unless it is directly relevant to the system positioning layer.\n"
7. Keep your output clean, technical, and focused on architecture positioning.\n"
8. Begin your output with the disclaimer:\n"
"The following data is synthetic and generated for illustrative purposes only."\n\n"
Remember: This report is public. Do not disclose or reference the private company input directly.\n"""
        )

    def run(self, user_prompt: str, prior_context: Dict, rag_context: str = "", system_architecture: Optional[str] = None, company_capabilities: Optional[str] = None) -> str:
        vertical_result = prior_context.get("vertical_result", "")
        geo_result = prior_context.get("geo_result", "")
        segment_result = prior_context.get("segment_result", "")
        # Compose the prompt, including private company capabilities as a non-output context
        prompt = (
            f"{self.prompt_template}\n"
            f"User Prompt: {user_prompt}\n\n"
            f"[IoT Vertical Result]\n{vertical_result}\n\n"
            f"[Geo Segmentation Result]\n{geo_result}\n\n"
            f"[Segment Synthesis Result]\n{segment_result}\n\n"
            f"[RAG Context]\n{rag_context}\n"
        )
        if company_capabilities:
            prompt += f"\n[Private Company Capabilities] (for LLM context only, do not include in output):\n{company_capabilities}\n"
        if system_architecture:
            prompt += f"\nSystem Architecture: {system_architecture}\n"
        result = self.llm_client(prompt)
        return f"{DISCLAIMER}\n\n{result.strip()}"

class CompanyAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = (
            """
# Company Validation of Positioning
Role: Company Capability Validator.

Task: Evaluate whether the recommended IoT system positioning layer matches the company's capabilities.

Context:
You will receive:
- The user prompt
- IoT Vertical Agent output
- Geo Segmentation Agent output
- Segment Agent output
- Positioning Agent output
- Company capabilities (private, not to be quoted directly)

IoT Technology Stack Framework:
Consider the company's fit across these technological positioning options:
- Device Layer: Hardware design, embedded software, sensor technology
- Connectivity Layer: Network protocols, communication infrastructure
- IoT Cloud Layer: Platform development, data analytics, application services
- Cross-cutting Systems: Security expertise, system integration, data management

Instructions:
1. For each market variable, rate from 1 (poor fit) to 5 (excellent fit) how well the company is positioned to compete, with a brief justification:
    - Market size and growth rate: Overall market volume and projected growth within the selected vertical–geography pair
    - Profitability potential: Expected ROI and margin levels relative to solution scope, pricing model, and buyer willingness to pay
    - Regulatory requirements and fit: Certification, compliance, and data regulation conditions (e.g., CE, FCC, GDPR, NIS2)
    - Competitive intensity: Degree of saturation and strength of rival offerings
    - Digital maturity: Organization readiness of segment to adopt and scale digital IoT systems
    - Customer consolidation: Centralization of purchasing decisions affecting sales cycle complexity
    - Technological readiness: Business systems, external information sources, and existing IoT systems integrability
2. Evaluate the company's technological positioning fit:
    - Assess capabilities across device, connectivity, cloud, and cross-cutting systems
    - Consider the company's ability to handle ecosystem complexity at the recommended layer
    - Evaluate technical depth vs. breadth based on positioning recommendation
3. Provide an ultimate recommendation:
    - Strongly recommended
    - Acceptable with caveats
    - Not recommended
4. Justify your recommendation based on the company capabilities and the Positioning Agent's output.
5. Do NOT quote or paraphrase private company input directly.
6. Output must be concise, actionable, and confidential-friendly.
"""
        )

    def run(self, user_prompt: str, prior_context: Dict, rag_context: str = "") -> str:
        vertical_result = prior_context.get("vertical_result", "")
        geo_result = prior_context.get("geo_result", "")
        segment_result = prior_context.get("segment_result", "")
        positioning_result = prior_context.get("positioning_result", "")
        prompt = (
            f"{self.prompt_template}\n"
            f"User Prompt: {user_prompt}\n\n"
            f"[IoT Vertical Result]\n{vertical_result}\n\n"
            f"[Geo Segmentation Result]\n{geo_result}\n\n"
            f"[Segment Synthesis Result]\n{segment_result}\n\n"
            f"[Positioning Agent Result]\n{positioning_result}\n\n"
            f"[Company Capabilities Context]\n{rag_context}\n"
        )
        result = self.llm_client(prompt)
        return f"{DISCLAIMER}\n\n{result.strip()}"

class SegmentRankingAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = (
            """
# Segment Ranking Table
This Segment Ranking Agent is part of a multi-agent system for GenAI-driven market segmentation and positioning in IoT markets, implemented for a Master's thesis using the Design Science Research methodology.

Instructions:
- For each segment (expect minimum 5 segments), output a single unified table (one row per segment) with the following columns:
| Segment Name | Market Potential (1–5) | Justification for Market Potential | Competitive Intensity (1–5) | Justification for Competitive Intensity | Regulatory Complexity (1–5) | Justification for Regulatory Complexity | Technological Readiness (1–5) | Justification for Technological Readiness | Digital Maturity (1–5) | Justification for Digital Maturity | Fit with Company Capabilities (1–5) | Justification for Fit with Company Capabilities | Ultimate Recommendation |
- Fill in all columns for each segment, using the Segment Agent, Positioning Agent, and Company Capabilities context.
- Output the table in markdown format, with column headers and one row per segment.
- Rank segments by overall attractiveness, with the most promising segments listed first.
- The same table will be exported to Excel for management decision workshops.
- Be concise and actionable. Structure your output clearly.

Remember: The following data is synthetic and generated for illustrative purposes only.
"""
        )

    def run(self, prior_context: Dict, company_capabilities: str = "") -> str:
        segment_result = prior_context.get("segment_result", "")
        positioning_result = prior_context.get("positioning_result", "")
        prompt = (
            f"{self.prompt_template}\n"
            f"[Segment Synthesis Result]\n{segment_result}\n\n"
            f"[Positioning Agent Result]\n{positioning_result}\n\n"
            f"[Company Capabilities Context]\n{company_capabilities}\n"
        )
        result = self.llm_client(prompt)
        return result.strip()
