import streamlit as st
import os
from ner_processor import NERProcessor

# Page configuration with better styling
st.set_page_config(
    page_title="Text Entity Extractor", 
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better text display
st.markdown("""
<style>
.entity-box {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize processors
if 'ner_processor' not in st.session_state:
    st.session_state.ner_processor = NERProcessor()

# Main title
st.title("� Text Entity Extractor")
st.markdown("Extract important information from plain text")

# Sidebar for options
with st.sidebar:
    st.header("⚙️ Information")
    
    st.markdown("**Extracted entities:**")
    st.markdown("- 👤 Names")
    st.markdown("- 📅 Dates")
    st.markdown("- 💰 Amounts")
    st.markdown("- 📍 Locations")
    st.markdown("- 🏢 Organizations")
    st.markdown("- 📞 Phone numbers")
    st.markdown("- 📧 Email addresses")
    st.markdown("- 🌐 URLs")
    st.markdown("- 🕐 Times")

# Main content area
st.subheader("✍️ Enter Text")
text_to_process = st.text_area(
    "Enter text:",
    height=300,
    help="Paste or type your text here",
    placeholder="Enter your text here..."
)

# Process button and results
if text_to_process and len(text_to_process.strip()) > 0:
    if st.button("🔍 Extract Entities", type="primary"):
        with st.spinner("Analyzing text and extracting entities..."):
            results = st.session_state.ner_processor.process_document(text_to_process)
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Extraction Results")
        
        if results.get('error'):
            st.error(f"❌ Error: {results['error']}")
        else:
            # Create columns for better layout
            col1, col2 = st.columns(2)
            
            entity_icons = {
                'names': '👤',
                'dates': '📅',
                'amounts': '💰',
                'locations': '📍',
                'organizations': '🏢',
                'phones': '📞',
                'emails': '📧',
                'urls': '🌐',
                'times': '🕐'
            }
            
            entity_labels = {
                'names': 'Names',
                'dates': 'Dates',
                'amounts': 'Amounts',
                'locations': 'Locations',
                'organizations': 'Organizations',
                'phones': 'Phone Numbers',
                'emails': 'Email Addresses',
                'urls': 'URLs',
                'times': 'Times'
            }
            
            # Display results in columns
            col_index = 0
            columns = [col1, col2]
            
            for entity_type, entities in results.items():
                if entities and entity_type != 'error':
                    with columns[col_index % 2]:
                        icon = entity_icons.get(entity_type, '📝')
                        label = entity_labels.get(entity_type, entity_type.title())
                        
                        st.markdown(f"### {icon} {label}")
                        
                        # Display entities in a nice format
                        entity_container = st.container()
                        with entity_container:
                            for entity in entities:
                                if isinstance(entity, dict):
                                    # If entity is a dict, display key info
                                    entity_text = str(entity.get('text', entity))
                                else:
                                    entity_text = str(entity)
                                
                                st.markdown(f'<div class="entity-box">• {entity_text}</div>', 
                                          unsafe_allow_html=True)
                        
                        st.markdown("")  # Add space
                    
                    col_index += 1
            
            # Summary
            total_entities = sum(len(entities) for entities in results.values() if isinstance(entities, list))
            if total_entities > 0:
                st.success(f"✅ Successfully extracted {total_entities} entities from the text!")
            else:
                st.warning("⚠️ No entities were found in the text. Make sure the text contains recognizable entities.")

else:
    st.info("👆 Please enter text to start extracting entities.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p>Text Entity Extractor | Powered by LangExtract</p>
    </div>
    """, 
    unsafe_allow_html=True
)