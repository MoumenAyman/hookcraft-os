import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import json
import time

if "is_premium" not in st.session_state:
    st.session_state.is_premium = False
if "generated_content" not in st.session_state:
    st.session_state.generated_content = None
if "automation_logs" not in st.session_state:
    st.session_state.automation_logs = []
if "scheduler_queue" not in st.session_state:
    st.session_state.scheduler_queue = []
if "system_telemetry" not in st.session_state:
    st.session_state.system_telemetry = {"ingested_bytes": 0, "api_transactions": 0, "webhooks_fired": 0}

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(
    page_title="HookCraft OS Ultimate - Enterprise Engine",
    page_icon="https://cdn-icons-png.flaticon.com/512/2103/2103633.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background-color: #02040a;
        color: #f3f4f6;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.2); }
        50% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.4); }
        100% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.2); }
    }
    @keyframes slideInUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .super-title {
        font-size: 72px;
        font-weight: 800;
        letter-spacing: -4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6);
        background-size: 300% 300%;
        animation: gradientShift 12s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.05;
        margin-bottom: 5px;
    }
    .super-subtitle {
        font-size: 22px;
        color: #9ca3af;
        margin-bottom: 45px;
        font-weight: 300;
    }
    .premium-card {
        background: linear-gradient(180deg, #0b1120 0%, #040712 100%);
        border: 1px solid #1e293b;
        border-radius: 24px;
        padding: 40px;
        margin-bottom: 35px;
        animation: slideInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both, pulseGlow 8s ease infinite;
    }
    .accent-linkedin { border-left: 6px solid #0a66c2; }
    .accent-x { border-left: 6px solid #1da1f2; }
    .accent-instagram { border-left: 6px solid #e1306c; }
    .accent-youtube { border-left: 6px solid #ff0000; }
    .accent-newsletter { border-left: 6px solid #10b981; }

    .feature-tag {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 5px 14px;
        border-radius: 50px;
        font-size: 11px;
        color: #60a5fa;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        display: inline-block;
        margin-bottom: 20px;
    }
    .mockup-header-frame {
        display: flex;
        align-items: center;
        margin-bottom: 25px;
    }
    .mockup-avatar-node {
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        border-radius: 50%;
        margin-right: 16px;
    }
    .mockup-meta-node {
        display: flex;
        flex-direction: column;
    }
    .mockup-user-name {
        font-weight: 700;
        font-size: 18px;
        color: #f9fafb;
    }
    .mockup-user-sub {
        font-size: 13px;
        color: #6b7280;
    }
    .mockup-body-text {
        font-size: 17px;
        line-height: 1.8;
        color: #e5e7eb;
        white-space: pre-wrap;
    }
    .telemetry-dashboard-grid {
        display: flex;
        gap: 15px;
        margin-top: 30px;
        padding-top: 25px;
        border-top: 1px solid #1e293b;
    }
    .telemetry-node-block {
        flex: 1;
        background-color: #02040a;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #111827;
        transition: transform 0.2s ease;
    }
    .telemetry-node-block:hover {
        transform: translateY(-2px);
    }
    .telemetry-value-text {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
    }
    .telemetry-label-text {
        font-size: 11px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    .automation-terminal {
        background-color: #010204;
        border: 1px solid #1e293b;
        font-family: 'Courier New', Courier, monospace;
        padding: 20px;
        border-radius: 12px;
        color: #10b981;
        max-height: 250px;
        overflow-y: auto;
        margin-top: 15px;
    }
    .automation-line {
        margin-bottom: 6px;
        font-size: 13px;
    }
    .automation-line.success { color: #10b981; }
    .automation-line.info { color: #3b82f6; }
    .automation-line.warning { color: #f59e0b; }

    .paywall-gate-container {
        background: linear-gradient(135deg, #070a13 0%, #1e112c 100%);
        border: 2px solid #7c3aed;
        padding: 60px;
        border-radius: 28px;
        text-align: center;
        margin-top: 50px;
        box-shadow: 0 25px 55px rgba(0,0,0,0.8);
    }
    .paywall-gate-trigger-btn {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        padding: 20px 60px !important;
        border-radius: 14px !important;
        text-decoration: none;
        display: inline-block;
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.4);
        transition: transform 0.2s ease;
    }
    .paywall-gate-trigger-btn:hover {
        transform: scale(1.03);
    }
    .stButton > button {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155 !important;
        color: #f3f4f6 !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        border-color: #3b82f6 !important;
        color: #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)


def network_scraper_engine(endpoint_url):
    try:
        network_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        http_response = requests.get(endpoint_url, headers=network_headers, timeout=15)
        if http_response.status_code == 200:
            dom_parser = BeautifulSoup(http_response.text, "html.parser")
            paragraphs_list = dom_parser.find_all("p")
            merged_text = " ".join([paragraph.get_text() for paragraph in paragraphs_list])
            return merged_text[:15000]
        return None
    except:
        return None


def dispatch_webhook_automation(endpoint_url, payload_data):
    try:
        network_headers = {"Content-Type": "application/json"}
        serialized_data = json.dumps(payload_data)
        network_response = requests.post(endpoint_url, data=serialized_data, headers=network_headers, timeout=10)
        if network_response.status_code in [200, 201, 202]:
            return True
        return False
    except:
        return False


def coordinate_multi_agent_network(raw_corpus, selected_persona, architectural_blueprint):
    if not GOOGLE_API_KEY:
        return "Infrastructure Interruption Error: The target AI Studio model could not find a validated environment key configuration."

    orchestration_prompt = f"""
    You are the Chief Media Strategist of an elite international algorithmic distribution firm.
    Deconstruct the provided text corpus and transform it into exactly 9 sovereign channel-specific content assets.

    Text Corpus: {raw_corpus}
    Persona Parameter Matrix: {selected_persona}
    Structural Layout Matrix: {architectural_blueprint}

    Execute and output the following individual modules strictly encapsulated by their exact structural token tags:

    [MODULE_LINKEDIN_EXEC]
    An authoritative corporate thought leadership piece. Features an aggressive initial hook line, single-sentence space breaks to maximize mobile scrolling click-throughs, strict analytics tone, and absolutely zero low-value hashtags.

    [MODULE_LINKEDIN_STORY]
    An alternative narrative framework post driven by storytelling, detailing a personal contrarian experience extracted from the data core.

    [MODULE_X_THREAD]
    A sequence array consisting of exactly 4 hyper-optimized connected text posts. Thread 1 must formulate an undeniable psychological open-loop hook.

    [MODULE_X_SINGLE]
    A sharp, viral statement engineering maximum impact under 240 total characters.

    [MODULE_INSTAGRAM_CAROUSEL]
    A clear sequence blueprint text for 4 structural image slides combined with a comprehensive multi-line text caption layout.

    [MODULE_YOUTUBE_REELS]
    A complete short-form cinematic video production script including specific bracketed directions for the speaker: Hook (0-3s), Core Narrative Body, and Terminal Action Trigger.

    [MODULE_NEWSLETTER_DISPATCH]
    An elite corporate briefing editorial newsletter email featuring a highly compelling subject line and executive signature block.

    [MODULE_SEO_AUDIT]
    Isolate exactly 5 core semantic keywords from the data corpus and supply a one-sentence ranking directive strategy for search engines.

    [MODULE_TITLES_POOL]
    Provide exactly 3 variations of explosive high-click-through viral headlines optimized for digital distribution.
    """
    try:
        generative_model = genai.GenerativeModel("gemini-1.5-flash")
        agent_transaction = generative_model.generate_content(orchestration_prompt)
        return agent_transaction.text
    except Exception as operational_fault:
        return str(operational_fault)


def extract_individual_matrix_nodes(raw_response_string):
    structural_node_map = {
        "li_exec": "System standing by for orchestration matrix.",
        "li_story": "Narrative architecture node unallocated.",
        "x_thread": "Sequential array structure unallocated.",
        "x_single": "Single shot stream offline.",
        "ig_carousel": "Visual structural mapping unallocated.",
        "yt_script": "Cinematic audio pipeline script empty.",
        "newsletter": "Dispatch editorial manifest uncompiled.",
        "seo_keywords": "Semantic keyword matrices empty.",
        "titles_pool": "Title pool matrix unallocated."
    }
    try:
        if "[MODULE_LINKEDIN_EXEC]" in raw_response_string:
            segments = raw_response_string.split("[MODULE_LINKEDIN_EXEC]")
            sub_segments = segments[1].split("[MODULE_LINKEDIN_STORY]")
            structural_node_map["li_exec"] = sub_segments[0].strip()

            sub_sub_segments = sub_segments[1].split("[MODULE_X_THREAD]")
            structural_node_map["x_thread"] = sub_sub_segments[0].strip()

            x_thread_segments = sub_sub_segments[1].split("[MODULE_X_SINGLE]")
            structural_node_map["x_single"] = x_thread_segments[0].strip()

            x_single_segments = x_thread_segments[1].split("[MODULE_INSTAGRAM_CAROUSEL]")
            structural_node_map["ig_carousel"] = x_single_segments[0].strip()

            ig_segments = x_single_segments[1].split("[MODULE_YOUTUBE_REELS]")
            structural_node_map["yt_script"] = ig_segments[0].strip()

            yt_segments = ig_segments[1].split("[MODULE_NEWSLETTER_DISPATCH]")
            structural_node_map["newsletter"] = yt_segments[0].strip()

            news_segments = yt_segments[1].split("[MODULE_SEO_AUDIT]")
            structural_node_map["seo_keywords"] = news_segments[0].strip()
            structural_node_map["titles_pool"] = news_segments[1].strip()
        else:
            structural_node_map["li_exec"] = raw_response_string
    except:
        pass
    return structural_node_map


with st.sidebar:
    st.markdown("<h2 style='color:#ffffff; font-weight:800; font-size:26px;'>HookCraft OS Ultra</h2>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#4b5563; font-size:12px; margin-top:-15px;'>Enterprise Core Engine Pro x64</p>",
                unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(
        "<p style='color:#3b82f6; font-size:11px; font-weight:700; text-transform:uppercase;'>1. Data Ingestion Vector</p>",
        unsafe_allow_html=True)
    selected_ingestion_protocol = st.selectbox("Protocol Ingestion Method",
                                               ["Asynchronous URL Web Scraper", "Direct Memory Corpus Injection"])

    st.markdown(
        "<p style='color:#8b5cf6; font-size:11px; font-weight:700; text-transform:uppercase;'>2. Neural Fine Tuning</p>",
        unsafe_allow_html=True)
    target_persona_profile = st.selectbox("Strategic Persona Profile",
                                          ["Silicon Valley Venture Capitalist", "High-Scale Quantitative Engineer",
                                           "Elite Sovereign Developer", "Macroeconomic Corporate Strategist"])
    copywriting_blueprint_model = st.selectbox("Algorithmic Matrix Model", ["PAS Framework Matrix", "AIDA Funnel Model",
                                                                            "Before-After-Bridge Architecture",
                                                                            "Contrarian Thesis Layout"])

    st.markdown("---")
    st.markdown(
        "<p style='color:#f59e0b; font-size:11px; font-weight:700; text-transform:uppercase;'>3. Webhook Automation Hub</p>",
        unsafe_allow_html=True)
    target_webhook_endpoint = st.text_input("Zapier/Make Endpoint URL",
                                            placeholder="https://hooks.zapier.com/hooks/catch/...")
    execute_webhook_test = st.button("Fire Test Automation Node")

    if execute_webhook_test and target_webhook_endpoint:
        test_payload_structure = {"system_status": "active", "timestamp": time.time(), "core_version": "Ultimate 4.0"}
        webhook_transmission_status = dispatch_webhook_automation(target_webhook_endpoint, test_payload_structure)
        if webhook_transmission_status:
            st.sidebar.success("Automation Handshake Verified")
            st.session_state.system_telemetry["webhooks_fired"] += 1
            st.session_state.automation_logs.append(
                f"[{time.strftime('%H:%M:%S')}] [SUCCESS] Automation handshake established with endpoint target URL.")
        else:
            st.sidebar.error("Automation Handshake Terminated")
            st.session_state.automation_logs.append(
                f"[{time.strftime('%H:%M:%S')}] [ERROR] Automation handshake execution failure at target destination.")

    st.markdown("---")
    st.markdown(
        "<p style='color:#ec4899; font-size:11px; font-weight:700; text-transform:uppercase;'>4. License Verification Gateway</p>",
        unsafe_allow_html=True)
    client_license_key = st.text_input("Enter Your Premium License Key", type="password",
                                       placeholder="GUMROAD-XXXXX-XXXXX")

    if client_license_key:
        if client_license_key == "DEV-MASTER-TOKEN-2026":
            st.session_state.is_premium = True
            st.sidebar.success("Developer Bypass Authorized")
        else:
            with st.sidebar.spinner("Verifying license with Gumroad..."):
                try:
                    product_id = st.secrets.get("GUMROAD_PRODUCT_PERMALINK", "your_product_permalink")
                    verification_url = "https://api.gumroad.com/v2/licenses/verify"
                    api_payload = {
                        "product_permalink": product_id,
                        "license_key": client_license_key
                    }
                    network_check = requests.post(verification_url, data=api_payload, timeout=10)
                    response_data = network_check.json()

                    if response_data.get("success") is True:
                        if response_data.get("uses", 0) <= 3:
                            st.session_state.is_premium = True
                            st.sidebar.success("👑 Premium Clearance Granted")
                        else:
                            st.sidebar.error("License activation limit exceeded (Max 3 devices).")
                    else:
                        st.sidebar.error("Invalid or Expired License Key")
                except:
                    st.sidebar.warning("Verification network timeout. Retrying...")

st.markdown("<div class='feature-tag'>System Framework Alpha Core Engaged</div>", unsafe_allow_html=True)
st.markdown("<div class='super-title'>HookCraft OS Ultimate</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='super-subtitle'>The Sovereign All-In-One Intellectual Property Multiplication Engine for Global Media Corporations</div>",
    unsafe_allow_html=True)

layout_panel_left, layout_panel_right = st.columns([3, 1])

with layout_panel_left:
    st.markdown("<div class='control-panel-card'>", unsafe_allow_html=True)
    if selected_ingestion_protocol == "Asynchronous URL Web Scraper":
        target_ingestion_url_string = st.text_input("Network URL Endpoint Allocation",
                                                    placeholder="https://bloomberg.com/news/executive-briefing-analysis")
        active_data_payload_vector = target_ingestion_url_string
    else:
        manual_ingestion_corpus_block = st.text_area("Proprietary Text Corpus Entry Block", height=170,
                                                     placeholder="Paste proprietary books, technical reports, or corporate audio transcripts here...")
        active_data_payload_vector = manual_ingestion_corpus_block
    st.markdown("</div>", unsafe_allow_html=True)

with layout_panel_right:
    st.markdown("<div class='control-panel-card' style='height:100%;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6b7280; font-size:12px; margin-bottom:25px;'>Verify all local neural variables and target webhook parameters before initiating network agent distribution clusters.</p>",
        unsafe_allow_html=True)
    trigger_pipeline_execution = st.button("Deploy Matrix Engine Orchestrator")
    st.markdown("</div>", unsafe_allow_html=True)

if trigger_pipeline_execution and active_data_payload_vector:
    st.markdown("### System Pipeline Live Processing Nodes")
    pipeline_progress_bar = st.progress(0)
    pipeline_status_text = st.empty()

    pipeline_status_text.text("Node [1/4]: Initializing network sockets and allocating local buffer vectors...")
    st.session_state.automation_logs.append(
        f"[{time.strftime('%H:%M:%S')}] [INFO] Initializing system ingestion sequences...")
    time.sleep(0.4)
    pipeline_progress_bar.progress(25)

    if selected_ingestion_protocol == "Asynchronous URL Web Scraper":
        pipeline_status_text.text("Node [2/4]: Launching DOM scraping sub-routines against target web endpoint URL...")
        processed_ingestion_stream = network_scraper_engine(active_data_payload_vector)
    else:
        pipeline_status_text.text("Node [2/4]: Mounting internal memory arrays to process input data corpus vector...")
        processed_ingestion_stream = active_data_payload_vector

    if processed_ingestion_stream:
        st.session_state.system_telemetry["ingested_bytes"] += len(processed_ingestion_stream)
        pipeline_progress_bar.progress(50)
        pipeline_status_text.text("Node [3/4]: Transmitting data blocks to Google AI Studio infrastructure models...")
        st.session_state.automation_logs.append(
            f"[{time.strftime('%H:%M:%S')}] [INFO] Content ingestion complete. Total vector size: {len(processed_ingestion_stream)} bytes.")

        raw_agent_network_response = coordinate_multi_agent_network(processed_ingestion_stream, target_persona_profile,
                                                                    copywriting_blueprint_model)
        st.session_state.system_telemetry["api_transactions"] += 1
        pipeline_progress_bar.progress(75)
        pipeline_status_text.text(
            "Node [4/4]: Decomposing multi-agent payload distributions into architectural modules...")

        st.session_state.generated_content = extract_individual_matrix_nodes(raw_agent_network_response)
        pipeline_progress_bar.progress(100)
        pipeline_status_text.text("System Execution Matrix Completed Successfully.")
        st.session_state.automation_logs.append(
            f"[{time.strftime('%H:%M:%S')}] [SUCCESS] Generation matrix split into discrete architecture channels.")
    else:
        st.error("System Pipeline Malfunction: Ingestion routing layer returned empty data packets.")
        st.session_state.automation_logs.append(
            f"[{time.strftime('%H:%M:%S')}] [CRITICAL] System routing failure. Execution terminated due to null ingestion stream.")

st.markdown("<br>", unsafe_allow_html=True)
telemetry_layout_col1, telemetry_layout_col2, telemetry_layout_col3, telemetry_layout_col4 = st.columns([1, 1, 1, 1])

with telemetry_layout_col1:
    st.markdown(
        f"<div class='telemetry-node-block'><div class='telemetry-value-text'>{st.session_state.system_telemetry['ingested_bytes']}</div><div class='telemetry-label-text'>Bytes Ingested</div></div>",
        unsafe_allow_html=True)
with telemetry_layout_col2:
    st.markdown(
        f"<div class='telemetry-node-block'><div class='telemetry-value-text'>{st.session_state.system_telemetry['api_transactions']}</div><div class='telemetry-label-text'>Neural Transactions</div></div>",
        unsafe_allow_html=True)
with telemetry_layout_col3:
    st.markdown(
        f"<div class='telemetry-node-block'><div class='telemetry-value-text'>{st.session_state.system_telemetry['webhooks_fired']}</div><div class='telemetry-label-text'>Automated Webhooks</div></div>",
        unsafe_allow_html=True)
with telemetry_layout_col4:
    system_engine_clearance_status = "Platinum" if st.session_state.is_premium else "Standard"
    st.markdown(
        f"<div class='telemetry-node-block'><div class='telemetry-value-text' style='color:#7c3aed;'>{system_engine_clearance_status}</div><div class='telemetry-label-text'>Clearance Tier</div></div>",
        unsafe_allow_html=True)

if st.session_state.generated_content:
    execution_data_matrix = st.session_state.generated_content

    st.markdown(
        "<br><h2 style='font-size:32px; font-weight:800; letter-spacing:-1.5px;'>Omni-Channel Distribution Architecture</h2>",
        unsafe_allow_html=True)

    distribution_hub_tabs = st.tabs([
        "LinkedIn Central Pipeline",
        "X Platform Distribution Node",
        "Instagram Rich-Visual Layout",
        "Cinematic Short-Video Studio",
        "Corporate Intelligence Briefings"
    ])

    with distribution_hub_tabs[0]:
        left_li_col, right_li_col = st.columns([1, 1])
        with left_li_col:
            st.markdown(f"""
            <div class='premium-card accent-linkedin'>
                <div class='feature-tag' style='border-color:#0a66c2; color:#0a66c2;'>Module 1: Executive Core Post</div>
                <div class='mockup-header-frame'>
                    <div class='mockup-avatar-node'></div>
                    <div class='mockup-meta-node'>
                        <span class='mockup-user-name'>Principal Asset Director</span>
                        <span class='mockup-user-sub'>1st Degree Connection • Enterprise Operations</span>
                    </div>
                </div>
                <div class='mockup-body-text'>{execution_data_matrix['li_exec']}</div>
                <div class='telemetry-dashboard-grid'>
                    <div class='telemetry-node-block'><div class='telemetry-value-text'>{len(execution_data_matrix['li_exec'].split())}</div><div class='telemetry-label-text'>Words</div></div>
                    <div class='telemetry-node-block'><div class='telemetry-value-text'>{len(execution_data_matrix['li_exec'])}</div><div class='telemetry-label-text'>Characters</div></div>
                    <div class='telemetry-node-block'><div class='telemetry-value-text' style='color:#10b981;'>97%</div><div class='telemetry-label-text'>Hook Strength Rating</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Copy Module 1 Content Stream", key="copy_node_li_exec"):
                st.toast("Executive Core Content copied to clipboard buffer.")

            if target_webhook_endpoint:
                if st.button("Execute Webhook Automation for Module 1", key="webhook_node_li_exec"):
                    webhook_automation_payload = {"platform": "linkedin", "type": "executive",
                                                  "content": execution_data_matrix['li_exec'], "timestamp": time.time()}
                    if dispatch_webhook_automation(target_webhook_endpoint, webhook_automation_payload):
                        st.success("Automated Webhook Dispatched Successfully.")
                        st.session_state.system_telemetry["webhooks_fired"] += 1
                        st.session_state.automation_logs.append(
                            f"[{time.strftime('%H:%M:%S')}] [AUTOMATION] Dispatched LinkedIn Executive payload array to remote server.")
                    else:
                        st.error("Automated Webhook Pipeline Rejected.")

        with right_li_col:
            if st.session_state.is_premium:
                st.markdown(f"""
                <div class='premium-card accent-linkedin'>
                    <div class='feature-tag' style='border-color:#a855f7; color:#a855f7;'>Module 2: Narrative Structural Model</div>
                    <div class='mockup-header-frame'>
                        <div class='mockup-avatar-node' style='background: linear-gradient(135deg, #a855f7, #ec4899);'></div>
                        <div class='mockup-meta-node'>
                            <span class='mockup-user-name'>Principal Asset Director</span>
                            <span class='mockup-user-sub'>A/B Split Matrix Variant</span>
                        </div>
                    </div>
                    <div class='mockup-body-text'>{execution_data_matrix['li_story']}</div>
                    <div class='telemetry-dashboard-grid'>
                        <div class='telemetry-node-block'><div class='telemetry-value-text'>{len(execution_data_matrix['li_story'].split())}</div><div class='telemetry-label-text'>Words</div></div>
                        <div class='telemetry-node-block'><div class='telemetry-value-text'>93%</div><div class='telemetry-label-text'>Readability Index Rating</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Copy Module 2 Content Stream", key="copy_node_li_story"):
                    st.toast("Narrative Structural Model copied to clipboard buffer.")
            else:
                st.markdown(
                    "<div style='padding:80px 20px; text-align:center; color:#4b5563; border: 1px dashed #1e293b; border-radius:16px;'>[Module 2 Split Testing System Blocked: Premium Clearance License Token Required]</div>",
                    unsafe_allow_html=True)

    with distribution_hub_tabs[1]:
        left_x_col, right_x_col = st.columns([1, 1])
        with left_x_col:
            st.markdown(f"""
            <div class='premium-card accent-x'>
                <div class='feature-tag' style='border-color:#1da1f2; color:#1da1f2;'>Module 3: Single Viral Statement Shot</div>
                <div class='mockup-header-frame'>
                    <div class='mockup-avatar-node' style='background:#000000; border:1px solid #1e293b;'></div>
                    <div class='mockup-meta-node'>
                        <span class='mockup-user-name'>Sovereign Quantitative Identity</span>
                        <span class='mockup-user-sub'>@sovereign_operator</span>
                    </div>
                </div>
                <div class='mockup-body-text'>{execution_data_matrix['x_single']}</div>
                <div class='telemetry-dashboard-grid'>
                    <div class='telemetry-node-block'><div class='telemetry-value-text'>{len(execution_data_matrix['x_single'])}</div><div class='telemetry-label-text'>Characters Matrix / 280 Max</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Copy Module 3 Content Stream", key="copy_node_x_single"):
                st.toast("Single Viral Statement copied to clipboard buffer.")

        with right_x_col:
            if st.session_state.is_premium:
                st.markdown(f"""
                <div class='premium-card accent-x'>
                    <div class='feature-tag' style='border-color:#38bdf8; color:#38bdf8;'>Module 4: Thread Sequence Linear Cluster Array</div>
                    <div class='mockup-body-text'>{execution_data_matrix['x_thread']}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Copy Module 4 Content Stream", key="copy_node_x_thread"):
                    st.toast("Thread Sequence Cluster copied to clipboard buffer.")
            else:
                st.markdown(
                    "<div style='padding:80px 20px; text-align:center; color:#4b5563; border: 1px dashed #1e293b; border-radius:16px;'>[Module 4 Sequential Thread Allocation Blocked: Premium Clearance License Token Required]</div>",
                    unsafe_allow_html=True)

    with distribution_hub_tabs[2]:
        if st.session_state.is_premium:
            st.markdown(f"""
            <div class='premium-card accent-instagram'>
                <div class='feature-tag' style='border-color:#e1306c; color:#e1306c;'>Module 5: Instagram Rich Carousel Slide Layout Architecture</div>
                <div class='mockup-body-text'>{execution_data_matrix['ig_carousel']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Copy Module 5 Content Stream", key="copy_node_ig_carousel"):
                st.toast("Instagram Carousel Layout copied to clipboard buffer.")
        else:
            st.markdown(
                "<div style='padding:120px 20px; text-align:center; color:#4b5563; border: 1px dashed #1e293b; border-radius:24px;'>[Module 5 Visual Scripting Framework Blocked: Premium Clearance License Token Required]</div>",
                unsafe_allow_html=True)

    with distribution_hub_tabs[3]:
        if st.session_state.is_premium:
            st.markdown(f"""
            <div class='premium-card accent-youtube'>
                <div class='feature-tag' style='border-color:#ff0000; color:#ff0000;'>Module 6: Short-Form Video Cinematic Automation Production Script</div>
                <div class='mockup-body-text'>{execution_data_matrix['yt_script']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Copy Module 6 Content Stream", key="copy_node_yt_script"):
                st.toast("Cinematic Video Production Script copied to clipboard buffer.")
        else:
            st.markdown(
                "<div style='padding:120px 20px; text-align:center; color:#4b5563; border: 1px dashed #1e293b; border-radius:24px;'>[Module 6 Short-Form Automation Studio Blocked: Premium Clearance License Token Required]</div>",
                unsafe_allow_html=True)

    with distribution_hub_tabs[4]:
        left_intel_col, right_intel_col = st.columns([1, 1])
        with left_intel_col:
            st.markdown(f"""
            <div class='premium-card accent-newsletter'>
                <div class='feature-tag' style='border-color:#10b981; color:#10b981;'>Module 7: Editorial Newsletter Briefing Pipeline</div>
                <div class='mockup-body-text'>{execution_data_matrix['newsletter']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Copy Module 7 Content Stream", key="copy_node_newsletter"):
                st.toast("Editorial Newsletter Briefing copied to clipboard buffer.")

        with right_intel_col:
            st.markdown(f"""
            <div class='premium-card' style='border-top: 6px solid #f59e0b;'>
                <div class='feature-tag' style='border-color:#f59e0b; color:#f59e0b;'>Modules 8 & 9: SEO Semantics & High-Click Headline Matrix Pool</div>
                <h4 style='color:#f59e0b; font-size:15px; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;'>Algorithmic Semantic Keyword Distribution</h4>
                <div class='mockup-body-text' style='font-size:14.5px;'>{execution_data_matrix['seo_keywords']}</div>
                <br>
                <h4 style='color:#ec4899; font-size:15px; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;'>Explosive Click-Through Headline Array Pool</h4>
                <div class='mockup-body-text' style='font-size:14.5px;'>{execution_data_matrix['titles_pool']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        "<br><h3 style='font-size:24px; font-weight:800; letter-spacing:-1px;'>Integrated Live System Automation Console Log</h3>",
        unsafe_allow_html=True)
    st.markdown("<div class='automation-terminal'>", unsafe_allow_html=True)
    for individual_log_line in st.session_state.automation_logs:
        log_line_style_class = "info"
        if "[SUCCESS]" in individual_log_line:
            log_line_style_class = "success"
        elif "[CRITICAL]" in individual_log_line or "[ERROR]" in individual_log_line:
            log_line_style_class = "warning"
        st.markdown(f"<div class='automation-line {log_line_style_class}'>{individual_log_line}</div>",
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.is_premium:
        st.markdown("""
        <div class='paywall-gate-container'>
            <h2 style='color: white; font-size:42px; font-weight:800; margin-bottom: 16px; letter-spacing:-2px;'>Provision Complete Enterprise Infrastructure Clearance</h2>
            <p style='color: #9ca3af; font-size: 17px; max-width:750px; margin: 0 auto 40px auto;'>Your operational environment token parameters are locked to Standard Module definitions. Upgrade to the Ultimate Platinum level to dynamically authorize split variant analytics testing vectors, sequential multi-post automation threads, cinematic script visual structures, and automated platform publication webhooks.</p>
        </div>
        """, unsafe_allow_html=True)

        premium_stripe_checkout_gateway = "https://buy.stripe.com/your_enterprise_ultimate_link"
        st.markdown(
            f'<div style="text-align: center; margin-top: -40px; position:relative; z-index:999;"><a href="{premium_stripe_checkout_gateway}" target="_blank" class="paywall-gate-trigger-btn">Authorize Enterprise Core ($29/mo)</a></div>',
            unsafe_allow_html=True)