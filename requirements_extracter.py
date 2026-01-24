# requirements_extractor.py
# Extracts key requirements from job descriptions WITHOUT storing full text

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Set

class RequirementsExtractor:
    """Extracts structured requirements from job postings"""
    
    # Common tech skills patterns
    TECH_SKILLS = {
        'languages': ['python', 'javascript', 'java', 'typescript', 'go', 'rust', 
                     'c\\+\\+', 'ruby', 'php', 'swift', 'kotlin', 'scala'],
        'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'spring', 
                      'node\\.?js', 'express', 'fastapi', 'rails', 'laravel'],
        'tools': ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'jenkins', 
                 'git', 'jira', 'figma', 'postgres', 'mongodb', 'redis'],
        'concepts': ['machine learning', 'ml', 'ai', 'devops', 'agile', 'scrum',
                    'microservices', 'rest api', 'graphql', 'ci/cd', 'tdd']
    }
    
    # Experience patterns
    EXP_PATTERNS = [
        r'(\d+)\+?\s*(?:years?|yrs?).*?(?:experience|exp)',
        r'(?:experience|exp).*?(\d+)\+?\s*(?:years?|yrs?)',
        r'minimum\s+(\d+)\s+years?',
        r'at\s+least\s+(\d+)\s+years?'
    ]
    
    def extract_from_url(self, url, timeout=10):
        """Fetch job page and extract requirements"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; JobScraper/1.0)'
            }
            r = requests.get(url, headers=headers, timeout=timeout)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Get text content
            text = soup.get_text()
            
            return self.extract_from_text(text)
        except Exception as e:
            print(f"    ⚠ Error extracting from {url}: {e}")
            return self._empty_requirements()
    
    def extract_from_text(self, text: str) -> Dict:
        """
        Extract structured requirements from job description text
        Returns: {
            'skills': [...],
            'experience_years': int,
            'education': str,
            'keywords': [...]
        }
        """
        if not text:
            return self._empty_requirements()
        
        text_lower = text.lower()
        
        # Extract skills
        skills = self._extract_skills(text_lower)
        
        # Extract experience
        experience = self._extract_experience(text_lower)
        
        # Extract education
        education = self._extract_education(text_lower)
        
        # Extract general keywords
        keywords = self._extract_keywords(text)
        
        return {
            'skills': list(skills)[:10],  # Top 10 skills
            'experience_years': experience,
            'education': education,
            'keywords': keywords[:15]  # Top 15 keywords
        }
    
    def _extract_skills(self, text: str) -> Set[str]:
        """Extract technical skills from text"""
        found_skills = set()
        
        for category, skills in self.TECH_SKILLS.items():
            for skill in skills:
                # Use word boundaries to avoid false matches
                pattern = r'\b' + skill + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    found_skills.add(skill.replace('\\', ''))
        
        return found_skills
    
    def _extract_experience(self, text: str) -> int:
        """Extract years of experience required"""
        for pattern in self.EXP_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    years = int(match.group(1))
                    if 0 <= years <= 20:  # Sanity check
                        return years
                except:
                    continue
        return 0  # Default to 0 if not found
    
    def _extract_education(self, text: str) -> str:
        """Extract education level"""
        education_levels = {
            'phd': ['ph\\.?d', 'doctorate', 'doctoral'],
            'masters': ['master', 'msc', 'mba', 'm\\.s\\.'],
            'bachelors': ['bachelor', 'bsc', 'b\\.s\\.', 'b\\.a\\.', 'undergraduate']
        }
        
        for level, patterns in education_levels.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level
        
        return 'not_specified'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from requirements sections"""
        
        # Find requirements/qualifications sections
        requirements_text = self._extract_requirements_section(text)
        
        if not requirements_text:
            requirements_text = text[:1000]  # Fallback to first 1000 chars
        
        keywords = set()
        
        # Extract capitalized terms (2-20 chars)
        caps_pattern = r'\b[A-Z][a-zA-Z]{1,19}\b'
        for match in re.finditer(caps_pattern, requirements_text):
            word = match.group()
            if len(word) > 2 and word.lower() not in ['the', 'and', 'for', 'with']:
                keywords.add(word)
        
        # Extract common phrases
        phrases = [
            'remote', 'hybrid', 'full-time', 'part-time', 'contract',
            'startup', 'enterprise', 'saas', 'b2b', 'b2c'
        ]
        
        text_lower = requirements_text.lower()
        for phrase in phrases:
            if phrase in text_lower:
                keywords.add(phrase)
        
        return list(keywords)
    
    def _extract_requirements_section(self, text: str) -> str:
        """Extract just the requirements/qualifications section"""
        
        # Common section headers
        section_markers = [
            r'(?:requirements|qualifications|what we.*looking for|what you.*bring|'
            r'must have|required skills|key qualifications)[:\s]*',
        ]
        
        for marker in section_markers:
            match = re.search(marker, text, re.IGNORECASE)
            if match:
                start = match.end()
                section = text[start:start+800]
                
                # Stop at next major section if found
                next_section = re.search(
                    r'\n\s*(?:benefits|perks|about us|company|apply|how to)',
                    section,
                    re.IGNORECASE
                )
                if next_section:
                    section = section[:next_section.start()]
                
                return section
        
        return ""
    
    def _empty_requirements(self) -> Dict:
        """Return empty requirements structure"""
        return {
            'skills': [],
            'experience_years': 0,
            'education': 'not_specified',
            'keywords': []
        }
