import streamlit as st
import pandas as pd
import json
from datetime import datetime
import io
from ner_processor import ArabicNERProcessor

# Configure page
st.set_page_config(
    page_title="Arabic NER Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for RTL support and better Arabic text display
st.markdown("""
    <style>
    .arabic-text {
        direction: rtl;
        text-align: right;
        font-family: 'Traditional Arabic', 'Arial Unicode MS', sans-serif;
        font-size: 16px;
        line-height: 1.8;
    }
    .entity-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'processor' not in st.session_state:
        st.session_state.processor = ArabicNERProcessor()
    if 'extraction_history' not in st.session_state:
        st.session_state.extraction_history = []

def display_extraction_results(extracted_data, original_text):
    """Display the extraction results in a formatted way."""
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 نتائج الاستخراج")
        
        # Contract type
        if extracted_data['contract_type']:
            st.success(f"**نوع المستند:** {extracted_data['contract_type']}")
        
        # Names section
        if extracted_data['names']:
            st.markdown("### 👤 الأسماء المستخرجة")
            for i, name in enumerate(extracted_data['names'], 1):
                st.markdown(f"**{i}.** {name}")
        
        # Dates section
        if extracted_data['dates']:
            st.markdown("### 📅 التواريخ")
            for i, date in enumerate(extracted_data['dates'], 1):
                st.markdown(f"**{i}.** {date}")
        
        # Duration section
        if extracted_data['durations']:
            st.markdown("### ⏱️ المدة الزمنية")
            for i, duration in enumerate(extracted_data['durations'], 1):
                st.markdown(f"**{i}.** {duration}")
        
        # Amounts section
        if extracted_data['amounts']:
            st.markdown("### 💰 المبالغ المالية")
            for i, amount in enumerate(extracted_data['amounts'], 1):
                st.markdown(f"**{i}.** {amount}")
        
        # Locations section
        if extracted_data['locations']:
            st.markdown("### 📍 المواقع")
            for i, location in enumerate(extracted_data['locations'], 1):
                st.markdown(f"**{i}.** {location}")
        
        # Phone numbers section
        if extracted_data['phone_numbers']:
            st.markdown("### 📞 أرقام الهاتف")
            for i, phone in enumerate(extracted_data['phone_numbers'], 1):
                st.markdown(f"**{i}.** {phone}")
    
    with col2:
        st.subheader("📈 إحصائيات المستند")
        
        # Document statistics
        st.metric("عدد الكلمات", extracted_data['word_count'])
        st.metric("عدد الأحرف", extracted_data['text_length'])
        st.metric("اللغة المكتشفة", extracted_data['language'])
        
        # Entity counts
        st.markdown("### عدد الكيانات المستخرجة")
        entities_count = {
            'الأسماء': len(extracted_data['names']),
            'التواريخ': len(extracted_data['dates']),
            'المدد': len(extracted_data['durations']),
            'المبالغ': len(extracted_data['amounts']),
            'المواقع': len(extracted_data['locations']),
            'الهواتف': len(extracted_data['phone_numbers'])
        }
        
        for entity_type, count in entities_count.items():
            if count > 0:
                st.metric(entity_type, count)

def export_results_to_json(extracted_data, original_text):
    """Export results to JSON format."""
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'original_text_preview': original_text[:200] + "..." if len(original_text) > 200 else original_text,
        'extraction_results': extracted_data,
        'summary': st.session_state.processor.format_extraction_summary(extracted_data)
    }
    return json.dumps(export_data, ensure_ascii=False, indent=2)

def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.title("📄 مستخرج الكيانات المسماة العربية")
    st.markdown("**استخراج المعلومات المهمة من النصوص والعقود العربية**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        
        # File upload option
        uploaded_file = st.file_uploader(
            "رفع ملف نصي",
            type=['txt', 'docx', 'pdf'],
            help="يدعم ملفات النص العادي حالياً"
        )
        
        # Processing options
        st.subheader("خيارات المعالجة")
        show_confidence = st.checkbox("إظهار مستوى الثقة", value=False)
        detailed_view = st.checkbox("العرض التفصيلي", value=True)
        
        # History section
        if st.session_state.extraction_history:
            st.subheader("📚 السجل")
            for i, item in enumerate(reversed(st.session_state.extraction_history[-5:]), 1):
                with st.expander(f"استخراج {i} - {item['timestamp'][:10]}"):
                    st.text(item['text_preview'])
                    if st.button(f"استخدم هذا النص", key=f"history_{i}"):
                        st.session_state.current_text = item['original_text']
                        st.experimental_rerun()
    
    # Main content area
    tabs = st.tabs(["📝 إدخال النص", "📊 النتائج", "📋 التقرير"])
    
    with tabs[0]:
        st.subheader("أدخل النص العربي للمعالجة")
        
        # Text input methods
        input_method = st.radio(
            "طريقة الإدخال:",
            ["كتابة مباشرة", "رفع ملف"],
            horizontal=True
        )
        
        text_input = ""
        
        if input_method == "كتابة مباشرة":
            text_input = st.text_area(
                "النص العربي:",
                height=300,
                placeholder="الرجاء إدخال النص العربي هنا...",
                help="يمكنك نسخ ولصق العقد أو المستند هنا"
            )
        
        elif input_method == "رفع ملف" and uploaded_file:
            try:
                # Handle different file types
                if uploaded_file.type == "text/plain":
                    text_input = str(uploaded_file.read(), "utf-8")
                else:
                    st.warning("نوع الملف غير مدعوم حالياً. يرجى استخدام ملف نصي (.txt)")
            except Exception as e:
                st.error(f"خطأ في قراءة الملف: {e}")
        
        # Sample texts for testing
        with st.expander("🧪 نصوص تجريبية"):
            sample_contract = """
            عقد عمل
            
            بين السيد أحمد محمد علي (الطرف الأول) والشركة السعودية للتطوير (الطرف الثاني)
            
            بتاريخ 15/03/2024، تم الاتفاق على عقد عمل لمدة سنتين براتب شهري قدره 8000 ريال سعودي.
            
            مكان العمل: الرياض، المملكة العربية السعودية
            هاتف: +966501234567
            
            يبدأ العمل في 1/04/2024 وينتهي في 31/03/2026.
            """
            
            if st.button("استخدام النص التجريبي"):
                text_input = sample_contract
                st.experimental_rerun()
        
        # Process button
        if st.button("🔍 معالجة النص", type="primary", disabled=not text_input.strip()):
            if text_input.strip():
                with st.spinner("جاري معالجة النص..."):
                    try:
                        # Process the document
                        extracted_data = st.session_state.processor.process_document(text_input)
                        
                        # Store in session state
                        st.session_state.current_extraction = extracted_data
                        st.session_state.current_text = text_input
                        
                        # Add to history
                        history_item = {
                            'timestamp': datetime.now().isoformat(),
                            'text_preview': text_input[:100] + "...",
                            'original_text': text_input,
                            'extraction_data': extracted_data
                        }
                        st.session_state.extraction_history.append(history_item)
                        
                        st.success("تم استخراج المعلومات بنجاح!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء المعالجة: {e}")
    
    with tabs[1]:
        if 'current_extraction' in st.session_state:
            display_extraction_results(
                st.session_state.current_extraction,
                st.session_state.current_text
            )
            
            # Export options
            st.subheader("📥 تصدير النتائج")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 تصدير JSON"):
                    json_data = export_results_to_json(
                        st.session_state.current_extraction,
                        st.session_state.current_text
                    )
                    st.download_button(
                        label="تحميل ملف JSON",
                        data=json_data,
                        file_name=f"extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("📊 تصدير CSV"):
                    # Create a simple CSV with extracted entities
                    df_data = []
                    for entity_type, entities in {
                        'Names': st.session_state.current_extraction['names'],
                        'Dates': st.session_state.current_extraction['dates'],
                        'Durations': st.session_state.current_extraction['durations'],
                        'Amounts': st.session_state.current_extraction['amounts'],
                        'Locations': st.session_state.current_extraction['locations'],
                        'Phone Numbers': st.session_state.current_extraction['phone_numbers']
                    }.items():
                        for entity in entities:
                            df_data.append({'Entity Type': entity_type, 'Value': entity})
                    
                    if df_data:
                        df = pd.DataFrame(df_data)
                        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="تحميل ملف CSV",
                            data=csv_data,
                            file_name=f"extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
        else:
            st.info("👈 الرجاء معالجة نص أولاً من تبويب 'إدخال النص'")
    
    with tabs[2]:
        if 'current_extraction' in st.session_state:
            st.subheader("📋 تقرير الاستخراج")
            
            # Generate summary
            summary = st.session_state.processor.format_extraction_summary(
                st.session_state.current_extraction
            )
            
            st.markdown("### الملخص")
            st.markdown(f'<div class="arabic-text">{summary}</div>', unsafe_allow_html=True)
            
            # Detailed breakdown
            st.markdown("### التفاصيل الكاملة")
            with st.expander("عرض البيانات الخام"):
                st.json(st.session_state.current_extraction)
        else:
            st.info("👈 الرجاء معالجة نص أولاً من تبويب 'إدخال النص'")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        تم تطوير هذا التطبيق لاستخراج الكيانات المسماة من النصوص العربية
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()