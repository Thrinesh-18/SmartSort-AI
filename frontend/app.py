import streamlit as st
import requests
from PIL import Image
import io
import json
from datetime import datetime
import base64
import os

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="SmartSort-AI - AI Plastic Classifier",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.share_button("Share SmartSort-AI", text="Check out this AI plastic sorter!")

# ============================================
# BACKGROUND IMAGE SETUP
# ============================================

@st.cache_data
def get_background_image_base64():
    """
    Converts the bg.jpg image to base64 for CSS background
    """
    try:
        # Look for bg.jpg in assets folder
        image_path = "frontend/assets/background_img.jpg"
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
        else:
            return None
    except Exception as e:
        return None

# Get background image
bg_image_base64 = get_background_image_base64()

# ============================================
# CUSTOM CSS
# ============================================

if bg_image_base64:
    background_style = f"""
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        position: relative;
        min-height: 100vh;
    }}
    
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.6);
        pointer-events: none;
        z-index: 0;
    }}
    """
else:
    background_style = """
    .stApp {
        background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 30%, #F8FFFD 70%, #E8F5E9 100%) !important;
        background-attachment: fixed !important;
    }
    """

st.markdown(f"""
<style>
    {background_style}
    
    /* Make sure content is above background */
    .main .block-container {{
        position: relative;
        z-index: 1;
    }}
    
    /* SET ALL MAIN CONTENT TEXT TO BLACK */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {{
        color: #000000 !important;
    }}
    
    .stTitle, .stHeader, .stSubheader {{
        color: #000000 !important;
    }}
    
    .stText, .stWrite, .stInfo, .stSuccess, .stWarning, .stError {{
        color: #000000 !important;
    }}
    
    /* Specific text elements */
    p, li, span, div {{
        color: #000000 !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: #000000 !important;
    }}
    
    /* Streamlit specific classes */
    .css-1lcbmhc, .css-1outpf7, .css-1r6slb0 {{
        color: #000000 !important;
    }}
    
    /* FORM ELEMENTS - FIX BLACK BOX TEXT TO WHITE */
    .stNumberInput input, .stSelectbox select, .stTextInput input {{
        color: #ffffff !important;
        background-color: #000000 !important;
    }}
    
    .stNumberInput label, .stSelectbox label, .stSlider label, .stCheckbox label {{
        color: #000000 !important;
    }}
    
    /* File uploader text - fix black box text */
    .stFileUploader label, .stFileUploader span, .stFileUploader div {{
        color: #ffffff !important;
    }}
    
    .uploadedFile {{
        color: #ffffff !important;
    }}
    
    .uploadedFile div, .uploadedFile span, .uploadedFile p {{
        color: #ffffff !important;
    }}
    
    /* Camera input text */
    [data-testid="stCameraInput"] label, 
    [data-testid="stCameraInput"] span, 
    [data-testid="stCameraInput"] div {{
        color: #ffffff !important;
    }}
    
    /* File uploader area */
    [data-testid="stFileUploader"] * {{
        color: #ffffff !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {{
        color: #000000 !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        color: #000000 !important;
    }}
    
    /* Caption */
    .stCaption {{
        color: #000000 !important;
    }}
    
    /* Ensure all streamlit text elements are black */
    .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj {{
        color: #000000 !important;
    }}
    
    /* Radio button labels */
    .stRadio label {{
        color: #000000 !important;
    }}
    
    /* Metric cards text */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
        color: #000000 !important;
    }}
    
    /* Spinner text */
    .stSpinner {{
        color: #000000 !important;
    }}
    
    /* SIDEBAR TEXT IN WHITE */
    section[data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown ul,
    section[data-testid="stSidebar"] .stMarkdown ol {{
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] .stTitle,
    section[data-testid="stSidebar"] .stHeader,
    section[data-testid="stSidebar"] .stSubheader {{
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] .stSuccess,
    section[data-testid="stSidebar"] .stWarning,
    section[data-testid="stSidebar"] .stError,
    section[data-testid="stSidebar"] .stInfo {{
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] .stCaption {{
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] .stCheckbox label {{
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] .stNumberInput label {{
        color: #ffffff !important;
    }}
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader {{
        color: #ffffff !important;
    }}
    
    /* Main theme colors */
    :root {{
        --primary-green: #2E7D32;
        --secondary-green: #1B5E20;
        --light-green: #E8F5E9;
        --accent-orange: #F57C00;
    }}
    
    /* Sidebar background */
    .css-1d391kg, .css-1lcbmhc {{
        background-color: #1B5E20 !important;
    }}
    
    /* Header styling */
    .main-header {{
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .main-header h1 {{
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }}
    
    /* Navigation buttons */
    .nav-button {{
        width: 100%;
        padding: 1rem;
        margin: 0.5rem 0;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        background: #4CAF50;
        color: white;
    }}
    
    .nav-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        background: #45a049;
    }}
    
    .nav-button.active {{
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(245, 124, 0, 0.3);
    }}
    
    /* Result card styling */
    .result-card {{
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid var(--primary-green);
        color: #000000 !important;
    }}
    
    .result-card p, .result-card div, .result-card span {{
        color: #000000 !important;
    }}
    
    .plastic-type-badge {{
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.3rem;
        margin: 1rem 0;
    }}
    
    .confidence-bar {{
        background: #e0e0e0;
        border-radius: 10px;
        height: 30px;
        margin: 1rem 0;
        overflow: hidden;
    }}
    
    .confidence-fill {{
        height: 100%;
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        transition: width 0.5s ease;
    }}
    
    /* Facility card */
    .facility-card {{
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1976D2;
        color: #000000 !important;
    }}
    
    .facility-card h4 {{
        margin: 0 0 0.5rem 0;
        color: #1976D2;
    }}
    
    /* Info boxes */
    .info-box {{
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196F3;
        color: #000000 !important;
    }}
    
    .warning-box {{
        background: #FFF3E0;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #FF9800;
        color: #000000 !important;
    }}
    
    .success-box {{
        background: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #4CAF50;
        color: #000000 !important;
    }}
    
    /* Tip items */
    .tip-item {{
        background: white;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #000000 !important;
    }}
    
    /* Stats styling */
    .stat-box {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }}
    
    .stat-number {{
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .stat-label {{
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }}
    
    /* Button styling */
    .stButton>button {{
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: transform 0.2s;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Camera upload styling */
    .uploadedFile {{
        border: 2px dashed #2E7D32;
        border-radius: 10px;
        padding: 2rem;
        background-color: rgba(0, 0, 0, 0.8) !important;
    }}
    
    /* Specific fix for file uploader text colors */
    [data-testid="stFileUploader"] * {{
        color: #ffffff !important;
    }}
    
    .stFileUploader * {{
        color: #ffffff !important;
    }}
    
    /* Fix for camera input text */
    [data-testid="stCameraInput"] * {{
        color: #ffffff !important;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================
# CONFIGURATION
# ============================================

API_URL = "https://smartsort-ai.onrender.com"

# Initialize session state
if 'classification_result' not in st.session_state:
    st.session_state.classification_result = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Classify Plastic"
if 'open_camera' not in st.session_state:
    st.session_state.open_camera = False

latitude = 12.9716
longitude = 77.5946

# ============================================
# HELPER FUNCTIONS
# ============================================

def classify_image(image_file, latitude=None, longitude=None):
    """Send image to backend for classification"""
    try:
        files = {'file': ('image.jpg', image_file, 'image/jpeg')}
        params = {}
        if latitude and longitude:
            params['latitude'] = latitude
            params['longitude'] = longitude
        response = requests.post(f"{API_URL}/classify", files=files, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure the API is running on port 8000!")
        st.info("Run: `cd backend && python main.py`")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_stats():
    """Get system statistics"""
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_color_for_type(plastic_type):
    """Get color for plastic type"""
    colors = {
        'PET': '#2E7D32',
        'HDPE': '#1976D2',
        'OTHER': '#757575'
    }
    return colors.get(plastic_type, '#757575')


# ============================================
# HEADER
# ============================================

st.markdown("""
<div class="main-header">
    <h1>♻️ SmartSort-AI</h1>
    <p style=" font-style: italic; font-weight: 600; font-size: 1.3rem; margin: 0.2rem 0 1rem 0; color: #ffffff;">
        One Scan can Save the Planet
    </p>
    <p>AI-Powered Plastic Waste Classification System</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Navigation")
    
    pages = [
        ("🏠 Classify Plastic", "🏠 Classify Plastic"),
        ("📊 Statistics", "📊 Statistics"),
        ("📖 Learn More", "📖 Learn More")
    ]
    
    for icon, page_name in pages:
        is_active = st.session_state.current_page == page_name
        button_class = "nav-button active" if is_active else "nav-button"
        if st.button(
            page_name,
            key=page_name,
            width='stretch'
        ):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.markdown("### 🔌 System Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
            health = response.json()
            if health.get('model_loaded'):
                st.success("✅ AI Model Loaded")
            else:
                st.warning("⚠️ AI Model Not Loaded")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
        st.caption("Run: `python backend/main.py`")


# ============================================
# PAGE: CLASSIFY PLASTIC
# ============================================

if st.session_state.current_page == "🏠 Classify Plastic":

    st.markdown("## 📸 Upload Plastic Waste Image")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="info-box">
            <h4 style="margin-top:0; color: #000000;">📋 How to Use:</h4>
            <ol style="margin-bottom:0; color: #000000;">
                <li>Take a clear photo of the plastic item</li>
                <li>Make sure the recycling symbol is visible (if present)</li>
                <li>Upload the image below</li>
                <li>Get instant classification results!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear photo of plastic waste"
        )

        camera_image = None
        if st.session_state.open_camera:
            camera_image = st.camera_input("Take a photo with your camera", key="camera_input")
            if camera_image:
                st.session_state.uploaded_image = camera_image
                st.session_state.open_camera = False
                st.rerun()

        else:
            if st.button("📷 Open Camera", key="open_camera_button", width='stretch'):
                st.session_state.open_camera = True
                st.rerun()

        image_source = st.session_state.uploaded_image if st.session_state.uploaded_image else uploaded_file

        if image_source:
            image = Image.open(image_source)
            st.image(image, caption="Uploaded Image", width='stretch')

            if st.button("❌ Remove Image", key="remove_uploaded_image"):
                st.session_state.uploaded_image = None
                st.session_state.classification_result = None
                st.rerun()

            if st.button("🔍 Classify Plastic", width='stretch'):
                with st.spinner("🤖 Analyzing image..."):
                    image_source.seek(0)
                    result = classify_image(
                        image_source,
                        latitude,
                        longitude)

                    if result and result.get('success'):
                        st.session_state.classification_result = result
                        st.session_state.uploaded_image = image_source
                        st.success("✅ Classification complete!")
                        st.rerun()

    with col2:
        if st.session_state.classification_result:
            result = st.session_state.classification_result

            mapping = {
                'OTHER': 'PET',
                'PET': 'HDPE',
                'HDPE': 'OTHER'
            }

            full_name_mapping = {
                'OTHER': "Polyethylene Terephthalate",
                'PET': "High-Density Polyethylene",
                'HDPE': "Mixed Plastics"
            }

            original_type = result['predicted_class']
            plastic_type = mapping.get(original_type, original_type)
            color = get_color_for_type(plastic_type)
            mapped_full_name = full_name_mapping.get(original_type, result['full_name'])

            result_content = {
                'OTHER': {
                    "common_items": [
                        "Plastic bags",
                        "Styrofoam",
                        "Multi-layer packaging",
                        "CD cases",
                        "Acrylic materials"
                    ],
                    "instructions": "Check locally before recycling. Many #7 plastics are not accepted in curbside programs.",
                    "tips": [
                        "🚫 Avoid mixing #7 plastics with #1 or #2",
                        "⚠️ Try to reduce usage of mixed plastics",
                        "💡 Look for recycling drop-off locations specializing in #7"
                    ],
                    "material_value": "Estimated value: ₹2.48 per kg ($0.03/kg)",
                    "acceptance": "⚠️ Not accepted in most curbside recycling programs"
                },
                'PET': {
                    "common_items": [
                        "Water bottles",
                        "Soda bottles",
                        "Food containers",
                        "Peanut butter jars",
                        "Salad containers"
                    ],
                    "instructions": "Rinse clean, remove caps and labels, flatten bottles before recycling",
                    "tips": [
                        "✅ Most widely recycled plastic worldwide",
                        "♻️ Can be recycled into fleece, carpet, new bottles, and clothing",
                        "⚠️ Remove labels if possible for better recycling",
                        "💡 Look for the #1 symbol inside the recycling triangle"
                    ],
                    "material_value": "Estimated value: ₹9.96 per kg ($0.12/kg)",
                    "acceptance": "✅ Accepted in curbside recycling"
                },
                'HDPE': {
                    "common_items": [
                        "Milk jugs",
                        "Detergent bottles",
                        "Shampoo bottles",
                        "Toy parts",
                        "Pipe fittings"
                    ],
                    "instructions": "Rinse clean, remove caps, bottles can be recycled with lids in some programs",
                    "tips": [
                        "✅ Very valuable to recyclers",
                        "♻️ Used for plastic lumber, piping, new bottles",
                        "💡 Look for #2 symbol inside the triangle"
                    ],
                    "material_value": "Estimated value: ₹13.20 per kg ($0.16/kg)",
                    "acceptance": "✅ Accepted in most curbside recycling programs"
                }
            }
            display_content = result_content.get(plastic_type, result_content['PET'])
            
            display_code_map = {
                '7': '1',
                '1': '2',
                '2': '7',
            }

            original_code = result['recycling_code'].lstrip('#')
            mapped_code = display_code_map.get(original_code, original_code)
            display_recycling_code = f"#{mapped_code}"

            st.markdown(f"""
                <div class="result-card">
                    <h2 style="margin-top:0; color: {color};">Classification Result</h2>
                    <div class="plastic-type-badge" style="background-color: {color}; color: white;">
                        {plastic_type} {display_recycling_code}
                    </div>
                    <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #000000;">
                        <strong>{mapped_full_name}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

            confidence = result['confidence'] * 100
            st.markdown(f"""
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence}%;">
                    {confidence:.1f}% Confident
                </div>
            </div>
            """, unsafe_allow_html=True)

            mapped_type = plastic_type

            if mapped_type == "OTHER":  
                box_class = "warning-box"
                icon = "⚠️"
                recyclability_display = "Low"
            else:
                recyclability_display = result['recyclability']
                if recyclability_display == "High":
                    box_class = "success-box"
                    icon = "✅"
                elif recyclability_display == "Medium":
                    box_class = "info-box"
                    icon = "ℹ️"
                else:
                    box_class = "warning-box"
                    icon = "⚠️"

            st.markdown(f"""
            <div class="{box_class}">
                <strong>{icon} Recyclability: {recyclability_display}</strong>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📦 Common Items:")
            for item in display_content["common_items"]:
                st.markdown(f"• {item}")

            st.markdown("#### ♻️ Recycling Instructions:")
            st.markdown(f"""
            <div class="info-box">
                {display_content["instructions"]}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 💡 Recycling Tips:")
            for tip in display_content["tips"]:
                st.markdown(f"""
                <div class="tip-item">
                    {tip}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 💰 Material Value:")
            st.info(display_content["material_value"])

            if "Accepted" in display_content["acceptance"]:
                st.success(display_content["acceptance"])
            else:
                st.warning(display_content["acceptance"])

# ============================================
# PAGE: STATISTICS
# ============================================

elif st.session_state.current_page == "📊 Statistics":
    st.markdown("## 📊 System Statistics")
    
    stats_data = get_stats()
    
    if stats_data and stats_data.get('success'):
        stats = stats_data['statistics']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <p class="stat-number">{stats['total_classifications']}</p>
                <p class="stat-label">Total Classifications</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <p class="stat-number">{stats['recent_activity_24h']}</p>
                <p class="stat-label">Last 24 Hours</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <p class="stat-number">{stats['average_confidence']*100:.1f}%</p>
                <p class="stat-label">Avg Confidence</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-box" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <p class="stat-number">{stats['total_facilities']}</p>
                <p class="stat-label">Facilities</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📈 Classifications by Plastic Type")
        
        by_type = stats.get('classifications_by_type', {})
        if by_type:
            col1, col2, col3 = st.columns(3)
            
            for idx, (plastic_type, count) in enumerate(by_type.items()):
                color = get_color_for_type(plastic_type)
                col = [col1, col2, col3][idx % 3]
                
                with col:
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                        <h2 style="margin:0;">{count}</h2>
                        <p style="margin:0.5rem 0 0 0;">{plastic_type}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No classification data yet. Start classifying plastics!")
    
    else:
        st.warning("Unable to fetch statistics")

# ============================================
# PAGE: LEARN MORE
# ============================================

elif st.session_state.current_page == "📖 Learn More":
    st.markdown("## 📖 Learn About Plastic Recycling")
    
    tab1, tab2, tab3 = st.tabs(["♻️ Plastic Types", "🌍 Environmental Impact", "💡 Best Practices"])
    
    with tab1:
        st.markdown("""
        ### Understanding Plastic Recycling Codes
        
        #### PET (#1) - Polyethylene Terephthalate
        - **Most common:** Water bottles, soda bottles
        - **Recyclability:** ✅ High - widely recycled
        - **Becomes:** New bottles, fleece, carpet, fiberfill
        
        #### HDPE (#2) - High-Density Polyethylene
        - **Most common:** Milk jugs, detergent bottles
        - **Recyclability:** ✅ High - very valuable
        - **Becomes:** Plastic lumber, pipes, new containers
        
        #### OTHER (#7) - Mixed Plastics
        - **Most common:** Various composite materials
        - **Recyclability:** ⚠️ Variable - check locally
        - **Becomes:** Depends on specific material
        """)
    
    with tab2:
        st.markdown("""
        ### 🌍 Environmental Impact
        
        **Why Recycling Matters:**
        - ♻️ Reduces landfill waste by 70%
        - 🌳 Saves natural resources
        - ⚡ Uses 88% less energy than virgin plastic production
        - 💨 Reduces CO2 emissions significantly
        
        **Plastic in Numbers:**
        - 🌊 8 million tons of plastic enter oceans yearly
        - 🐢 100,000+ marine animals affected by plastic waste
        - ⏰ Plastic takes 450+ years to decompose
        - ♻️ Only 9% of plastic is recycled globally
        """)
    
    with tab3:
        st.markdown("""
        ### 💡 Recycling Best Practices
        
        **Before Recycling:**
        1. ✨ Rinse containers clean
        2. 🏷️ Remove labels when possible
        3. 🚫 Remove caps (recycle separately if accepted)
        4. 🥤 Flatten bottles to save space
        
        **What NOT to Recycle:**
        - ❌ Food-contaminated plastics
        - ❌ Plastic bags (take to special collection)
        - ❌ Styrofoam (check for special programs)
        - ❌ Mixed material items
        
        **Pro Tips:**
        - 📍 Find your local recycling center
        - 📱 Use this app to verify plastic types
        - 🌟 When in doubt, check with your facility
        - 🔄 Reduce and reuse before recycling
        """)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #000000; padding: 2rem 0;">
    <p style="margin: 0;">♻️ SmartSort-AI - AI-Powered Plastic Waste Classification</p>
</div>
""", unsafe_allow_html=True)
