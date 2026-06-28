import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json
import datetime
import base64
import time
import random
import os

# ==========================================
# 1. SETUP & BRANDING CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Flashpoint Finds - Premium Comic Inspection Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom neon CSS styles for professional theme
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
        color: #ffffff;
    }
    h1, h2, h3, h4 {
        font-family: 'Oswald', sans-serif !important;
    }
    .stButton>button {
        background-color: #D32F2F !important;
        color: white !important;
        border: 1px solid #B71C1C !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    .stButton>button:hover {
        background-color: #B71C1C !important;
        box-shadow: 0 0 10px #D32F2F !important;
    }
</style>
""", unsafe_allow_html=True)

# Map official grading steps
GRADES_MAP = {
    10.0: "GM (Gem Mint)", 9.9: "MT (Mint)", 9.8: "NM/M (Near Mint/Mint)",
    9.6: "NM+ (Near Mint+)", 9.4: "NM (Near Mint)", 9.2: "NM- (Near Mint-)",
    9.0: "VF/NM (Very Fine/Near Mint)", 8.5: "VF+ (Very Fine+)", 8.0: "VF (Very Fine)",
    7.5: "VF- (Very Fine-)", 7.0: "FN/VF (Fine/Very Fine)", 6.5: "FN+ (Fine+)",
    6.0: "FN (Fine)", 5.5: "FN- (Fine-)", 5.0: "VG/FN (Very Good/Fine)",
    4.5: "VG+ (Very Good+)", 4.0: "VG (Very Good)", 3.5: "VG- (Very Good-)",
    3.0: "GD/VG (Good/Very Good)", 2.5: "GD (Good)", 2.0: "GD- (Good-)",
    1.5: "FR/GD (Fair/Good)", 1.0: "FR (Fair)", 0.5: "PR (Poor)"
}

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "comic_data" not in st.session_state:
    st.session_state.comic_data = {
        "title": "The Flash",
        "issue": "139",
        "publisher": "DC Comics",
        "year": "1963",
        "artist": "Carmine Infantino",
        "price": "12¢",
        "keyLevel": "Major Key Issues",
        "significance": "First appearance of Professor Zoom (Eobard Thawne / Reverse-Flash). Origin of Professor Zoom. Classic silver-age milestone.",
        "trivia": "One of the most valuable Flash silver age books. Print runs were standard for the early 60s, highly sought-after collectible.",
        "impact": 9,
        "cover": 8,
        "divergence": 9,
        "investmentTier": "Blue Chip Key",
        "arbitrage": "1.8x CGC Slab Premium",
        "liquidity": "Liquid A+",
        "horizon": "Legacy Hold",
        "spine": 0.0,
        "spineroll": 0.0,
        "splits": 0.0,
        "gloss": 0.0,
        "corners": 0.0,
        "stains": 0.0,
        "writing": 0.0,
        "staples": 0.0,
        "detachment": 0.0,
        "pagecolor": 0.0,
        "missing": 0.0,
        "character": "Reverse-Flash, Barry Allen",
        "team": "Justice League of America",
        "universe": "DC Universe",
        "genre": "Superheroes",
        "story": "Menace of the Reverse-Flash!",
        "writer": "John Broome",
        "format": "Single Issue",
        "type": "Comic Book",
        "tradition": "US Comics",
        "variant": "Standard Cover",
        "style": "Color",
        "language": "English",
        "country": "United States",
        "audience": "General Audience",
        "features": "1st Edition, Key Issue, Origin Story",
        "upc": "Does Not Apply",
        "grader": "Flashpoint Finds",
        "cert": "FF139902026",
        "signed": "No",
        "signedby": "",
        "auth": "None",
        "authnum": "",
        "inscribed": "No",
        "personalized": "No",
        "saleunit": "Single Unit",
        "convention": "None",
        "unitqty": "1",
        "unittype": "Unit",
        "prop65": "No Warning Applicable",
        "notes": "Comic book is flat, complete and solid. Corner structures are relatively sharp. Back cover presents high surface gloss."
    }

# ==========================================
# 3. SIDEBAR BRANDING & CREDENTIALS
# ==========================================
with st.sidebar:
    # Defensively load the logo file to prevent runtime crashes if missing on GitHub
    logo_filename = "logo.png"
    fallback_logo_filename = "Flashpoint Finds (5).png"
    
    if os.path.exists(logo_filename):
        st.image(logo_filename, caption="Flashpoint Finds LLC Verification Hub", use_container_width=True)
    elif os.path.exists(fallback_logo_filename):
        st.image(fallback_logo_filename, caption="Flashpoint Finds LLC Verification Hub", use_container_width=True)
    else:
        # Fallback text-badge in case of upload discrepancy
        st.markdown("""
        <div style="background: linear-gradient(135deg, #B71C1C, #121212); padding: 15px; border-radius: 8px; border: 2px solid #D32F2F; text-align: center; margin-bottom: 15px;">
            <span style="font-family: 'Oswald', sans-serif; font-size: 20px; font-weight: bold; color: #ffffff; letter-spacing: 2px;">⚡ FLASHPOINT FINDS</span>
            <span style="font-size: 9px; color: #aaa; display: block; margin-top: 5px; text-transform: uppercase;">Verification Hub</span>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 Pro-Tip: Rename your brand logo to 'logo.png' and upload it to the root of your GitHub repository to display it here.")

    st.markdown("---")
    st.markdown("### ⚡ API Authentication Portal")
    
    # Check Streamlit secrets first, else fallback to manual input
    secret_key = st.secrets.get("GEMINI_API_KEY", "")
    if secret_key:
        st.success("API Key Loaded from Chrono-Secrets!")
        api_key = secret_key
    else:
        api_key = st.text_input("Enter Gemini API Key", type="password", help="Input your Google AI Studio key to enable Web Chrono-Pulls.")
        
    st.markdown("---")
    st.markdown("### 📝 Quick Calibration Presets")
    if st.button("Set Barry Allen Signature"):
        st.session_state.comic_data["signed"] = "Yes"
        st.session_state.comic_data["signedby"] = "Carmine Infantino"
        st.session_state.comic_data["auth"] = "PSA/DNA"
        st.session_state.comic_data["authnum"] = "FF-BALLEN-842"
        st.rerun()

# ==========================================
# 4. CHRONO-ENGINE API RUNNERS
# ==========================================
def call_gemini_with_backoff(prompt, images=None):
    if not api_key:
        st.warning("Please configure your Gemini API Key in the sidebar or secrets manager to execute automated runs.")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    
    # Configure precise JSON enforcement
    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING"},
                "issue": {"type": "STRING"},
                "publisher": {"type": "STRING"},
                "year": {"type": "STRING"},
                "artist": {"type": "STRING"},
                "price": {"type": "STRING"},
                "keyLevel": {"type": "STRING"},
                "significance": {"type": "STRING"},
                "trivia": {"type": "STRING"},
                "character": {"type": "STRING"},
                "team": {"type": "STRING"},
                "universe": {"type": "STRING"},
                "genre": {"type": "STRING"},
                "story": {"type": "STRING"},
                "writer": {"type": "STRING"},
                "variant": {"type": "STRING"},
                "features": {"type": "STRING"},
                "story_impact": {"type": "NUMBER"},
                "cover_desirability": {"type": "NUMBER"},
                "timeline_divergence": {"type": "NUMBER"},
                "investmentTier": {"type": "STRING"},
                "arbitrage": {"type": "STRING"},
                "liquidity": {"type": "STRING"},
                "horizon": {"type": "STRING"},
                "spine": {"type": "NUMBER"},
                "spineroll": {"type": "NUMBER"},
                "splits": {"type": "NUMBER"},
                "gloss": {"type": "NUMBER"},
                "corners": {"type": "NUMBER"},
                "stains": {"type": "NUMBER"},
                "writing": {"type": "NUMBER"},
                "staples": {"type": "NUMBER"},
                "detachment": {"type": "NUMBER"},
                "pagecolor": {"type": "NUMBER"},
                "missing": {"type": "NUMBER"},
                "notes": {"type": "STRING"}
            },
            "required": ["title", "issue", "publisher", "year"]
        }
    }

    # Assemble multimodal content list
    contents = [prompt]
    if images:
        for img in images:
            contents.append(img)

    # 5x Exponential backoff loop
    delay = 1.0
    for attempt in range(5):
        try:
            response = model.generate_content(contents, generation_config=generation_config)
            return json.loads(response.text)
        except Exception as e:
            if attempt == 4:
                st.error(f"Timeline Engine error: {str(e)}")
                return None
            time.sleep(delay + random.uniform(0.1, 0.5))
            delay *= 2.0
    return None

# ==========================================
# 5. HISTORICAL CAPSULE & STRATEGY GENERATORS
# ==========================================
def autoComputeEra(year_str):
    try:
        y = int(year_str)
    except:
        return "Modern Age (1992-Present)"
    if y < 1956: return "Golden Age (1938-1956)"
    if y >= 1956 and y < 1970: return "Silver Age (1956-1970)"
    if y >= 1970 and y < 1985: return "Bronze Age (1970-1985)"
    if y >= 1985 and y < 1992: return "Copper Age (1984-1992)"
    return "Modern Age (1992-Present)"

def autoComputeVintage(year_str):
    try:
        y = int(year_str)
        return "Yes" if y < 2000 else "No"
    except:
        return "No"

# ==========================================
# 6. APP MAIN GRID LAYOUT
# ==========================================
st.title("⚡ Flashpoint Finds Portfolio & Grader")

left_col, right_col = st.columns([7, 5])

# LEFT PANEL: INPUT INTERFACE TABS
with left_col:
    tab_id, tab_key, tab_grade, tab_ebay = st.tabs(["1. Metadata Scanner", "2. Lore & Investment", "3. Diagnostics Grading", "4. eBay Spec Assistant"])
    
    # ------------------
    # TAB 1: METADATA & SCOPE
    # ------------------
    with tab_id:
        st.subheader("⚡ Grounded Timeline Query Engine")
        web_query = st.text_input("Grounded Book Identification Search Bar", placeholder="e.g. Amazing Spider-Man 300 (1988)")
        
        # Web Search Pull Functionality
        if st.button("Initiate Chrono-Pull Search"):
            if web_query:
                with st.spinner("Querying Comic Database Records..."):
                    prompt = f"Perform a grounded web search for the comic book: '{web_query}'. Retrieve publishing details, creator names, variant configurations, key issue importance indicators, LCOG trivia, and financial diagnostics."
                    data = call_gemini_with_backoff(prompt)
                    if data:
                        st.session_state.comic_data.update(data)
                        st.success("⚡ System synchronized with grounded comic database assets!")
                        st.rerun()
            else:
                st.error("Please insert search term coordinates.")

        st.markdown("---")
        st.subheader("📸 Direct Front & Back Image Scanner")
        
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            front_file = st.file_uploader("Front Cover Upload", type=["png", "jpg", "jpeg"])
        with col_img2:
            back_file = st.file_uploader("Back Cover Upload (Optional)", type=["png", "jpg", "jpeg"])

        if st.button("Analyze Uploaded Cover Assets"):
            if front_file:
                with st.spinner("Initiating Chrono-Scan Cover Analysis..."):
                    images_to_send = []
                    # Read image files safely
                    front_bytes = front_file.read()
                    images_to_send.append({"mime_type": front_file.type, "data": front_bytes})
                    
                    if back_file:
                        back_bytes = back_file.read()
                        images_to_send.append({"mime_type": back_file.type, "data": back_bytes})

                    prompt = "Examine the covers of this comic. Extract the title, issue number, publisher, year, artist, variant type, visible cover wear deductions, and estimate historical and collection significance."
                    data = call_gemini_with_backoff(prompt, images=images_to_send)
                    if data:
                        st.session_state.comic_data.update(data)
                        st.success("⚡ Chrono-Scan Complete! Cover visual elements mapped to workspace.")
                        st.rerun()
            else:
                st.error("Front Cover image is required to initiate visual scans.")

        st.markdown("---")
        st.subheader("Manual Entry Mappings")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.session_state.comic_data["title"] = st.text_input("Series Title", st.session_state.comic_data["title"])
            st.session_state.comic_data["publisher"] = st.text_input("Publisher", st.session_state.comic_data["publisher"])
            st.session_state.comic_data["artist"] = st.text_input("Cover Artist(s)", st.session_state.comic_data["artist"])
        with col_m2:
            st.session_state.comic_data["issue"] = st.text_input("Issue Number", st.session_state.comic_data["issue"])
            st.session_state.comic_data["year"] = st.text_input("Publication Year", st.session_state.comic_data["year"])
            st.session_state.comic_data["price"] = st.text_input("Original Retail Price", st.session_state.comic_data["price"])

    # ------------------
    # TAB 2: LORE & INVESTMENT
    # ------------------
    with tab_key:
        st.subheader("🗝️ Key Category Designation")
        st.session_state.comic_data["keyLevel"] = st.selectbox(
            "Select Registry Classification Tier",
            ["Major Key Issues", "Minor Key Issues", "Iconic Cover / Variant", "Collectible Comic Book"],
            index=["Major Key Issues", "Minor Key Issues", "Iconic Cover / Variant", "Collectible Comic Book"].index(st.session_state.comic_data["keyLevel"])
        )
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.session_state.comic_data["impact"] = st.slider("Story Impact (1-10)", 1, 10, int(st.session_state.comic_data["impact"]))
        with col_s2:
            st.session_state.comic_data["cover"] = st.slider("Cover Desirability (1-10)", 1, 10, int(st.session_state.comic_data["cover"]))
        with col_s3:
            st.session_state.comic_data["divergence"] = st.slider("Timeline Divergence (1-10)", 1, 10, int(st.session_state.comic_data["divergence"]))

        st.markdown("---")
        st.subheader("📈 Portfolio Diagnostics & Arbitrage Metrics")
        col_p1, col_inv2 = st.columns(2)
        with col_p1:
            st.session_state.comic_data["investmentTier"] = st.selectbox(
                "Asset Investment Classification Category",
                ["Blue Chip Key", "Emerging Classic", "Speculative Growth", "Historical Core"],
                index=["Blue Chip Key", "Emerging Classic", "Speculative Growth", "Historical Core"].index(st.session_state.comic_data["investmentTier"])
            )
            st.session_state.comic_data["liquidity"] = st.selectbox(
                "Liquidity Velocity Score",
                ["Liquid A+", "Strong B", "Niche C"],
                index=["Liquid A+", "Strong B", "Niche C"].index(st.session_state.comic_data["liquidity"])
            )
        with col_inv2:
            st.session_state.comic_data["arbitrage"] = st.text_input("CGC Slab Arbitrage Multiplier Premium", st.session_state.comic_data["arbitrage"])
            st.session_state.comic_data["horizon"] = st.selectbox(
                "Target Holding Horizon Strategy",
                ["Legacy Hold", "Strategic Accumulate", "Flip Target"],
                index=["Legacy Hold", "Strategic Accumulate", "Flip Target"].index(st.session_state.comic_data["horizon"])
            )

        st.markdown("---")
        st.session_state.comic_data["significance"] = st.text_area("Key Significance Highlights", st.session_state.comic_data["significance"])
        st.session_state.comic_data["trivia"] = st.text_area("LCOG Trivia & Milestones", st.session_state.comic_data["trivia"])

    # ------------------
    # TAB 3: GRADING MATRIX
    # ------------------
    with tab_grade:
        st.subheader("🔍 Deep-Dive Deduction Calibration Matrix")
        
        # Setup options
        options_gloss = {
            "0.0": ("High Brilliant Gloss / Mirror-like", 10.0),
            "-0.2": ("Slight Reduction / Minor Surface Scuffs", 9.2),
            "-1.0": ("Moderate Gloss / Light Creasing", 7.5),
            "-2.5": ("Dull finish / Dimpling & Creasing", 5.5),
            "-4.0": ("Heavy Wear / Flat / Large Creases", 4.0)
        }
        options_corners = {
            "0.0": ("Sharp, clean corners", 10.0),
            "-0.2": ("Minor blunting on 1-2 corners", 9.4),
            "-0.6": ("Moderate blunting on multiple corners", 8.0),
            "-1.5": ("Severe rounding / Minor chew or corner loss", 5.0)
        }
        options_stains = {
            "0.0": ("None", 10.0),
            "-0.4": ("Minor dust shadow / Tiny watermark", 9.0),
            "-1.5": ("Moderate staining / Foxing present", 6.5),
            "-3.5": ("Major water damage / Staining", 3.5)
        }
        options_writing = {
            "0.0": ("None", 10.0),
            "-0.2": ("Small pencil price / Arrival date stamp", 9.4),
            "-1.5": ("Large ink signature / Price mark", 7.0)
        }
        options_spine = {
            "0.0": ("0 stress lines", 10.0),
            "-0.2": ("1-2 minor stress lines", 9.6),
            "-0.5": ("3-4 stress lines", 9.0),
            "-1.2": ("5-9 stress lines", 8.0),
            "-2.5": ("10+ stress lines / spine wear", 6.0)
        }
        options_roll = {
            "0.0": ("Perfect / Flat", 10.0),
            "-0.4": ("Minor spine roll", 9.0),
            "-1.5": ("Moderate spine roll", 7.0),
            "-3.0": ("Major / Severe spine roll", 4.0)
        }
        options_splits = {
            "0.0": ("None", 10.0),
            "-1.5": ("Spine split under 0.5 inches", 4.0),
            "-3.5": ("Spine split over 1 inch", 2.5)
        }
        options_rust = {
            "0.0": ("Clean / No rust", 10.0),
            "-0.2": ("Minor staple tarnish", 8.5),
            "-1.0": ("Moderate rust on staples", 5.5),
            "-2.5": ("Rusty staples with migration staining", 3.5)
        }
        options_detachment = {
            "0.0": ("Fully Attached", 10.0),
            "-1.0": ("Staple tear present", 5.5),
            "-3.0": ("Cover detached at one staple", 3.0),
            "-5.0": ("Cover completely detached", 1.5)
        }
        options_pagecolor = {
            "0.0": ("White Pages", 10.0),
            "-0.2": ("Off-White to White", 9.4),
            "-0.5": ("Off-White Pages", 8.0),
            "-1.5": ("Cream Pages", 5.5),
            "-3.0": ("Tan Pages", 3.5),
            "-6.0": ("Brittle / Chipping edges", 1.0)
        }
        options_missing = {
            "0.0": ("None / 100% Intact", 10.0),
            "-3.0": ("Coupon cutout present", 1.5),
            "-8.0": ("Story page removed", 0.5)
        }

        # Helper select builder
        def create_deduct_select(label, options_dict, current_val_key):
            keys_list = list(options_dict.keys())
            idx = 0
            curr_str = f"{float(current_val_key):.1f}" if "-" in str(current_val_key) or float(current_val_key) != 0.0 else f"{float(current_val_key):.1f}"
            for i, k in enumerate(keys_list):
                if f"{float(k):.1f}" == curr_str:
                    idx = i
                    break
            sel = st.selectbox(label, keys_list, format_func=lambda x: f"{options_dict[x][0]} ({x})", index=idx)
            return float(sel), options_dict[sel][1], options_dict[sel][0]

        st.markdown("#### 1. Cover & Corners")
        g_gloss_ded, g_gloss_cap, g_gloss_lbl = create_deduct_select("Cover Gloss Level", options_gloss, st.session_state.comic_data["gloss"])
        g_corners_ded, g_corners_cap, g_corners_lbl = create_deduct_select("Corner Wear Level", options_corners, st.session_state.comic_data["corners"])
        g_stains_ded, g_stains_cap, g_stains_lbl = create_deduct_select("Water Damage / Staining", options_stains, st.session_state.comic_data["stains"])
        g_writing_ded, g_writing_cap, g_writing_lbl = create_deduct_select("Writing / Price Stamps on Cover", options_writing, st.session_state.comic_data["writing"])

        st.markdown("#### 2. Spine & Binding")
        g_spine_ded, g_spine_cap, g_spine_lbl = create_deduct_select("Color-Breaking Spine Stress (Count)", options_spine, st.session_state.comic_data["spine"])
        g_roll_ded, g_roll_cap, g_roll_lbl = create_deduct_select("Spine Roll Level", options_roll, st.session_state.comic_data["spineroll"])
        g_splits_ded, g_splits_cap, g_splits_lbl = create_deduct_select("Spine Splits", options_splits, st.session_state.comic_data["splits"])
        g_rust_ded, g_rust_cap, g_rust_lbl = create_deduct_select("Staple Rust & Migration", options_rust, st.session_state.comic_data["staples"])
        g_detach_ded, g_detach_cap, g_detach_lbl = create_deduct_select("Cover Detachment Status", options_detachment, st.session_state.comic_data["detachment"])

        st.markdown("#### 3. Interior Pages & Color")
        g_color_ded, g_color_cap, g_color_lbl = create_deduct_select("Interior Page Color", options_pagecolor, st.session_state.comic_data["pagecolor"])
        g_missing_ded, g_missing_cap, g_missing_lbl = create_deduct_select("Coupon Cutouts / Missing Pages", options_missing, st.session_state.comic_data["missing"])

        # Calculations
        tot_deduct = g_gloss_ded + g_corners_ded + g_stains_ded + g_writing_ded + g_spine_ded + g_roll_ded + g_splits_ded + g_rust_ded + g_detach_ded + g_color_ded + g_missing_ded
        raw_calc_score = 10.0 + tot_deduct
        lowest_cap = min(g_gloss_cap, g_corners_cap, g_stains_cap, g_writing_cap, g_spine_cap, g_roll_cap, g_splits_cap, g_rust_cap, g_detach_cap, g_color_cap, g_missing_cap)
        final_score = max(0.5, min(raw_calc_score, lowest_cap))

        # Map rounded grade scale
        rounded_official = 0.5
        for step in sorted(list(GRADES_MAP.keys()), reverse=True):
            if final_score >= step:
                rounded_official = step
                break

        # Sync calculations to session memory
        st.session_state.comic_data.update({
            "gloss": g_gloss_ded,
            "corners": g_corners_ded,
            "stains": g_stains_ded,
            "writing": g_writing_ded,
            "spine": g_spine_ded,
            "spineroll": g_roll_ded,
            "splits": g_splits_ded,
            "staples": g_rust_ded,
            "detachment": g_detach_ded,
            "pagecolor": g_color_ded,
            "missing": g_missing_ded,
            "final_grade_num": rounded_official,
            "final_grade_str": GRADES_MAP[rounded_official]
        })

        st.session_state.comic_data["notes"] = st.text_area("Grader Inspection Notes", st.session_state.comic_data["notes"])

    # ------------------
    # TAB 4: EBAY ASSISTANT
    # ------------------
    with tab_ebay:
        st.subheader("⚡ 37-Field eBay Spec configuration")
        st.session_state.comic_data["character"] = st.text_input("Character(s) List", st.session_state.comic_data["character"])
        st.session_state.comic_data["team"] = st.text_input("Superhero Team Alliance", st.session_state.comic_data["team"])
        st.session_state.comic_data["universe"] = st.text_input("Fiction Universe Setup", st.session_state.comic_data["universe"])
        st.session_state.comic_data["story"] = st.text_input("Story Arc / Title", st.session_state.comic_data["story"])
        st.session_state.comic_data["writer"] = st.text_input("Writer Credit", st.session_state.comic_data["writer"])
        st.session_state.comic_data["features"] = st.text_input("Features/Identifiers", st.session_state.comic_data["features"])
        st.session_state.comic_data["upc"] = st.text_input("UPC Identifier Code", st.session_state.comic_data["upc"])
        st.session_state.comic_data["signed"] = st.selectbox("Is Autographed?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state.comic_data["signed"]))
        
        if st.session_state.comic_data["signed"] == "Yes":
            st.session_state.comic_data["signedby"] = st.text_input("Autographed By", st.session_state.comic_data["signedby"])
            st.session_state.comic_data["auth"] = st.text_input("Authentication Service Company", st.session_state.comic_data["auth"])
            st.session_state.comic_data["authnum"] = st.text_input("Cert/Authentication Serial Number", st.session_state.comic_data["authnum"])

# ==========================================
# 7. RIGHT PANEL: PREMIUM CARD RENDERING DESK
# ==========================================
with right_col:
    st.subheader("⚡ Dynamic Chrono-Deck Preview")
    
    # Calculate Era/Vintage automatically
    computed_era = autoComputeEra(st.session_state.comic_data["year"])
    computed_vintage = autoComputeVintage(st.session_state.comic_data["year"])
    
    grade_num_val = st.session_state.comic_data.get("final_grade_num", 9.0)
    grade_str_val = st.session_state.comic_data.get("final_grade_str", "Very Fine/Near Mint")
    
    # Generate unique barcode text
    clean_title = st.session_state.comic_data["title"].replace(' ', '').upper()[:5]
    clean_issue = st.session_state.comic_data["issue"].zfill(3)
    clean_grade = str(grade_num_val).replace('.', '')
    barcode_string = f"FF{clean_title}{clean_issue}{clean_grade}"
    
    # Check if a custom brand logo image can be rendered on the virtual card layout
    # Use standard Base64 parsing to inject raw image directly inside iframe components
    logo_base64_str = ""
    target_logo = "logo.png" if os.path.exists("logo.png") else ("Flashpoint Finds (5).png" if os.path.exists("Flashpoint Finds (5).png") else None)
    
    if target_logo:
        try:
            with open(target_logo, "rb") as image_file:
                logo_base64_str = base64.b64encode(image_file.read()).decode()
        except Exception:
            pass

    header_logo_html = ""
    if logo_base64_str:
        header_logo_html = f'<img src="data:image/png;base64,{logo_base64_str}" style="width:40px; height:40px; border-radius:4px; object-cover: cover; border:1px solid rgba(0,242,255,0.4);" alt="Logo">'
    else:
        header_logo_html = '<div style="width:40px; height:40px; border-radius:4px; background:#D32F2F; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:18px;">⚡</div>'

    # HTML Layout injection inside components
    card_html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #151515, #0a0a0a); border: 4px solid #D32F2F; border-radius: 12px; padding: 25px; color: #ffffff; width: 440px; aspect-ratio: 5/7; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 30px rgba(0,0,0,0.5); overflow:hidden; box-sizing: border-box;">
        <div>
            <!-- Header -->
            <div style="display:flex; justify-content:space-between; align-items:start; border-bottom:2px solid #D32F2F; padding-bottom:12px; margin-bottom:15px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    {header_logo_html}
                    <div>
                        <h3 style="margin:0; font-family: 'Arial Black', Gadget, sans-serif; font-size:18px; letter-spacing:1px; color:#FFC107; line-height:1.2;">FLASHPOINT FINDS</h3>
                        <span style="font-size:9px; color:#aaa; text-transform:uppercase; font-weight:bold; letter-spacing:2px; display:block; margin-top:2px;">Verified Comic Evaluation</span>
                    </div>
                </div>
                <div style="text-align:right; font-size:9px; color:#D32F2F; font-weight:bold;">
                    FF-VERIFIED
                </div>
            </div>
            
            <!-- Book Identity -->
            <div style="margin-bottom:15px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <h2 style="margin:0; font-size:20px; font-weight:bold; text-transform:uppercase;">{st.session_state.comic_data['title']}</h2>
                    <span style="font-size:10px; font-weight:bold; background:rgba(255,193,7,0.15); border:1px solid rgba(255,193,7,0.3); color:#FFC107; padding:2px 6px; border-radius:4px;">{st.session_state.comic_data['investmentTier']}</span>
                </div>
                <div style="font-size:12px; color:#aaa; margin-top:2px;">#{st.session_state.comic_data['issue']} &bull; DC Comics ({st.session_state.comic_data['year']})</div>
            </div>
            
            <!-- Key Collector Sign -->
            <div style="margin-bottom:15px;">
                <span style="font-size:10px; font-weight:bold; color:#D32F2F; text-transform:uppercase; letter-spacing:1px;">{st.session_state.comic_data['keyLevel']}</span>
                <p style="margin:3px 0 0 0; font-size:11px; color:#ddd; line-height:1.4; background:rgba(255,255,255,0.02); border-left:2px solid #FFC107; padding-left:10px;">{st.session_state.comic_data['significance']}</p>
            </div>
            
            <!-- Diagnostics meters -->
            <div style="background: rgba(0,0,0,0.3); border:1px solid #222; padding:10px; border-radius:8px; margin-bottom:15px;">
                <span style="font-size:9px; font-weight:bold; color:#00f2ff; text-transform:uppercase; letter-spacing:1px; display:block; margin-bottom:6px;">⚡ Chrono-Diagnostics Spec</span>
                <div style="display:flex; flex-direction:column; gap:4px; font-size:10px;">
                    <div style="display:flex; justify-content:space-between;"><span>Story Impact:</span> <strong>{st.session_state.comic_data['impact']}/10</strong></div>
                    <div style="display:flex; justify-content:space-between;"><span>Cover Desirability:</span> <strong>{st.session_state.comic_data['cover']}/10</strong></div>
                    <div style="display:flex; justify-content:space-between;"><span>Timeline Divergence:</span> <strong>{st.session_state.comic_data['divergence']}/10</strong></div>
                </div>
            </div>
        </div>
        
        <!-- Bottom Signature & Grade stamp -->
        <div>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed #333; padding-top:12px; margin-bottom:10px;">
                <div style="text-align:center; background:#111; border:1px solid #222; border-radius:6px; padding:6px 12px;">
                    <span style="font-size:8px; color:#888; display:block;">GRADE</span>
                    <strong style="font-size:24px; color:#FFC107; font-family:'Arial Black';">{grade_num_val:.1f}</strong>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:9px; color:#aaa; font-weight:bold; display:block; text-transform:uppercase;">{grade_str_val}</span>
                    <span style="font-size:8px; color:#888; display:block; margin-top:2px;">Pages: {st.session_state.comic_data.get('page_quality', 'White')}</span>
                </div>
            </div>
            
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:8px; color:#555; text-transform:uppercase;">
                <span>Verified Front Plate Backer</span>
                <span style="font-family: monospace;">{barcode_string}</span>
            </div>
        </div>
    </div>
    """
    
    components.html(card_html, height=640, scrolling=False)
    
    # ------------------
    # EBAY TEXT CONSOLE DESK
    # ------------------
    st.markdown("---")
    st.subheader("📋 eBay Listing Copy desk Console")
    
    # Pre-configure calculated Listing Title
    ebay_title_string = generateEbayTitle()
    st.text_input("Calculated SEO eBay Title (Character Capped)", value=ebay_title_string, disabled=True)
    
    # Generate list block of specs
    specs_list = getEbaySpecificsList()
    specs_text = "\n".join([f"{item['name']}: {item['value']}" for item in specs_list])
    
    st.text_area("Constructed eBay 37-Specifics Pack", value=specs_text, height=180, disabled=True)
    
    st.subheader("HTML Listing Description Output")
    html_desc = generateEbayDescription()
    st.text_area("Responsive HTML Listing Code Output", value=html_desc, height=150)