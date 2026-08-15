import re, os

class Cleaner:
    def __init__(self):
        self.HEADER_PATTERN = re.compile(r'^(#{1,4})\s+(.+)$')   # Matches markdown headers (#, ##, ###, ####)
        self.CLEAN_TITLE_PATTERN = re.compile(r'^\d+\.?\s*')     
        self.NON_WORD_PATTERN = re.compile(r'[^\w\s.-]')
        self.SPACE_DASH_PATTERN = re.compile(r'[-\s]+')
        self.REMOVE_HEADER_PATTERN = re.compile(r'^(bibliography|acknowledgment|acknowledgments)$', re.I)

    def filename_cleaner(self, filename: str) -> str:
        cleaned = self.SPACE_DASH_PATTERN.sub('_', filename)
        cleaned = self.NON_WORD_PATTERN.sub('', cleaned)
        cleaned = os.path.splitext(cleaned)[0]
        return cleaned.strip('_').lower()
    
    def text_cleaner(self, text: str) -> str:
        text = re.sub(r'(?im)^#{1,4}\s*(references)\b.*[\s\S]*', '',text)
        return text.strip()
