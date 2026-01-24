# requirements_extractor.py
import re
import requests
from bs4 import BeautifulSoup

class RequirementsExtractor:
    """Extract requirements from job posting URLs"""
    
   TECH_SKILLS = {
    # Product Strategy & Roadmap
    'product strategy', 'product roadmap', 'product vision', 'product discovery',
    'product lifecycle', 'product-market fit', 'prioritization', 'backlog management',
    'okrs', 'kpis', 'metrics', 'user stories', 'requirements gathering', 'prd',
    'go-to-market', 'stakeholder management', 'cross-functional collaboration',

    # Analytics & Data
    'data analysis', 'sql', 'a/b testing', 'experimentation', 'cohort analysis',
    'funnel analysis', 'dashboards', 'amplitude', 'mixpanel', 'google analytics',
    'ga4', 'looker', 'tableau', 'power bi',

    # AI / ML
    'artificial intelligence', 'machine learning', 'generative ai', 'llms',
    'prompt engineering', 'nlp', 'recommendation systems', 'data science',
    'mlops', 'openai api', 'embeddings', 'vector databases', 'rag',

    # UX / Design
    'ux design', 'ui design', 'user research', 'usability testing',
    'customer journey mapping', 'wireframing', 'prototyping',
    'figma', 'design systems', 'accessibility',

    # Customer Success & Growth
    'customer success', 'customer onboarding', 'customer retention',
    'churn reduction', 'nps', 'csat', 'user feedback', 'growth strategy',
    'pricing strategy', 'monetization',

    # Tech Foundations
    'apis', 'rest', 'graphql', 'microservices', 'cloud', 'aws',
    'docker', 'ci/cd', 'system design', 'scalability',
    'security', 'data privacy', 'gdpr',

    # Tools
    'jira', 'confluence', 'notion', 'slack', 'git', 'github',
    'linear', 'asana', 'trello', 'miro'  
}

    
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
        except:
            return self._empty_requirements()
    
    def extract_from_text(self, text):
        """Extract structured requirements from text"""
        text_lower = text.lower()
        
        # Extract skills
        skills = [skill for skill in self.TECH_SKILLS 
                  if re.search(r'\b' + skill.replace('.', r'\.') + r'\b', text_lower)]
        
        # Extract years of experience
        exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?).*?(?:experience|exp)', text_lower)
        experience_years = int(exp_match.group(1)) if exp_match else 0
        
        # Extract education
        education = 'bachelors' if 'bachelor' in text_lower else 'not_specified'
        if 'master' in text_lower or 'mba' in text_lower:
            education = 'masters'
        if 'phd' in text_lower or 'doctorate' in text_lower:
            education = 'phd'
        
        return {
            'skills': skills[:10],  # Top 10 skills
            'experience_years': experience_years,
            'education': education
        }
    
    def _empty_requirements(self):
        return {
            'skills': [],
            'experience_years': 0,
            'education': 'not_specified'
        }
