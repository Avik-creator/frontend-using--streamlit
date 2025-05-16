from datetime import date, datetime
import re
from difflib import get_close_matches
import logging
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRDateParser:
    """Robust date parser that handles OCR errors in dates and month names"""
    
    # Common OCR errors mapping (both full and abbreviated month names)
    OCR_MONTH_MAPPING = {
        # Full month names
        'detember': 'december',
        'septembar': 'september',
        'januery': 'january',
        'feburary': 'february',
        
        # Abbreviated month names
        'det': 'dec',
        'jat': 'jan',
        'feb': 'feb',  # Common correct abbreviation
        'mar': 'mar',
        'apl': 'apr',
        'may': 'may',
        'jun': 'jun',
        'jul': 'jul',
        'aug': 'aug',
        'sep': 'sep',
        'oct': 'oct',
        'nov': 'nov',
        'dec': 'dec',
    }

    # Month name variations (including common misspellings)
    MONTH_VARIANTS = {
        'january': ['jan', 'january', 'januery', 'janry', 'jaunary'],
        'february': ['feb', 'february', 'feburary', 'febry'],
        'march': ['mar', 'march'],
        'april': ['apr', 'april', 'aprl'],
        'may': ['may'],
        'june': ['jun', 'june'],
        'july': ['jul', 'july'],
        'august': ['aug', 'august'],
        'september': ['sep', 'september', 'sept', 'septembar'],
        'october': ['oct', 'october'],
        'november': ['nov', 'november'],
        'december': ['dec', 'december', 'detember']
    }

    @classmethod
    def correct_ocr_month(cls, month_str: str) -> str:
        """Correct OCR errors in month names with fuzzy matching"""
        original = month_str.lower().strip()
        
        # First try exact match in our OCR mapping
        if original in cls.OCR_MONTH_MAPPING:
            corrected = cls.OCR_MONTH_MAPPING[original]
            if corrected != original:
                logger.info(f"Corrected month '{original}' to '{corrected}'")
            return corrected
        
        # Try fuzzy matching with known month variants
        for correct_name, variants in cls.MONTH_VARIANTS.items():
            if original in variants:
                return correct_name[:3]  # Return abbreviated form
            
        # Use difflib for fuzzy matching
        all_month_names = list(cls.MONTH_VARIANTS.keys())
        matches = get_close_matches(original, all_month_names, n=1, cutoff=0.6)
        if matches:
            logger.info(f"Fuzzy matched month '{original}' to '{matches[0]}'")
            return matches[0][:3]  # Return abbreviated form
        
        # If still no match, try matching just first 3 characters
        if len(original) >= 3:
            first_three = original[:3]
            for correct_name in cls.MONTH_VARIANTS:
                if correct_name.startswith(first_three):
                    return correct_name[:3]
        
        logger.warning(f"Unable to correct month: '{original}'")
        return original  # Return as-is, let datetime parsing handle it

    @classmethod
    def parse_date_part(cls, date_part: str) -> Optional[int]:
        """Parse a date part (day, month, or year) with OCR error handling"""
        try:
            # Remove common OCR artifacts
            cleaned = re.sub(r'[^0-9]', '', date_part)
            return int(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None

    @classmethod
    def parse_date_string(cls, date_str: str) -> Optional[Tuple[date, date]]:
        """Parse a date range string with robust OCR error handling"""
        try:
            # Normalize the string first
            date_str = date_str.strip()
            
            # Handle date range
            if "-" in date_str:
                parts = [p.strip() for p in date_str.split("-", 1)]
                start_date = cls.parse_single_date(parts[0])
                end_date = cls.parse_single_date(parts[1])
                return start_date, end_date
            else:
                single_date = cls.parse_single_date(date_str)
                return single_date, datetime.now().date()
        except Exception as e:
            logger.error(f"Failed to parse date string '{date_str}': {str(e)}")
            return None

    @classmethod
    def parse_single_date(cls, date_str: str) -> Optional[date]:
        """Parse a single date with OCR error handling"""
        # Try multiple date format patterns
        patterns = [
            r'(?P<month>[a-zA-Z]+)\s*(?P<year>\d{4})',  # "Jan 2020" or "January2020"
            r'(?P<year>\d{4})\s*(?P<month>[a-zA-Z]+)',  # "2020 Jan" or "2020January"
            r'(?P<month>\d{1,2})/(?P<year>\d{4})',      # "1/2020" or "01/2020"
            r'(?P<year>\d{4})/(?P<month>\d{1,2})',      # "2020/1" or "2020/01"
            r'(?P<year>\d{4})',                         # Just year "2020"
        ]

        for pattern in patterns:
            match = re.match(pattern, date_str, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                year = cls.parse_date_part(groups.get('year', ''))
                month_str = groups.get('month', '1')
                
                # Handle month parsing
                month = 1  # Default to January if month can't be determined
                if month_str:
                    if month_str.isdigit():
                        month = int(month_str)
                    else:
                        # Handle text month names with OCR correction
                        corrected_month = cls.correct_ocr_month(month_str)
                        try:
                            month = datetime.strptime(corrected_month[:3], '%b').month
                        except ValueError:
                            try:
                                month = datetime.strptime(corrected_month, '%B').month
                            except ValueError:
                                logger.warning(f"Could not parse month: {month_str}")
                                month = 1
                
                # Validate and return date
                if year:
                    try:
                        return str(month) + str(year)
                    except ValueError as e:
                        logger.warning(f"Invalid date {year}-{month}-1: {str(e)}")
                        continue
        
        logger.warning(f"Could not parse date string: {date_str}")
        return None



def parse_date_range(date_range):
    """Wrapper for the robust OCR date parser"""
    result = OCRDateParser.parse_date_string(date_range)
    if result:
        start_date, end_date = result
        # Ensure chronological order
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        return start_date, end_date
    else:
        # Fallback to current date if parsing fails
        today = datetime.now().date()
        return today, today

def month_from_name(date_pass):
    """Backward-compatible wrapper"""
    result = OCRDateParser.parse_single_date(date_pass)
    return result if result else date(1900, 1, 1)  # Safe default

