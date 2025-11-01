import streamlit as st
import pandas as pd
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.data_loader import DataLoader
from backend.query_parser import QueryParser
from backend.search_engine import SearchEngine
from backend.summarizer import Summarizer

# Page config
st.set_page_config(
    page_title="Property Search Assistant",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple, clean CSS
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Property card with light background */
    .property-card {
        background: #ffffff;
        border: 2px solid #c9b1b1;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .property-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-color: #4CAF50;
    }
    
    .property-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1976D2;
        margin-bottom: 0.5rem;
    }
    
    .property-price {
        font-size: 1.6rem;
        font-weight: bold;
        color: #2E7D32;
        margin: 0.5rem 0;
    }
    
    .property-details {
        color: #424242;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0.75rem 0;
    }
    
    .amenity-tag {
        display: inline-block;
        background: #E3F2FD;
        color: #1565C0;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        margin: 0.25rem;
        font-size: 0.85rem;
        border: 1px solid #90CAF9;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.75rem 0;
    }
    
    .user-message {
        background: #000000;
        border: 2px solid #4CAF50;
        color: #ffffff;
    }
    
    .bot-message {
        background: #000000;
        border: 2px solid #4CAF50;
        color: #ffffff;
    }
    
    /* View button */
    .view-btn {
        display: inline-block;
        margin-top: 0.75rem;
        padding: 0.6rem 1.2rem;
        background: #1976D2;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        font-weight: 500;
    }
    
    .view-btn:hover {
        background: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None

# Load data
@st.cache_data
def load_data():
    loader = DataLoader(data_dir='data')
    return loader.load_and_merge()

# Initialize components
if not st.session_state.data_loaded:
    with st.spinner("Loading property data..."):
        st.session_state.df = load_data()
        st.session_state.data_loaded = True

parser = QueryParser()
search_engine = SearchEngine(st.session_state.df)
summarizer = Summarizer()

# Header
st.title("🏠 Property Search Assistant")
st.markdown("Find your dream property")

# Stats (only 3 metrics, removed Cities)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Total Properties", len(st.session_state.df))

with col2:
    st.metric("💰 Avg Price", f"₹{st.session_state.df['price_cr'].mean():.2f} Cr")

with col3:
    ready_count = len(st.session_state.df[st.session_state.df['status'].str.contains('Ready', na=False)])
    st.metric("🏗️ Ready to Move", ready_count)

st.divider()

# Example queries
st.subheader("💡 Try These Queries")

example_queries = [
    "3BHK apartments in Mumbai under 2 Cr",
    "Ready to move 2BHK in Pune",
    "Apartments under 1.5 Cr",
]

cols = st.columns(3)
for idx, query in enumerate(example_queries):
    with cols[idx % 3]:
        if st.button(query, key=f"example_{idx}", use_container_width=True):
            st.session_state.example_query = query
            st.rerun()

st.divider()

# Display chat history
for message in st.session_state.messages:
    if message['role'] == 'user':
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 Assistant:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
        
        # Display property cards
        if 'properties' in message and message['properties']:
            for i in range(0, len(message['properties']), 2):
                col1, col2 = st.columns(2)
                
                # First property
                if i < len(message['properties']):
                    prop = message['properties'][i]
                    with col1:
                        st.markdown(f"""
                        <div class="property-card">
                            <div class="property-title">{prop['title']}</div>
                            <div class="property-price">{prop['price']}</div>
                            <div class="property-details">
                                <strong>📍 Location:</strong> {prop['location']}<br>
                                <strong>🛏️ Configuration:</strong> {prop['bhk']}<br>
                                <strong>📏 Carpet Area:</strong> {prop['carpet_area']} sq.ft<br>
                                <strong>🏗️ Status:</strong> {prop['status']}
                            </div>
                            <div style="margin-top: 10px;">
                                {''.join([f'<span class="amenity-tag">{amenity}</span>' for amenity in prop['amenities']])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Second property
                if i + 1 < len(message['properties']):
                    prop = message['properties'][i + 1]
                    with col2:
                        st.markdown(f"""
                        <div class="property-card">
                            <div class="property-title">{prop['title']}</div>
                            <div class="property-price">{prop['price']}</div>
                            <div class="property-details">
                                <strong>📍 Location:</strong> {prop['location']}<br>
                                <strong>🛏️ Configuration:</strong> {prop['bhk']}<br>
                                <strong>📏 Carpet Area:</strong> {prop['carpet_area']} sq.ft<br>
                                <strong>🏗️ Status:</strong> {prop['status']}
                            </div>
                            <div style="margin-top: 10px;">
                                {''.join([f'<span class="amenity-tag">{amenity}</span>' for amenity in prop['amenities']])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

# Handle example query click
if 'example_query' in st.session_state and st.session_state.example_query:
    user_query = st.session_state.example_query
    st.session_state.example_query = None
else:
    # Chat input
    user_query = st.chat_input("Ask me about properties... (e.g., '2BHK in Mumbai under 1.5 Cr')")

if user_query:
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': user_query
    })
    
    # Parse query
    filters = parser.parse(user_query)
    
    # Search
    results = search_engine.search(filters, top_n=10)
    
    # If no results, try expanding search
    expanded = None
    if results.empty:
        results, expanded = search_engine.expand_search(filters)
    
    # Get statistics
    stats = search_engine.get_statistics(results, filters)
    
    # Generate summary
    summary = summarizer.generate_summary(results, filters, stats, expanded)
    
    # Format property cards
    property_cards = []
    for _, row in results.iterrows():
        property_cards.append(summarizer.format_property_card(row))
    
    # Add bot response
    st.session_state.messages.append({
        'role': 'assistant',
        'content': summary,
        'properties': property_cards[:6]
    })
    
    # Rerun to update UI
    st.rerun()