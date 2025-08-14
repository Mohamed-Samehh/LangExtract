import re
from datetime import datetime
from typing import Dict, List, Optional
import langdetect
from langextract import extract
import spacy

class ArabicNERProcessor:
    def __init__(self):
        """Initialize the Arabic NER processor with patterns and configurations."""
        
        # Arabic date patterns
        self.date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # DD/MM/YYYY or DD-MM-YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD or YYYY-MM-DD
            r'\d{1,2}\s+\w+\s+\d{4}',        # DD Month YYYY in Arabic
            r'في\s+\d{1,2}\s+\w+\s+\d{4}',  # في DD Month YYYY
            r'بتاريخ\s+\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # بتاريخ DD/MM/YYYY
        ]
        
        # Arabic duration patterns
        self.duration_patterns = [
            r'لمدة\s+(\d+)\s*(سنة|شهر|يوم|أسبوع)',
            r'(\d+)\s*(سنة|شهر|يوم|أسبوع)',
            r'مدة\s+(\d+)\s*(سنة|شهر|يوم|أسبوع)',
            r'فترة\s+(\d+)\s*(سنة|شهر|يوم|أسبوع)',
        ]
        
        # Arabic name indicators
        self.name_indicators = [
            r'السيد\s+([^\s]+(?:\s+[^\s]+)*)',
            r'السيدة\s+([^\s]+(?:\s+[^\s]+)*)',
            r'الأستاذ\s+([^\s]+(?:\s+[^\s]+)*)',
            r'الدكتور\s+([^\s]+(?:\s+[^\s]+)*)',
            r'المهندس\s+([^\s]+(?:\s+[^\s]+)*)',
            r'اسم\s*:\s*([^\n]+)',
            r'الاسم\s*:\s*([^\n]+)',
            r'المتعاقد\s*:\s*([^\n]+)',
            r'الطرف الأول\s*:\s*([^\n]+)',
            r'الطرف الثاني\s*:\s*([^\n]+)',
        ]
        
        # Money/amount patterns
        self.money_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(ريال|دولار|دينار|درهم|جنيه)',
            r'مبلغ\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(ريال|دولار|دينار|درهم|جنيه)',
            r'قيمة\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(ريال|دولار|دينار|درهم|جنيه)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*من\s*(الريالات|الدولارات|الدنانير|الدراهم)',
        ]
        
        # Contract type indicators
        self.contract_types = [
            'عقد عمل', 'عقد إيجار', 'عقد بيع', 'عقد شراء', 'عقد خدمات',
            'اتفاقية', 'بروتوكول', 'مذكرة تفاهم', 'عقد مقاولة', 'عقد توريد'
        ]
        
        # Location patterns
        self.location_patterns = [
            r'في\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s*،|\s*\.|\s*$)',
            r'بمدينة\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s*،|\s*\.|\s*$)',
            r'بمحافظة\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s*،|\s*\.|\s*$)',
            r'العنوان\s*:\s*([^\n]+)',
        ]

    def detect_language(self, text: str) -> str:
        """Detect if the text is in Arabic."""
        try:
            detected = langdetect.detect(text)
            return detected
        except:
            # Fallback: check for Arabic characters
            arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
            total_chars = len([char for char in text if char.isalpha()])
            if total_chars > 0 and arabic_chars / total_chars > 0.5:
                return 'ar'
            return 'unknown'

    def extract_names(self, text: str) -> List[str]:
        """Extract names from Arabic text."""
        names = []
        
        for pattern in self.name_indicators:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if name and len(name.split()) <= 4:  # Reasonable name length
                    names.append(name)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(names))

    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from Arabic text."""
        dates = []
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append(match.group(0).strip())
        
        return list(dict.fromkeys(dates))

    def extract_durations(self, text: str) -> List[str]:
        """Extract duration information from Arabic text."""
        durations = []
        
        for pattern in self.duration_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                durations.append(match.group(0).strip())
        
        return list(dict.fromkeys(durations))

    def extract_money_amounts(self, text: str) -> List[str]:
        """Extract money amounts from Arabic text."""
        amounts = []
        
        for pattern in self.money_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amounts.append(match.group(0).strip())
        
        return list(dict.fromkeys(amounts))

    def extract_locations(self, text: str) -> List[str]:
        """Extract locations from Arabic text."""
        locations = []
        
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                if location and len(location.split()) <= 3:
                    locations.append(location)
        
        return list(dict.fromkeys(locations))

    def identify_contract_type(self, text: str) -> Optional[str]:
        """Identify the type of contract."""
        text_lower = text.lower()
        
        for contract_type in self.contract_types:
            if contract_type in text_lower:
                return contract_type
        
        return None

    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers."""
        phone_patterns = [
            r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'هاتف\s*:\s*([+\d\s-()]+)',
            r'جوال\s*:\s*([+\d\s-()]+)',
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                phone = match.group(0).strip() if 'هاتف' not in pattern and 'جوال' not in pattern else match.group(1).strip()
                phones.append(phone)
        
        return list(dict.fromkeys(phones))

    def process_document(self, text: str) -> Dict[str, any]:
        """Process the entire document and extract all relevant information."""
        
        # Detect language
        language = self.detect_language(text)
        
        # Extract information
        extracted_data = {
            'language': language,
            'names': self.extract_names(text),
            'dates': self.extract_dates(text),
            'durations': self.extract_durations(text),
            'amounts': self.extract_money_amounts(text),
            'locations': self.extract_locations(text),
            'contract_type': self.identify_contract_type(text),
            'phone_numbers': self.extract_phone_numbers(text),
            'text_length': len(text),
            'word_count': len(text.split()),
        }
        
        # Use langextract for additional entity extraction if available
        try:
            lang_extracted = extract(text)
            if hasattr(lang_extracted, 'entities'):
                extracted_data['additional_entities'] = lang_extracted.entities
        except Exception as e:
            extracted_data['langextract_error'] = str(e)
        
        return extracted_data

    def format_extraction_summary(self, extracted_data: Dict[str, any]) -> str:
        """Format the extracted data into a readable summary."""
        summary = []
        
        if extracted_data['contract_type']:
            summary.append(f"نوع العقد: {extracted_data['contract_type']}")
        
        if extracted_data['names']:
            summary.append(f"الأسماء المستخرجة: {', '.join(extracted_data['names'])}")
        
        if extracted_data['dates']:
            summary.append(f"التواريخ: {', '.join(extracted_data['dates'])}")
        
        if extracted_data['durations']:
            summary.append(f"المدة: {', '.join(extracted_data['durations'])}")
        
        if extracted_data['amounts']:
            summary.append(f"المبالغ: {', '.join(extracted_data['amounts'])}")
        
        if extracted_data['locations']:
            summary.append(f"المواقع: {', '.join(extracted_data['locations'])}")
        
        if extracted_data['phone_numbers']:
            summary.append(f"أرقام الهاتف: {', '.join(extracted_data['phone_numbers'])}")
        
        return '\n'.join(summary) if summary else "لم يتم العثور على معلومات محددة"