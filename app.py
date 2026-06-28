import streamlit as st
import streamlit.components.v1 as components
import json
import datetime
import base64
import time
import random
import os
import requests

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

# Dynamic SVG code rendering of the Flashpoint Finds Lightning Logo
# This bypasses the local file-loading crash completely!
logo_svg_html = """
<div style="text-align: center; margin-bottom: 15px;">
    <svg viewBox="0 0 100 100" style="width: 100%; max-width: 140px; filter: drop-shadow(0 0 12px rgba(211,47,47,0.8));">
        <!-- Glowing Red Outer F Structure -->
        <path d="M 22,25 L 82,25 L 82,37 L 46,37 L 46,50 L 76,50 L 76,62 L 46,62 L 46,90 L 32,90 L 32,37 L 22,37 Z" fill="#D32F2F" />
        <path d="M 25,28 L 79,28 L 79,34 L 43,34 L 43,53 L 73,53 L 73,59 L 43,59 L 43,87 L 35,87 L 35,34 L 25,34 Z" fill="#121212" />
        <!-- White Glowing lightning bolt splitting through the center -->
        <polygon points="68,8 38,58 56,58 24,96 82,42 54,42" fill="#FFFFFF" stroke="#D32F2F" stroke-width="1.5" />
    </svg>
</div>
"""

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "comic_data" not in st.session_state:
    st.session_state.comic_data = {
        "title": "Toyman Fleer Brilliants",
        "issue": "73",
        "publisher": "Upper Deck",
        "year": "2025",
        "artist": "Fleer Art Crew",
        "price": "$5.95",
        "keyLevel": "Iconic Cover / Variant",
        "significance": "Gorgeous #73 Toyman base foil card from the lightning-fast 2025 Upper Deck Fleer Superman collection. High-gloss holographic board.",
        "trivia": "This artifact highlights Winslow Schott, the Toyman! A brilliant but twisted inventor who uses weaponized toys.",
        "impact": 7,
        "cover": 9,
        "divergence": 6,
        "investmentTier": "Emerging Classic",
        "arbitrage": "1.5x Raw Card Value",
        "liquidity": "Strong B",
        "horizon": "Strategic Accumulate",
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
        "character": "Toyman, Superman",
        "team": "Superman Rogues Gallery",
        "universe": "DC Universe",
        "genre": "Superheroes",
        "story": "Fleer Brilliants Superman Foil Set",
        "writer": "Winslow Schott",
        "format": "Single Issue",
        "type": "Trading Card",
        "tradition": "US Comics",
        "variant": "Base Foil Variant",
        "style": "Color",
        "language": "English",
        "country": "United States",
        "audience": "General Audience",
        "features": "Holographic Foil Board, Near Mint Condition",
        "upc": "Does Not Apply",
        "grader": "Flashpoint Finds",
        "cert": "FF73902025",
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
        "notes": "Pack-fresh modern foil card exhibiting high surface gloss, sharp corners, and clean edges."
    }

# ==========================================
# 3. HELPER TIMELINE UTILITIES
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

def autoGenerateHistoricalCapsule(year_str):
    try:
        y = int(year_str)
    except:
        return "This release serves as a permanent point of record within contemporary comic book history."
    
    if y >= 1938 and y < 1950:
        return f"In {y}, the Golden Age of comics was flourishing. Shipped at a standard 10¢ price point, readers witnessed early heroic archetypes and heavy pulp formatting. This preservation copy stands as a cornerstone of the earliest modern graphic narratives."
    elif y >= 1950 and y < 1956:
        return f"In {y}, the industry was transitioning from war pulp and romance toward science-fiction and horror. This volume captures the critical dawn of the silver-age transition period."
    elif y >= 1956 and y < 1970:
        return f"In {y}, the Silver Age of comics was in absolute high gear. This comic represents the zenith of iconic cosmic origins, bold cover lineart, and the establishment of the modern corporate universe hierarchies we trade today."
    elif y >= 1970 and y < 1985:
        return f"In {y}, the Bronze Age of comics began exploring darker themes, socially relevant writing, and direct market distribution. A magnificent copy from a highly transitional, raw narrative era."
    elif y >= 1985 and y < 1992:
        return f"In {y}, the Copper Age was redefining graphic design. Standard price points hovered between 75¢ and $1.00. High-quality paper stocks and dark indie writing reached new heights during this period."
    else:
        return f"In {y}, the Modern Age of comics was establishing digital printing, premium glossy cardstock covers, and limited variant tier structures. Highly desired for modern collector census metrics."

# ==========================================
# 4. EBAY FIELDS GENERATORS
# ==========================================
def generateEbayTitle():
    title = (st.session_state.get("comic_data", {}).get("title", "")).upper()
    issue = st.session_state.get("comic_data", {}).get("issue", "")
    issue_str = f"#{issue}" if issue else ""
    year = st.session_state.get("comic_data", {}).get("year", "")
    year_str = f"({year})" if year else ""
    
    grade_num = st.session_state.get("comic_data", {}).get("final_grade_num", 9.0)
    grade_str = st.session_state.get("comic_data", {}).get("final_grade_str", "Very Fine/Near Mint")
    grade_part = grade_str.split('(')[0].strip().upper() + " " + str(grade_num)
    
    character = (st.session_state.get("comic_data", {}).get("character", "")).upper()
    publisher = (st.session_state.get("comic_data", {}).get("publisher", "")).upper()
    era = autoComputeEra(year).upper()
    variant = (st.session_state.get("comic_data", {}).get("variant", "")).upper()
    
    key_info = "KEY" if st.session_state.get("comic_data", {}).get("keyLevel", "") != "Collectible Comic Book" else ""
    
    parts = []
    if title: parts.append(title)
    if issue_str: parts.append(issue_str)
    if year_str: parts.append(year_str)
    if variant and variant != "STANDARD COVER": parts.append(variant)
    if character: parts.append(character)
    if key_info: parts.append(key_info)
    if grade_part: parts.append(grade_part)
    if era: parts.append(era)
    if publisher: parts.append(publisher)
    
    result = " ".join(parts)
    if len(result) > 80:
        parts = []
        if title: parts.append(title)
        if issue_str: parts.append(issue_str)
        if year_str: parts.append(year_str)
        if variant and variant != "STANDARD COVER": parts.append(variant)
        if character: parts.append(character)
        if grade_part: parts.append(grade_part)
        result = " ".join(parts)
        if len(result) > 80:
            result = result[:80]
    return result

def getEbaySpecificsList():
    year_val = st.session_state.get("comic_data", {}).get("year", "N/A")
    grade_num = st.session_state.get("comic_data", {}).get("final_grade_num", 9.0)
    grade_str = st.session_state.get("comic_data", {}).get("final_grade_str", "Very Fine/Near Mint").split('(')[0].strip()
    
    return [
        { "name": "UPC", "value": st.session_state.get("comic_data", {}).get("upc", "Does Not Apply") or "Does Not Apply" },
        { "name": "Series Title", "value": st.session_state.get("comic_data", {}).get("title", "N/A") or "N/A" },
        { "name": "Character", "value": st.session_state.get("comic_data", {}).get("character", "N/A") or "N/A" },
        { "name": "Genre", "value": st.session_state.get("comic_data", {}).get("genre", "Superheroes") or "Superheroes" },
        { "name": "Artist/Writer", "value": st.session_state.get("comic_data", {}).get("writer", "N/A") or "N/A" },
        { "name": "Publisher", "value": st.session_state.get("comic_data", {}).get("publisher", "N/A") or "N/A" },
        { "name": "Superhero Team", "value": st.session_state.get("comic_data", {}).get("team", "N/A") or "N/A" },
        { "name": "Publication Year", "value": year_val or "N/A" },
        { "name": "Format", "value": st.session_state.get("comic_data", {}).get("format", "Single Issue") or "Single Issue" },
        { "name": "Era", "value": autoComputeEra(year_val) },
        { "name": "Type", "value": st.session_state.get("comic_data", {}).get("type", "Comic Book") or "Comic Book" },
        { "name": "Grade", "value": f"{grade_num} {grade_str}" },
        { "name": "Professional Grader", "value": st.session_state.get("comic_data", {}).get("grader", "Flashpoint Finds") or "Flashpoint Finds" },
        { "name": "Certification Number", "value": st.session_state.get("comic_data", {}).get("cert", "Seller Authenticated") or "Seller Authenticated" },
        { "name": "Tradition", "value": st.session_state.get("comic_data", {}).get("tradition", "US Comics") or "US Comics" },
        { "name": "Universe", "value": st.session_state.get("comic_data", {}).get("universe", "N/A") or "N/A" },
        { "name": "Cover Artist", "value": st.session_state.get("comic_data", {}).get("artist", "N/A") or "N/A" },
        { "name": "Features", "value": st.session_state.get("comic_data", {}).get("features", "N/A") or "N/A" },
        { "name": "Unit of Sale", "value": st.session_state.get("comic_data", {}).get("saleunit", "Single Unit") or "Single Unit" },
        { "name": "Convention/Event", "value": st.session_state.get("comic_data", {}).get("convention", "None") or "None" },
        { "name": "Signed", "value": st.session_state.get("comic_data", {}).get("signed", "No") or "No" },
        { "name": "Signed By", "value": st.session_state.get("comic_data", {}).get("signedby", "N/A") or "N/A" },
        { "name": "Autograph Authentication", "value": st.session_state.get("comic_data", {}).get("auth", "None") or "None" },
        { "name": "Autograph Authentication Number", "value": st.session_state.get("comic_data", {}).get("authnum", "N/A") or "N/A" },
        { "name": "Inscribed", "value": st.session_state.get("comic_data", {}).get("inscribed", "No") or "No" },
        { "name": "Personalized", "value": st.session_state.get("comic_data", {}).get("personalized", "No") or "No" },
        { "name": "Vintage", "value": autoComputeVintage(year_val) },
        { "name": "Story Title", "value": st.session_state.get("comic_data", {}).get("story", "N/A") or "N/A" },
        { "name": "Style", "value": st.session_state.get("comic_data", {}).get("style", "Color") or "Color" },
        { "name": "Language", "value": st.session_state.get("comic_data", {}).get("language", "English") or "English" },
        { "name": "Variant Type", "value": st.session_state.get("comic_data", {}).get("variant", "Standard Cover") or "Standard Cover" },
        { "name": "Country of Origin", "value": st.session_state.get("comic_data", {}).get("country", "United States") or "United States" },
        { "name": "Intended Audience", "value": st.session_state.get("comic_data", {}).get("audience", "General Audience") or "General Audience" },
        { "name": "California Prop 65 Warning", "value": st.session_state.get("comic_data", {}).get("prop65", "No Warning Applicable") or "No Warning Applicable" },
        { "name": "Issue Number", "value": st.session_state.get("comic_data", {}).get("issue", "N/A") or "N/A" },
        { "name": "Unit Quantity", "value": st.session_state.get("comic_data", {}).get("unitqty", "1") or "1" },
        { "name": "Unit Type", "value": st.session_state.get("comic_data", {}).get("unittype", "Unit") or "Unit" }
    ]

def generateEbayDescription():
    title = (st.session_state.comic_data.get("title", "")).upper()
    issue = st.session_state.comic_data.get("issue", "")
    issue_str = f"No. {issue}" if issue else ""
    publisher = (st.session_state.comic_data.get("publisher", "")).upper()
    year = st.session_state.comic_data.get("year", "")
    artist = st.session_state.comic_data.get("artist", "") or "Unknown"
    price = st.session_state.comic_data.get("price", "")
    
    grade_num = st.session_state.comic_data.get("final_grade_num", 9.0)
    grade_str = st.session_state.comic_data.get("final_grade_str", "Very Fine/Near Mint").split('(')[0].strip()
    page_quality = st.session_state.comic_data.get("page_quality", "White Pages")
    
    format_val = st.session_state.comic_data.get("format", "Single Issue")
    type_val = st.session_state.comic_data.get("type", "Comic Book")
    era_val = autoComputeEra(year)
    
    significance = st.session_state.comic_data.get("significance", "")
    trivia = st.session_state.comic_data.get("trivia", "")
    notes = st.session_state.comic_data.get("notes", "")
    
    is_key = st.session_state.comic_data.get("keyLevel", "") != "Collectible Comic Book"
    is_key_heading = "KEY ISSUE UNLOCKED!" if is_key else "COLLECTIBLE TIMELINE ADDITION!"
    
    grade_sub_label = f"({format_val.upper()})"

    id_paragraph_text = f"Presenting <em>{title} {issue_str}</em>, officially published by {publisher} in {year}. This copy is formatted as a premium {format_val} {type_val} from the classic {era_val}. Features artwork by {artist}. Originally retailing for {price}. This serves as an essential, high-data-grade reference piece for dedicated collectors and timeline curators tracking core publisher canon."

    lore_paragraph_text = ""
    if significance:
        lore_paragraph_text += f"<strong>Key Significance:</strong> {significance}<br><br>"
    if trivia:
        lore_paragraph_text += f"<strong>League of Comic Geeks Insights:</strong> {trivia}"
    if not lore_paragraph_text:
        lore_paragraph_text = "This release is a valued addition to the ongoing publisher universe. Standard core continuity adventures are preserved inside."

    page_text = f" Pages are evaluated as {page_quality}." if page_quality else ""
    notes_part = notes if notes else "Inspected at standard high magnification under color-balanced studio light boards."
    condition_paragraph_text = f"This copy presents beautifully with strong visual appeal. {notes_part}{page_text}"

    return f"""<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @media only screen and (max-width: 768px) {{
        .fp-wrapper {{ padding: 15px 5px !important; border-width: 6px !important; }}
        .fp-container {{ max-width: 100% !important; }}
        .fp-box {{ padding: 25px 15px !important; margin-bottom: 25px !important; }}
        .fp-h2 {{ font-size: 16px !important; letter-spacing: 2px !important; }}
        .fp-p {{ font-size: 15px !important; }}
        .fp-grade {{ font-size: 20px !important; display: block !important; text-align: center; margin-bottom: 5px; }}
        .fp-grade-desc {{ display: block !important; text-align: center; }}
        .fp-grade-container {{ flex-direction: column !important; align-items: center !important; }}
        .fp-main-title {{ font-size: 18px !important; letter-spacing: 2px !important; margin-bottom: 20px !important; }}
        .fp-promo-box {{ padding: 15px !important; }}
    }}
</style>
<div class="fp-wrapper" style="max-width: 100%; margin: 0 auto; background-image: url('https://64.media.tumblr.com/c7a138bc324f7e89f030a7ce168123dc/467e51bf96bb5ff2-74/s1280x1920/ac98ada6f68a26eef2b561de81314840ca30eaf2.gif'); background-repeat: repeat; background-attachment: scroll; padding: 40px 10px; border: 12px solid #000000; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #ffffff; line-height: 1.6; box-sizing: border-box; box-shadow: inset 0 0 150px rgba(0,0,0,1);">
    <div class="fp-container" style="max-width: 850px; margin: 0 auto;">
        
        <!-- HEADER BRANDING LOGO -->
        <div style="text-align: center; margin-bottom: 40px; margin-top: 10px; padding: 10px;">
            <img src="https://i.ibb.co/6PSpSMRJ/Flashpoint-Finds-5.png" alt="Flashpoint Finds Logo" style="border: 4px solid #00f2ff; box-shadow: 0 0 25px rgba(0, 242, 255, 0.6); max-width: 180px; height: auto; display: block; margin: 0 auto; background-color: rgba(0,0,0,0.4); border-radius: 4px;">
        </div>
        
        <!-- CORE BOOK DETAILS CONTAINER -->
        <div class="fp-box" style="border: 2px solid #00f2ff; background: rgba(0, 0, 0, 0.9); padding: 40px 30px; margin-bottom: 40px; box-shadow: 0 0 30px rgba(0, 242, 255, 0.15); position: relative; border-radius: 4px;">
            <div style="position: absolute; top: -2px; left: -2px; width: 30px; height: 30px; border-top: 5px solid #00f2ff; border-left: 5px solid #00f2ff; border-radius: 4px 0 0 0;"></div>
            <div style="position: absolute; bottom: -2px; right: -2px; width: 30px; height: 30px; border-bottom: 5px solid #00f2ff; border-right: 5px solid #00f2ff; border-radius: 0 0 4px 0;"></div>
            
            <!-- SECTION 1: ITEM IDENTIFICATION -->
            <div style="margin-bottom: 40px;">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <div style="background: #e00000; width: 4px; height: 24px; margin-right: 12px; flex-shrink: 0;"></div>
                    <h2 class="fp-h2" style="font-family: 'Arial Black', Gadget, sans-serif; font-size: 18px; color: #00f2ff; text-transform: uppercase; margin: 0; letter-spacing: 3px; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);">Item Identification</h2>
                </div>
                <p class="fp-p" style="text-align: left; font-size: 17px; margin: 0; color: #ffffff; border-left: 1px solid rgba(0, 242, 255, 0.3); padding-left: 15px;">
                    <strong style="color: #00f2ff; text-transform: uppercase; letter-spacing: 1px;">{is_key_heading}</strong><br><br>
                    {id_paragraph_text}
                </p>
            </div>
            
            <!-- SECTION 2: LORE TRANSMISSION -->
            <div style="margin-bottom: 40px;">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <div style="background: #00f2ff; width: 4px; height: 24px; margin-right: 12px; flex-shrink: 0;"></div>
                    <h2 class="fp-h2" style="font-family: 'Arial Black', Gadget, sans-serif; font-size: 18px; color: #00f2ff; text-transform: uppercase; margin: 0; letter-spacing: 3px;">Lore Transmission</h2>
                </div>
                <p class="fp-p" style="text-align: left; font-size: 17px; margin: 0 0 25px 0; color: #ffffff; border-left: 1px solid rgba(0, 242, 255, 0.3); padding-left: 15px;">
                    {lore_paragraph_text}
                </p>
            </div>
            
            <!-- SECTION 3: CONDITION ANALYSIS -->
            <div style="margin-bottom: 10px;">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <div style="background: #e00000; width: 4px; height: 24px; margin-right: 12px; flex-shrink: 0;"></div>
                    <h2 class="fp-h2" style="font-family: 'Arial Black', Gadget, sans-serif; font-size: 18px; color: #00f2ff; text-transform: uppercase; margin: 0; letter-spacing: 3px;">Condition Analysis</h2>
                </div>
                <div class="fp-grade-container" style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid rgba(0, 242, 255, 0.3); padding-bottom: 10px; margin-bottom: 15px;">
                    <span class="fp-grade" style="font-family: 'Arial Black', sans-serif; font-size: 24px; text-transform: uppercase; color: #00f2ff; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);">Condition: {grade_str.upper()} ({grade_num:.1f})</span>
                    <span class="fp-grade-desc" style="font-size: 12px; color: #e00000; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">{grade_sub_label}</span>
                </div>
                <p class="fp-p" style="font-size: 15px; color: #d0d0d0; line-height: 1.6;">
                    {condition_paragraph_text}<br><br>
                    <span style="color: rgb(224, 0, 0); font-size: 13px; font-style: italic; background-color: rgba(0, 242, 255, 0.05); padding: 3px 5px; border-radius: 2px;">*Please do not hesitate to reach out if you have questions or would like to see additional photos!*</span>
                </p>
            </div>
        </div>
        
        <!-- POLICY & PROTOCOLS CONTAINER -->
        <div class="fp-box" style="border: 2px solid #00f2ff; background: rgba(0, 0, 0, 0.95); padding: 40px 30px; box-shadow: 0 0 40px rgba(0, 242, 255, 0.1); position: relative; border-radius: 4px;">
            <div style="position: absolute; top: -2px; left: -2px; width: 30px; height: 30px; border-top: 5px solid #00f2ff; border-left: 5px solid #00f2ff; border-radius: 4px 0 0 0;"></div>
            
            <h2 class="fp-main-title" style="font-family: 'Arial Black', Gadget, sans-serif; font-size: 22px; color: #000000; text-transform: uppercase; background-color: #00f2ff; margin-top: 0; margin-bottom: 30px; letter-spacing: 4px; padding: 10px 20px; display: inline-block; box-shadow: 4px 4px 0 #e00000;">⚡ Protocols</h2>
            
            <div class="fp-p" style="text-align: left; font-size: 15px; line-height: 1.8; color: #ffffff;">
                <p style="margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
                    <strong style="color: #00f2ff; text-transform: uppercase;">📦 Shipping &amp; Combined Orders:</strong><br>
                    <strong style="color: #ffffff;">Comics:</strong> Shipped FAST and secure in rigid Gemini mailers via USPS Ground Advantage ($6.99 base, +$0.50 each additional). <span style="color: #00f2ff; font-weight: bold; text-transform: uppercase;">⚡ SHIPPING IS STRICTLY CAPPED AT $9.99! Buy as many comics as you want, and never pay more than $9.99 to ship your entire order!</span><br>
                    <strong style="color: #ffffff;">Trading Cards:</strong> Shipped via eBay Standard Envelope for a flat $0.99. Combined shipping is available at a discounted price of $0.15/additional single! (Larger card orders over 3 oz or $20 automatically upgrade to Ground Advantage).<br>
                    <strong style="color: #ffffff;">Books &amp; Magazines:</strong> Heavy lore requires heavy protection! Shipped securely via USPS Ground Advantage or Media Mail (depending on USPS content eligibility rules).<br>
                    <strong style="color: #ffffff;">Video Games:</strong> Shipped FAST and secure via USPS Ground Advantage, heavily protected to ensure fragile cases and discs survive the jump through the timeline intact!<br>
                    <strong style="color: #ffffff;">Media/CDs:</strong> Shipped FAST and secure via USPS Media Mail or Ground Advantage. CDs are shipped in dedicated, crush-proof cardboard media mailers to prevent jewel case cracking during transit!<br>
                    <strong style="color: #ffffff;">Action Figures &amp; Toys:</strong> Shipped FAST and secure via USPS Ground Advantage, heavily protected to ensure boxes and backing cards survive the jump through the timeline intact!<br>
                    <strong style="color: #ffffff;">Diecast Vehicles:</strong> Shipped FAST and secure via USPS Ground Advantage, heavily protected in a rigid box to ensure the packaging survives the jump through the timeline intact!<br>
                    <strong style="color: #ffffff;">Combined Shipping:</strong> To help keep the timeline organized and trigger your automated shipping caps and promos, please add all items to your cart <em>before</em> checking out so they process as a single order.
                </p>
                
                <p style="margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
                    <strong style="color: #00f2ff; text-transform: uppercase;">⚡ No Rewinds (Returns):</strong><br>
                    Collectibles are a fast-moving game. Because of market volatility and the risk of item tampering or "swapping," we do not accept returns for buyer's remorse. Once we make a deal and the item hits your collection, it’s part of the permanent timeline! <em>However, as a buyer, you are always fully protected by the eBay Money Back Guarantee if an item arrives damaged in transit or significantly not as described.</em>
                </p>
                
                <p style="margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
                    <strong style="color: #00f2ff; text-transform: uppercase;">⚡ The Real Deal:</strong><br>
                    Transparency is everything at Flashpoint Finds. My promise to you is that every single item in my store is exactly as described and pictured. I provide high-resolution photos of every item so you can see the truth for yourself. What you see in the gallery is exactly what shows up at your door—please review them closely before securing your item!
                </p>
                
                <p style="margin-bottom: 25px;">
                    <strong style="color: #00f2ff; text-transform: uppercase;">⚡ Your Data, Your Timeline:</strong><br>
                    I value your privacy as much as a Mint condition grail. When you buy from Flashpoint Finds, your data is only used for one thing: getting your package to you securely. <strong>The Flashpoint Promise:</strong> I will never sell your info, add you to a mailing list, or use outside trackers. Your personal info stays in this transaction and nowhere else.
                </p>

                <!-- TIERED PROMOTIONS BOX -->
                <div class="fp-promo-box" style="margin: 30px 0 10px 0; border: 2px solid #00f2ff; padding: 20px; background: rgba(0, 242, 255, 0.05); position: relative;">
                    <div style="position: absolute; top: -12px; left: 10px; background: #00f2ff; color: #000; padding: 4px 10px; font-size: 12px; font-weight: bold; text-transform: uppercase;">⚡ Flashpoint Tiered Promos</div>
                    <strong style="font-size: 18px; color: #ffffff; text-transform: uppercase; display: block; margin-top: 10px;">Build Your Bundle &amp; Save!</strong>
                    <p style="font-size: 14px; color: #d0d0d0; margin-top: 10px; margin-bottom: 15px; line-height: 1.5;">We price accurately to the current market, but reward timeline curators who bundle! Mix and match items within the same promotional tier to trigger massive discounts at checkout:</p>
                    <ul style="font-size: 14px; color: #00f2ff; line-height: 1.8; margin: 0; padding-left: 20px;">
                        <li><strong style="color: #ffffff;">Tier 1 (Items $7.99 &amp; Under):</strong> Buy 4, Get 1 FREE!</li>
                        <li><strong style="color: #ffffff;">Tier 2 (Items $8.00 to $19.99):</strong> Buy 3, Get 1 FREE!</li>
                        <li><strong style="color: #ffffff;">Tier 3 (Grails $20.00+):</strong> Buy 2, Save 15% automatically!</li>
                    </ul>
                    <p style="font-size: 12px; color: #e00000; margin-top: 15px; font-style: italic; line-height: 1.4;">*Pro-Tip: Simply add all qualifying items from the same tier to your eBay cart before checkout, and the system will automatically deduct the discount!*</p>
                </div>
            </div>
        </div>
    </div>
</div>"""

# ==========================================
# 5. SIDEBAR BRANDING & CREDENTIALS
# ==========================================
with st.sidebar:
    st.markdown(logo_svg_html, unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-top: -10px;'><span style='font-family: \"Oswald\", sans-serif; font-size: 16px; font-weight: bold; color: #ffffff; letter-spacing: 2px;'>⚡ FLASHPOINT FINDS</span></div>", unsafe_allow_html=True)

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
# 6. CHRONO-ENGINE API RUNNERS
# ==========================================
def call_gemini_with_backoff(prompt, images=None, google_search=False):
    if not api_key:
        st.warning("Please configure your Gemini API Key in the sidebar or secrets manager to execute automated runs.")
        return None
    
    # Direct HTTP implementation: no native Python SDK imports or initialization needed!
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    parts = [{"text": prompt}]
    if images:
        for img in images:
            parts.append({
                "inlineData": {
                    "mimeType": img["mime_type"],
                    "data": base64.b64encode(img["data"]).decode("utf-8")
                }
            })
            
    payload = {
        "contents": [{
            "parts": parts
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
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
                    "missing": {"type": "NUMBER"}
                },
                "required": ["title", "issue", "publisher", "year"]
            }
        }
    }
    
    if google_search:
        payload["tools"] = [{"google_search": {}}]
        
    delay = 1.0
    for attempt in range(5):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                res_json = response.json()
                text_response = res_json["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_response)
            elif response.status_code in [429, 500, 502, 503, 504]:
                pass # Trigger next backoff retry iteration
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
                return None
        except Exception as e:
            if attempt == 4:
                st.error(f"Timeline Engine connection timeout: {str(e)}")
                return None
        time.sleep(delay + random.uniform(0.1, 0.5))
        delay *= 2.0
    return None

# ==========================================
# 7. APP MAIN GRID LAYOUT
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
                    data = call_gemini_with_backoff(prompt, google_search=True)
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
# 8. RIGHT PANEL: PREMIUM CARD RENDERING DESK
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
                    <span id="card-front-asset-tag" style="font-size:8px; font-weight:bold; background:rgba(255,193,7,0.15); border:1px solid rgba(255,193,7,0.4); color:#FFC107; padding:2px 6px; border-radius:4px; text-transform:uppercase; letter-spacing:1px; flex-shrink:0;">{st.session_state.comic_data.get('investmentTier', 'Blue Chip Key')}</span>
                </div>
                <div style="font-size:12px; color:#aaa; margin-top:2px;">#{st.session_state.comic_data['issue']} &bull; {st.session_state.comic_data['publisher']} ({st.session_state.comic_data['year']})</div>
                <div style="font-size:9px; color:#555; font-weight:semibold; margin-top:2px;">Cover Art: {st.session_state.comic_data['artist']}</div>
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
    
    st.components.v1.html(card_html, height=640, scrolling=False)
    
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