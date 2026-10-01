import streamlit as st
import requests
from PIL import Image
import base64
import os

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="SmartSort-AI | Plastic Classifier",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = "https://smartsort-ai.onrender.com"
latitude, longitude = 12.9716, 77.5946

PAGES = ["🏠 Classify Plastic", "📊 Statistics", "📖 Learn More"]

# ============================================
# STYLES
# ============================================
@st.cache_data
def get_background_image_base64():
    path = "frontend/assets/background_img.jpg"
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return None

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
  --g:#15803d; --g-dark:#14532d; --g-soft:#ecfdf3; --ink:#0f172a; --muted:#64748b;
  --line:#e2e8f0; --surface:#ffffff; --blue:#1d4ed8; --amber:#b45309; --amber-soft:#fffbeb;
  --radius:14px;
}
html, body, .stApp{font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif; color-scheme:light;}
.stApp{background:#f6f8f7;}
.block-container{max-width:1080px; padding:1.5rem 1.25rem 3rem;}
#MainMenu, footer, header[data-testid="stHeader"]{visibility:hidden; height:0;}

/* Text */
[data-testid="stMarkdownContainer"] *, label, .stCaption, [data-testid="stWidgetLabel"] *{color:var(--ink);}
.muted, .muted *{color:var(--muted) !important;}
h2{font-size:1.35rem !important; font-weight:700 !important; letter-spacing:-0.01em; margin:0 0 .25rem !important;}
h4{font-size:1rem !important; font-weight:600 !important; margin:1.25rem 0 .5rem !important;}

/* Hero */
.stApp .hero{background:linear-gradient(120deg,#14532d,#15803d); border-radius:var(--radius); padding:1.75rem 2rem; margin-bottom:1rem;}
.stApp .hero, .stApp .hero *{color:#fff !important;}
.hero h1{font-size:2rem; font-weight:800; letter-spacing:-0.02em; margin:0; padding:0;}
.hero p{margin:.35rem 0 0; font-size:1rem; opacity:.92;}

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--surface); border:1px solid var(--line) !important; border-radius:var(--radius) !important; box-shadow:0 1px 2px rgba(15,23,42,.04);}
.stApp .badge{display:inline-block; padding:.35rem 1rem; border-radius:999px; font-weight:700; font-size:1.15rem; color:#fff;}
.stApp .badge *{color:#fff !important;}
.fullname{font-size:1.05rem; font-weight:600; margin:.5rem 0 1rem;}
.bar{background:#e8eeea; border-radius:999px; height:12px; overflow:hidden;}
.bar > div{height:100%; background:var(--g); border-radius:999px; transition:width .6s ease;}
.barlabel{display:flex; justify-content:space-between; font-size:.85rem; margin:.9rem 0 .4rem; font-weight:600;}

/* Info tiles */
.grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:.75rem; margin:1rem 0;}
.tile{border:1px solid var(--line); border-radius:12px; padding:.85rem 1rem; background:#fff;}
.tile small{display:block; color:var(--muted) !important; font-weight:600; font-size:.78rem; margin-bottom:.2rem;}
.tile b{font-size:.98rem;}
.tile.ok{background:var(--g-soft); border-color:#bbf7d0;}
.tile.mid{background:#eff6ff; border-color:#bfdbfe;}
.tile.low{background:var(--amber-soft); border-color:#fde68a;}

/* Chips and tips */
.chips{display:flex; flex-wrap:wrap; gap:.4rem;}
.chip{padding:.3rem .8rem; border-radius:999px; background:#f1f5f9; border:1px solid var(--line); font-size:.88rem;}
.note{background:var(--g-soft); border-left:4px solid var(--g); border-radius:10px; padding:.85rem 1rem; font-size:.95rem;}
.tips{list-style:none; padding:0; margin:0; display:grid; gap:.5rem;}
.tips li{padding:.65rem .9rem; border:1px solid var(--line); border-radius:10px; background:#fff; font-size:.93rem;}

/* Empty state */
.empty{text-align:center; padding:3rem 1rem;}
.empty .ico{font-size:2.5rem;}
.empty p{margin:.4rem 0 0;}

/* Stats */
.stat{background:#fff; border:1px solid var(--line); border-radius:var(--radius); padding:1.1rem 1.25rem;}
.stat .n{font-size:1.9rem; font-weight:800; line-height:1.1; color:var(--g-dark) !important;}
.stat .l{font-size:.85rem; color:var(--muted) !important; font-weight:500; margin-top:.25rem;}

/* Buttons */
.stButton>button{min-height:2.75rem; border-radius:10px; font-weight:600; border:1px solid var(--line); background:#fff; color:var(--ink); transition:background .15s, border-color .15s, box-shadow .15s;}
.stButton>button:hover{border-color:var(--g); color:var(--g-dark); background:var(--g-soft);}
.stButton>button[kind="primary"]{background:var(--g); border-color:var(--g); color:#fff;}
.stButton>button[kind="primary"] *{color:#fff !important;}
.stButton>button[kind="primary"]:hover{background:var(--g-dark); border-color:var(--g-dark);}
button:focus-visible, input:focus-visible{outline:3px solid #86efac !important; outline-offset:2px;}

/* Uploader */
[data-testid="stFileUploaderDropzone"]{background:#f8fafc; border:2px dashed #cbd5e1; border-radius:12px;}
[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--g); background:var(--g-soft);}
[data-testid="stFileUploaderDropzone"] *{color:var(--ink) !important;}
[data-testid="stFileUploaderDropzone"] button{background:#fff; border:1px solid var(--line);}
[data-testid="stImage"] img{border-radius:12px;}

/* Tabs */
.stTabs [data-baseweb="tab"]{font-weight:600;}
.stTabs [aria-selected="true"]{color:var(--g-dark) !important;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--g);}

/* Sidebar */
section[data-testid="stSidebar"]{background:var(--g-dark);}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *, section[data-testid="stSidebar"] .stCaption *{color:#e7f5ec !important;}
.status{display:flex; align-items:center; gap:.5rem; padding:.35rem 0; font-size:.92rem;}
.dot{width:.6rem; height:.6rem; border-radius:50%; display:inline-block;}
.dot.on{background:#4ade80;} .dot.off{background:#f87171;} .dot.warn{background:#fbbf24;}

.fade{animation:fade .35s ease;}
@keyframes fade{from{opacity:0; transform:translateY(6px);} to{opacity:1; transform:none;}}

@media (max-width:768px){
  .block-container{padding:1rem .75rem 2rem;}
  .hero{padding:1.25rem !important;} .hero h1{font-size:1.6rem;}
}
@media (prefers-reduced-motion:reduce){*{transition:none !important; animation:none !important;}}
"""

bg = get_background_image_base64()
if bg:
    CSS += f""".stApp{{background-image:linear-gradient(rgba(246,248,247,.93),rgba(246,248,247,.93)),url("data:image/jpg;base64,{bg}");
    background-size:cover; background-position:center; background-attachment:fixed;}}"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================
defaults = {
    "classification_result": None,
    "uploaded_image": None,
    "history": [],
    "current_page": PAGES[0],
    "open_camera": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================
# HELPERS
# ============================================
def classify_image(image_file, latitude=None, longitude=None):
    """Send image to backend for classification"""
    try:
        files = {"file": ("image.jpg", image_file, "image/jpeg")}
        params = {}
        if latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude
        response = requests.post(f"{API_URL}/classify", files=files, params=params)
        if response.status_code == 200:
            return response.json()
        st.error(f"Classification failed ({response.status_code}). {response.text}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Can't reach the backend. Check that the API is running, then try again.")
        st.info("Run: `cd backend && python main.py`")
        return None
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        return None

def get_stats():
    try:
        response = requests.get(f"{API_URL}/stats")
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=30, show_spinner=False)
def get_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        return {"ok": r.status_code == 200, "data": r.json() if r.status_code == 200 else {}}
    except Exception:
        return None

def get_color_for_type(plastic_type):
    return {"PET": "#15803d", "HDPE": "#1d4ed8", "OTHER": "#64748b"}.get(plastic_type, "#64748b")

def html(s):
    st.markdown(s, unsafe_allow_html=True)

# ============================================
# SIDEBAR (status + about)
# ============================================
with st.sidebar:
    st.markdown("### ♻️ SmartSort-AI")
    st.markdown("**System status**")
    health = get_health()
    if health is None:
        html('<div class="status"><span class="dot off"></span>Backend offline</div>')
        st.caption("Run: `python backend/main.py`")
    elif not health["ok"]:
        html('<div class="status"><span class="dot off"></span>Backend error</div>')
    else:
        html('<div class="status"><span class="dot on"></span>Backend connected</div>')
        if health["data"].get("model_loaded"):
            html('<div class="status"><span class="dot on"></span>AI model loaded</div>')
        else:
            html('<div class="status"><span class="dot warn"></span>AI model not loaded</div>')
    st.caption("The free backend can take up to a minute to wake up after being idle.")

# ============================================
# HEADER + NAVIGATION
# ============================================
html("""
<div class="hero">
  <h1>♻️ SmartSort-AI</h1>
  <p><strong>One scan can save the planet.</strong> AI-powered plastic waste classification.</p>
</div>
""")

nav_cols = st.columns(len(PAGES))
for col, page in zip(nav_cols, PAGES):
    with col:
        active = st.session_state.current_page == page
        if st.button(page, key=f"nav_{page}", width="stretch",
                     type="primary" if active else "secondary"):
            st.session_state.current_page = page
            st.rerun()

st.write("")

# ============================================
# PAGE: CLASSIFY
# ============================================
if st.session_state.current_page == PAGES[0]:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("## Upload an image")
            st.caption("Photograph the plastic item with its recycling symbol visible, if it has one.")

            uploaded_file = st.file_uploader(
                "Choose an image",
                type=["jpg", "jpeg", "png"],
                help="Upload a clear photo of plastic waste",
                label_visibility="collapsed",
            )

            if st.session_state.open_camera:
                camera_image = st.camera_input("Take a photo with your camera", key="camera_input")
                if camera_image:
                    st.session_state.uploaded_image = camera_image
                    st.session_state.open_camera = False
                    st.rerun()
            else:
                if st.button("📷 Use camera instead", key="open_camera_button", width="stretch"):
                    st.session_state.open_camera = True
                    st.rerun()

            image_source = st.session_state.uploaded_image if st.session_state.uploaded_image else uploaded_file

            if image_source:
                image = Image.open(image_source)
                st.image(image, caption="Your image", width="stretch")

                b1, b2 = st.columns([2, 1])
                with b1:
                    classify_clicked = st.button("🔍 Classify plastic", type="primary", width="stretch")
                with b2:
                    if st.button("Remove", key="remove_uploaded_image", width="stretch"):
                        st.session_state.uploaded_image = None
                        st.session_state.classification_result = None
                        st.rerun()

                if classify_clicked:
                    with st.spinner("Analyzing image..."):
                        image_source.seek(0)
                        result = classify_image(image_source, latitude, longitude)
                        if result and result.get("success"):
                            st.session_state.classification_result = result
                            st.session_state.uploaded_image = image_source
                            st.rerun()

    with col2:
        if not st.session_state.classification_result:
            with st.container(border=True):
                html("""
                <div class="empty">
                  <div class="ico">🔎</div>
                  <h2>No result yet</h2>
                  <p class="muted">Upload or capture a photo, then select <b>Classify plastic</b>.
                  Your plastic type, recyclability and disposal tips will show up here.</p>
                </div>
                """)
        else:
            result = st.session_state.classification_result

            mapping = {"OTHER": "PET", "PET": "HDPE", "HDPE": "OTHER"}
            full_name_mapping = {
                "OTHER": "Polyethylene Terephthalate",
                "PET": "High-Density Polyethylene",
                "HDPE": "Mixed Plastics",
            }

            original_type = result["predicted_class"]
            plastic_type = mapping.get(original_type, original_type)
            color = get_color_for_type(plastic_type)
            mapped_full_name = full_name_mapping.get(original_type, result["full_name"])

            result_content = {
                "OTHER": {
                    "common_items": ["Plastic bags", "Styrofoam", "Multi-layer packaging", "CD cases", "Acrylic materials"],
                    "instructions": "Check locally before recycling. Many #7 plastics are not accepted in curbside programs.",
                    "tips": [
                        "🚫 Avoid mixing #7 plastics with #1 or #2",
                        "⚠️ Try to reduce usage of mixed plastics",
                        "💡 Look for recycling drop-off locations specializing in #7",
                    ],
                    "material_value": "₹2.48 per kg ($0.03/kg)",
                    "acceptance": "⚠️ Not accepted in most curbside recycling programs",
                },
                "PET": {
                    "common_items": ["Water bottles", "Soda bottles", "Food containers", "Peanut butter jars", "Salad containers"],
                    "instructions": "Rinse clean, remove caps and labels, flatten bottles before recycling",
                    "tips": [
                        "✅ Most widely recycled plastic worldwide",
                        "♻️ Can be recycled into fleece, carpet, new bottles, and clothing",
                        "⚠️ Remove labels if possible for better recycling",
                        "💡 Look for the #1 symbol inside the recycling triangle",
                    ],
                    "material_value": "₹9.96 per kg ($0.12/kg)",
                    "acceptance": "✅ Accepted in curbside recycling",
                },
                "HDPE": {
                    "common_items": ["Milk jugs", "Detergent bottles", "Shampoo bottles", "Toy parts", "Pipe fittings"],
                    "instructions": "Rinse clean, remove caps, bottles can be recycled with lids in some programs",
                    "tips": [
                        "✅ Very valuable to recyclers",
                        "♻️ Used for plastic lumber, piping, new bottles",
                        "💡 Look for #2 symbol inside the triangle",
                    ],
                    "material_value": "₹13.20 per kg ($0.16/kg)",
                    "acceptance": "✅ Accepted in most curbside recycling programs",
                },
            }
            display_content = result_content.get(plastic_type, result_content["PET"])

            display_code_map = {"7": "1", "1": "2", "2": "7"}
            original_code = result["recycling_code"].lstrip("#")
            display_recycling_code = f"#{display_code_map.get(original_code, original_code)}"

            confidence = max(0, min(100, result["confidence"] * 100))

            if plastic_type == "OTHER":
                tile_class, icon, recyclability_display = "low", "⚠️", "Low"
            else:
                recyclability_display = result["recyclability"]
                tile_class, icon = {
                    "High": ("ok", "✅"),
                    "Medium": ("mid", "ℹ️"),
                }.get(recyclability_display, ("low", "⚠️"))

            accepted = "Accepted" in display_content["acceptance"]
            accept_class = "ok" if accepted else "low"
            accept_text = display_content["acceptance"].lstrip("✅⚠️ ").strip()

            with st.container(border=True):
                html(f"""
                <div class="fade">
                  <span class="badge" style="background:{color};">{plastic_type} {display_recycling_code}</span>
                  <div class="fullname">{mapped_full_name}</div>
                  <div class="barlabel"><span>Confidence</span><span>{confidence:.1f}%</span></div>
                  <div class="bar" role="progressbar" aria-valuenow="{confidence:.0f}" aria-valuemin="0" aria-valuemax="100">
                    <div style="width:{confidence}%;"></div>
                  </div>
                  <div class="grid">
                    <div class="tile {tile_class}"><small>Recyclability</small><b>{icon} {recyclability_display}</b></div>
                    <div class="tile {accept_class}"><small>Curbside pickup</small><b>{accept_text}</b></div>
                    <div class="tile"><small>Estimated value</small><b>💰 {display_content["material_value"]}</b></div>
                  </div>
                </div>
                """)

                st.markdown("#### Common items")
                chips = "".join(f'<span class="chip">{i}</span>' for i in display_content["common_items"])
                html(f'<div class="chips">{chips}</div>')

                st.markdown("#### How to recycle")
                html(f'<div class="note">{display_content["instructions"]}</div>')

                st.markdown("#### Tips")
                tips = "".join(f"<li>{t}</li>" for t in display_content["tips"])
                html(f'<ul class="tips">{tips}</ul>')

# ============================================
# PAGE: STATISTICS
# ============================================
elif st.session_state.current_page == PAGES[1]:
    st.markdown("## System statistics")
    st.caption("Live numbers from the SmartSort-AI backend.")

    stats_data = get_stats()

    if stats_data and stats_data.get("success"):
        stats = stats_data["statistics"]
        cards = [
            (stats["total_classifications"], "Total classifications"),
            (stats["recent_activity_24h"], "Last 24 hours"),
            (f"{stats['average_confidence'] * 100:.1f}%", "Average confidence"),
            (stats["total_facilities"], "Facilities"),
        ]
        cols = st.columns(4)
        for col, (n, label) in zip(cols, cards):
            with col:
                html(f'<div class="stat"><div class="n">{n}</div><div class="l">{label}</div></div>')

        st.markdown("#### Classifications by plastic type")
        by_type = stats.get("classifications_by_type", {})
        if by_type:
            cols = st.columns(3)
            for idx, (plastic_type, count) in enumerate(by_type.items()):
                color = get_color_for_type(plastic_type)
                with cols[idx % 3]:
                    html(f"""
                    <div class="stat" style="border-top:4px solid {color};">
                      <div class="n">{count}</div><div class="l">{plastic_type}</div>
                    </div>
                    """)
        else:
            st.info("No classifications yet. Classify a plastic item to get started.")
    else:
        st.warning("Statistics are unavailable right now. Check the backend status in the sidebar and try again.")

# ============================================
# PAGE: LEARN MORE
# ============================================
elif st.session_state.current_page == PAGES[2]:
    st.markdown("## Learn about plastic recycling")
    st.caption("Quick reference for sorting and preparing plastics.")

    tab1, tab2, tab3 = st.tabs(["♻️ Plastic types", "🌍 Environmental impact", "💡 Best practices"])

    with tab1:
        with st.container(border=True):
            st.markdown("""
#### PET (#1): Polyethylene Terephthalate
- **Most common:** Water bottles, soda bottles
- **Recyclability:** ✅ High, widely recycled
- **Becomes:** New bottles, fleece, carpet, fiberfill

#### HDPE (#2): High-Density Polyethylene
- **Most common:** Milk jugs, detergent bottles
- **Recyclability:** ✅ High, very valuable
- **Becomes:** Plastic lumber, pipes, new containers

#### OTHER (#7): Mixed Plastics
- **Most common:** Various composite materials
- **Recyclability:** ⚠️ Variable, check locally
- **Becomes:** Depends on specific material
            """)

    with tab2:
        with st.container(border=True):
            st.markdown("""
#### Why recycling matters
- ♻️ Reduces landfill waste by 70%
- 🌳 Saves natural resources
- ⚡ Uses 88% less energy than virgin plastic production
- 💨 Reduces CO2 emissions significantly

#### Plastic in numbers
- 🌊 8 million tons of plastic enter oceans yearly
- 🐢 100,000+ marine animals affected by plastic waste
- ⏰ Plastic takes 450+ years to decompose
- ♻️ Only 9% of plastic is recycled globally
            """)

    with tab3:
        with st.container(border=True):
            st.markdown("""
#### Before recycling
1. ✨ Rinse containers clean
2. 🏷️ Remove labels when possible
3. 🚫 Remove caps (recycle separately if accepted)
4. 🥤 Flatten bottles to save space

#### What not to recycle
- ❌ Food-contaminated plastics
- ❌ Plastic bags (take to special collection)
- ❌ Styrofoam (check for special programs)
- ❌ Mixed material items

#### Pro tips
- 📍 Find your local recycling center
- 📱 Use this app to verify plastic types
- 🌟 When in doubt, check with your facility
- 🔄 Reduce and reuse before recycling
            """)

# ============================================
# FOOTER
# ============================================
html('<p class="muted" style="text-align:center; margin-top:2.5rem; font-size:.85rem;">♻️ SmartSort-AI · AI-powered plastic waste classification</p>')