import streamlit as st
import os
from ner_processor import ArabicNERProcessor
from pdf_processor import PDFProcessor

# Page configuration with better styling
st.set_page_config(
    page_title="Arabic Document Entity Extractor", 
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better Arabic text display
st.markdown("""
<style>
.arabic-text {
    direction: rtl;
    text-align: right;
    font-family: 'Arial Unicode MS', Tahoma, sans-serif;
}
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
    st.session_state.ner_processor = ArabicNERProcessor()

if 'pdf_processor' not in st.session_state:
    st.session_state.pdf_processor = PDFProcessor()

# Main title
st.title("📄 Arabic Document Entity Extractor")
st.markdown("Extract important information from Arabic documents (PDF, DOCX, TXT) or plain text")

# API Key Setup Warning
if not os.getenv('LANGEXTRACT_API_KEY'):
    st.error("""
    🚫 **LangExtract API Key Required**
    
    This application requires a Google AI API key to function:
    1. Get your API key from [Google AI Studio](https://aistudio.google.com/)
    2. Create a `.env` file in your project folder with: `LANGEXTRACT_API_KEY=your-api-key-here`
    3. Or set environment variable: `export LANGEXTRACT_API_KEY=your-api-key-here`
    
    **The application cannot extract entities without this API key.**
    """)
    st.stop()  # Stop execution if no API key
else:
    st.success("✅ LangExtract API key configured. AI-powered extraction ready!")

# Sidebar for options
with st.sidebar:
    st.header("⚙️ Options")
    input_method = st.radio(
        "Choose input method:",
        ["Upload Document", "Enter Text Manually"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("**Supported file types:**")
    st.markdown("- PDF files")
    st.markdown("- Word documents (.docx)")
    st.markdown("- Text files (.txt)")
    
    st.markdown("---")
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
text_to_process = None

if input_method == "Upload Document":
    st.subheader("📁 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt'],
        help="Upload a PDF, Word document, or text file containing Arabic text"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Extract text from file
        with st.spinner("Extracting text from document..."):
            text_to_process = st.session_state.pdf_processor.process_uploaded_file(uploaded_file)
        
        if text_to_process:
            # Show extracted text in an expander
            with st.expander("📖 View Extracted Text", expanded=False):
                st.markdown(f'<div class="arabic-text">{text_to_process}</div>', unsafe_allow_html=True)
            
            st.info(f"Extracted {len(text_to_process)} characters from the document")
        else:
            st.error("Failed to extract text from the document")

else:  # Manual text input
    st.subheader("✍️ Enter Arabic Text")
    text_to_process = st.text_area(
        "Enter Arabic text:",
        height=300,
        help="Paste or type your Arabic text here",
        placeholder="أدخل النص العربي هنا..."
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
                'names': 'Names (الأسماء)',
                'dates': 'Dates (التواريخ)',
                'amounts': 'Amounts (المبالغ)',
                'locations': 'Locations (الأماكن)',
                'organizations': 'Organizations (المؤسسات)',
                'phones': 'Phone Numbers (أرقام الهاتف)',
                'emails': 'Email Addresses (البريد الإلكتروني)',
                'urls': 'URLs (الروابط)',
                'times': 'Times (الأوقات)'
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
                                
                                st.markdown(f'<div class="entity-box arabic-text">• {entity_text}</div>', 
                                          unsafe_allow_html=True)
                        
                        st.markdown("")  # Add space
                    
                    col_index += 1
            
            # Summary
            total_entities = sum(len(entities) for entities in results.values() if isinstance(entities, list))
            if total_entities > 0:
                st.success(f"✅ Successfully extracted {total_entities} entities from the text!")
            else:
                st.warning("⚠️ No entities were found in the text. Make sure the text contains recognizable Arabic entities.")

else:
    st.info("👆 Please upload a document or enter text to start extracting entities.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p>Arabic Document Entity Extractor | Powered by LangExtract</p>
    </div>
    """, 
    unsafe_allow_html=True
)