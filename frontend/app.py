"""
SmartSort-AI - Streamlit Frontend
Beautiful, modern UI for AI-powered plastic waste classification
"""

import streamlit as st
import requests
from PIL import Image
import io
import json
from datetime import datetime
import base64

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="SmartSort-AI - AI Plastic Classifier",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-green: #2E7D32;
        --secondary-blue: #1976D2;
        --accent-orange: #F57C00;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Result card styling */
    .result-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid var(--primary-green);
    }
    
    .plastic-type-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.3rem;
        margin: 1rem 0;
    }
    
    .confidence-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 30px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        transition: width 0.5s ease;
    }
    
    /* Facility card */
    .facility-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1976D2;
    }
    
    .facility-card h4 {
        margin: 0 0 0.5rem 0;
        color: #1976D2;
    }
    
    /* Info boxes */
    .info-box {
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196F3;
    }
    
    .warning-box {
        background: #FFF3E0;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #FF9800;
    }
    
    .success-box {
        background: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #4CAF50;
    }
    
    /* Tip items */
    .tip-item {
        background: white;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Stats styling */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Camera upload styling */
    .uploadedFile {
        border: 2px dashed #2E7D32;
        border-radius: 10px;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONFIGURATION
# ============================================

API_URL = "http://localhost:8000"

# Initialize session state
if 'classification_result' not in st.session_state:
    st.session_state.classification_result = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'history' not in st.session_state:
    st.session_state.history = []

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

def get_facilities(latitude, longitude, plastic_type=None, radius_km=10):
    """Get nearby recycling facilities"""
    try:
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'radius_km': radius_km
        }
        if plastic_type:
            params['plastic_type'] = plastic_type
        
        response = requests.get(f"{API_URL}/facilities", params=params)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
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
    <p>AI-Powered Plastic Waste Classification System</p>
    <p style="font-size: 0.9rem; margin-top: 0.5rem;">
        📸 Upload a photo → 🤖 Get instant classification → 📍 Find recycling locations
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Navigation")
    
    page = st.radio(
        "Choose a page:",
        ["🏠 Classify Plastic", "📊 Statistics", "📍 Find Facilities", "📖 Learn More"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Settings")
    
    # Location settings
    with st.expander("📍 Location Settings"):
        use_location = st.checkbox("Use my location for facility search", value=True)
        
        if use_location:
            latitude = st.number_input("Latitude", value=12.9716, format="%.4f")
            longitude = st.number_input("Longitude", value=77.5946, format="%.4f")
            st.caption("📍 Default: Bengaluru, Karnataka")
        else:
            latitude = None
            longitude = None
    
    st.markdown("---")
    
    # System status
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

if page == "🏠 Classify Plastic":
    
    st.markdown("## 📸 Upload Plastic Waste Image")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h4 style="margin-top:0;">📋 How to Use:</h4>
            <ol style="margin-bottom:0;">
                <li>Take a clear photo of the plastic item</li>
                <li>Make sure the recycling symbol is visible (if present)</li>
                <li>Upload the image below</li>
                <li>Get instant classification results!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear photo of plastic waste"
        )
        
        # Camera input
        camera_image = st.camera_input("Or take a photo with your camera")
        
        # Use camera image if available, otherwise uploaded file
        image_source = camera_image if camera_image else uploaded_file
        
        if image_source:
            # Display image
            image = Image.open(image_source)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Classify button
            if st.button("🔍 Classify Plastic", use_container_width=True):
                with st.spinner("🤖 Analyzing image..."):
                    # Reset file pointer
                    image_source.seek(0)
                    
                    # Classify
                    result = classify_image(
                        image_source,
                        latitude if use_location else None,
                        longitude if use_location else None
                    )
                    
                    if result and result.get('success'):
                        st.session_state.classification_result = result
                        st.session_state.uploaded_image = image
                        st.success("✅ Classification complete!")
                        st.rerun()
    
    with col2:
        if st.session_state.classification_result:
            result = st.session_state.classification_result
            
            # Plastic type badge
            plastic_type = result['predicted_class']
            color = get_color_for_type(plastic_type)
            
            st.markdown(f"""
            <div class="result-card">
                <h2 style="margin-top:0; color: {color};">Classification Result</h2>
                <div class="plastic-type-badge" style="background-color: {color}; color: white;">
                    {plastic_type} {result['recycling_code']}
                </div>
                <p style="font-size: 1.1rem; margin: 0.5rem 0;">
                    <strong>{result['full_name']}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Confidence bar
            confidence = result['confidence'] * 100
            st.markdown(f"""
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence}%;>
                    {confidence:.1f}% Confident
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recyclability info
            recyclability = result['recyclability']
            if recyclability == "High":
                box_class = "success-box"
                icon = "✅"
            elif recyclability == "Medium":
                box_class = "info-box"
                icon = "ℹ️"
            else:
                box_class = "warning-box"
                icon = "⚠️"
            
            st.markdown(f"""
            <div class="{box_class}">
                <strong>{icon} Recyclability: {recyclability}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Common items
            st.markdown("#### 📦 Common Items:")
            for item in result['common_items']:
                st.markdown(f"• {item}")
            
            # Recycling instructions
            st.markdown("#### ♻️ Recycling Instructions:")
            st.markdown(f"""
            <div class="info-box">
                {result['instructions']}
            </div>
            """, unsafe_allow_html=True)
            
            # Tips
            st.markdown("#### 💡 Recycling Tips:")
            for tip in result['tips']:
                st.markdown(f"""
                <div class="tip-item">
                    {tip}
                </div>
                """, unsafe_allow_html=True)
            
            # Value
            st.markdown("#### 💰 Material Value:")
            st.info(f"Estimated value: **₹{result['value_per_kg'] * 83:.2f}** per kg (${result['value_per_kg']:.2f}/kg)")
            
            # Curbside acceptance
            if result['curbside_accepted']:
                st.success("✅ Accepted in curbside recycling")
            else:
                st.warning("⚠️ Not accepted in curbside - needs special drop-off")
            
            # Nearby facilities
            if result.get('nearest_facilities'):
                st.markdown("#### 📍 Nearest Recycling Facilities:")
                for facility in result['nearest_facilities'][:3]:
                    st.markdown(f"""
                    <div class="facility-card">
                        <h4>{facility['name']}</h4>
                        <p style="margin:0;">📍 {facility['distance_km']} km away</p>
                        <p style="margin:0.3rem 0 0 0; color: #666;">{facility['address']}</p>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================
# PAGE: STATISTICS
# ============================================

elif page == "📊 Statistics":
    st.markdown("## 📊 System Statistics")
    
    stats_data = get_stats()
    
    if stats_data and stats_data.get('success'):
        stats = stats_data['statistics']
        
        # Top row metrics
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
        
        # Classifications by type
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
# PAGE: FIND FACILITIES
# ============================================

elif page == "📍 Find Facilities":
    st.markdown("## 📍 Find Recycling Facilities")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_lat = st.number_input("Latitude", value=12.9716 if use_location else 0.0, format="%.4f")
        search_lon = st.number_input("Longitude", value=77.5946 if use_location else 0.0, format="%.4f")
    
    with col2:
        search_radius = st.slider("Search Radius (km)", 1, 50, 10)
        plastic_filter = st.selectbox("Filter by plastic type", ["All", "PET", "HDPE", "OTHER"])
    
    if st.button("🔍 Search Facilities", use_container_width=True):
        with st.spinner("Searching..."):
            filter_type = None if plastic_filter == "All" else plastic_filter
            facilities_data = get_facilities(search_lat, search_lon, filter_type, search_radius)
            
            if facilities_data and facilities_data.get('success'):
                facilities = facilities_data['facilities']
                
                st.success(f"✅ Found {len(facilities)} facilities within {search_radius} km")
                
                for facility in facilities:
                    st.markdown(f"""
                    <div class="facility-card">
                        <h3 style="margin-top:0; color: #1976D2;">{facility['name']}</h3>
                        <p><strong>📍 Distance:</strong> {facility['distance_km']} km</p>
                        <p><strong>📫 Address:</strong> {facility['address']}</p>
                        <p><strong>♻️ Accepts:</strong> {', '.join(facility['accepts_types'])}</p>
                        {f"<p><strong>📞 Phone:</strong> {facility['phone']}</p>" if facility.get('phone') else ""}
                        {f"<p><strong>🕒 Hours:</strong> {facility['hours']}</p>" if facility.get('hours') else ""}
                        {f"<p><strong>🌐 Website:</strong> <a href='{facility['website']}' target='_blank'>{facility['website']}</a></p>" if facility.get('website') else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No facilities found in this area")

# ============================================
# PAGE: LEARN MORE
# ============================================

elif page == "📖 Learn More":
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
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p style="margin: 0;">♻️ SmartSort-AI - AI-Powered Plastic Waste Classification</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
        Built with ❤️ using TensorFlow, FastAPI, and Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
