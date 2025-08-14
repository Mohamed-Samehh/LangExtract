import langextract as lx
import os
from typing import Dict, List

class NERProcessor:
    def __init__(self):
        """Initialize the NER processor with LangExtract (API key required)."""
        # Check if API key is available - required for operation
        self.api_key_available = bool(os.getenv('LANGEXTRACT_API_KEY'))
        
        # Define entity extraction prompt
        self.prompt = """
        Extract important entities from the text in order of appearance.
        Use exact text for extractions. Do not paraphrase or overlap entities.
        Extract: names, dates, amounts/money, locations, organizations, phone numbers, emails, URLs, times.
        For contracts, also extract: positions/job titles, ID numbers, work schedules, notice periods, governing laws.
        """
        
        # Define examples for few-shot learning
        self.examples = [
            lx.data.ExampleData(
                text="John Smith works at Microsoft Corporation in Seattle, earning $5000 monthly. His phone: 555-123-4567",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="name",
                        extraction_text="John Smith",
                        attributes={"type": "person"}
                    ),
                    lx.data.Extraction(
                        extraction_class="organization",
                        extraction_text="Microsoft Corporation",
                        attributes={"type": "company"}
                    ),
                    lx.data.Extraction(
                        extraction_class="location",
                        extraction_text="Seattle",
                        attributes={"type": "city"}
                    ),
                    lx.data.Extraction(
                        extraction_class="amount",
                        extraction_text="$5000",
                        attributes={"currency": "USD", "type": "salary"}
                    ),
                    lx.data.Extraction(
                        extraction_class="phone",
                        extraction_text="555-123-4567",
                        attributes={"type": "mobile"}
                    )
                ]
            ),
            lx.data.ExampleData(
                text="Employment Agreement dated March 15, 2024, between ABC Corp and Sarah Johnson, ID 123456789, as Software Engineer starting April 1, 2024, salary $60,000 annually, 40 hours weekly, 30 days notice required.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="date",
                        extraction_text="March 15, 2024",
                        attributes={"type": "agreement_date"}
                    ),
                    lx.data.Extraction(
                        extraction_class="organization",
                        extraction_text="ABC Corp",
                        attributes={"type": "employer"}
                    ),
                    lx.data.Extraction(
                        extraction_class="name",
                        extraction_text="Sarah Johnson",
                        attributes={"type": "employee"}
                    ),
                    lx.data.Extraction(
                        extraction_class="id_number",
                        extraction_text="123456789",
                        attributes={"type": "employee_id"}
                    ),
                    lx.data.Extraction(
                        extraction_class="position",
                        extraction_text="Software Engineer",
                        attributes={"type": "job_title"}
                    ),
                    lx.data.Extraction(
                        extraction_class="date",
                        extraction_text="April 1, 2024",
                        attributes={"type": "start_date"}
                    ),
                    lx.data.Extraction(
                        extraction_class="amount",
                        extraction_text="$60,000",
                        attributes={"currency": "USD", "type": "salary", "period": "annually"}
                    ),
                    lx.data.Extraction(
                        extraction_class="work_schedule",
                        extraction_text="40 hours weekly",
                        attributes={"type": "working_hours"}
                    ),
                    lx.data.Extraction(
                        extraction_class="notice_period",
                        extraction_text="30 days",
                        attributes={"type": "termination_notice"}
                    )
                ]
            )
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text for better extraction."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove common artifacts
        unwanted_chars = ['\uf8ff', '\ufeff', '\u200b']
        for char in unwanted_chars:
            text = text.replace(char, ' ')
        
        return text.strip()
    

    
    def process_document(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using LangExtract."""
        try:
            cleaned_text = self.clean_text(text)
            
            if not cleaned_text:
                return {
                    'error': 'No text to process',
                    'names': [], 'dates': [], 'amounts': [], 'locations': [],
                    'organizations': [], 'phones': [], 'emails': [], 'urls': [], 'times': [],
                    'positions': [], 'id_numbers': [], 'work_schedules': [], 'notice_periods': [], 'governing_laws': []
                }
            
            # LangExtract is required - no fallback
            if not self.api_key_available:
                return {
                    'error': 'LangExtract API key is required for entity extraction. Please set LANGEXTRACT_API_KEY environment variable.',
                    'names': [], 'dates': [], 'amounts': [], 'locations': [],
                    'organizations': [], 'phones': [], 'emails': [], 'urls': [], 'times': [],
                    'positions': [], 'id_numbers': [], 'work_schedules': [], 'notice_periods': [], 'governing_laws': []
                }
            
            # Use LangExtract for entity extraction
            result = lx.extract(
                text_or_documents=cleaned_text,
                prompt_description=self.prompt,
                examples=self.examples,
                model_id="gemini-2.5-flash"
            )
            
            # Convert LangExtract results to our format
            entities = {
                'names': [], 'dates': [], 'amounts': [], 'locations': [],
                'organizations': [], 'phones': [], 'emails': [], 'urls': [], 'times': [],
                'positions': [], 'id_numbers': [], 'work_schedules': [], 'notice_periods': [], 'governing_laws': []
            }
            
            if hasattr(result, 'extractions'):
                for extraction in result.extractions:
                    entity_class = getattr(extraction, 'extraction_class', 'unknown')
                    entity_text = getattr(extraction, 'extraction_text', '')
                    
                    if entity_class == 'name' and entity_text:
                        entities['names'].append(entity_text)
                    elif entity_class == 'date' and entity_text:
                        entities['dates'].append(entity_text)
                    elif entity_class == 'amount' and entity_text:
                        entities['amounts'].append(entity_text)
                    elif entity_class == 'location' and entity_text:
                        entities['locations'].append(entity_text)
                    elif entity_class == 'organization' and entity_text:
                        entities['organizations'].append(entity_text)
                    elif entity_class == 'phone' and entity_text:
                        entities['phones'].append(entity_text)
                    elif entity_class == 'email' and entity_text:
                        entities['emails'].append(entity_text)
                    elif entity_class == 'url' and entity_text:
                        entities['urls'].append(entity_text)
                    elif entity_class == 'time' and entity_text:
                        entities['times'].append(entity_text)
                    elif entity_class == 'position' and entity_text:
                        entities['positions'].append(entity_text)
                    elif entity_class == 'id_number' and entity_text:
                        entities['id_numbers'].append(entity_text)
                    elif entity_class == 'work_schedule' and entity_text:
                        entities['work_schedules'].append(entity_text)
                    elif entity_class == 'notice_period' and entity_text:
                        entities['notice_periods'].append(entity_text)
                    elif entity_class == 'governing_law' and entity_text:
                        entities['governing_laws'].append(entity_text)
            
            return entities
                
        except Exception as e:
            return {
                'error': f'LangExtract extraction failed: {str(e)}',
                'names': [], 'dates': [], 'amounts': [], 'locations': [],
                'organizations': [], 'phones': [], 'emails': [], 'urls': [], 'times': [],
                'positions': [], 'id_numbers': [], 'work_schedules': [], 'notice_periods': [], 'governing_laws': []
            }