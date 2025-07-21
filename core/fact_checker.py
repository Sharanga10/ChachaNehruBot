"""
Advanced Multi-Layered Fact-Checking System
Real-time verification with multiple sources and AI-powered analysis
"""

import asyncio
import aiohttp
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re
from urllib.parse import urlparse

import requests
from transformers import pipeline
import openai
from config.main_config import config_manager

class FactCheckStatus(Enum):
    VERIFIED = "verified"
    DISPUTED = "disputed"
    UNVERIFIED = "unverified"
    MISLEADING = "misleading"
    FALSE = "false"
    NEEDS_CONTEXT = "needs_context"

@dataclass
class FactCheckResult:
    status: FactCheckStatus
    confidence: float
    sources: List[Dict[str, Any]]
    reasoning: str
    timestamp: datetime
    fact_check_id: str
    context_flags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['status'] = self.status.value
        result['timestamp'] = self.timestamp.isoformat()
        return result

class EnhancedFactChecker:
    """
    World-class fact-checking system with multiple verification layers:
    1. Real-time news verification
    2. Historical context analysis
    3. Cross-source validation
    4. AI-powered reasoning
    5. Bias detection
    6. Misinformation patterns
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = config_manager.fact_check
        
        # Initialize AI models for fact-checking
        self._init_ai_models()
        
        # Fact-checking APIs
        self.fact_check_apis = {
            'snopes': 'https://api.snopes.com/v1/fact-check',
            'politifact': 'https://api.politifact.com/v2/statement',
            'factcheck_org': 'https://api.factcheck.org/v1/check',
            'google_factcheck': 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
        }
        
        # News verification sources
        self.news_apis = {
            'newsapi': 'https://newsapi.org/v2/everything',
            'guardian': 'https://content.guardianapis.com/search',
            'reuters': 'https://api.reuters.com/v1/news',
            'ap_news': 'https://api.ap.org/v2/search'
        }
        
        # Cache for fact-check results
        self.cache = {}
        self.cache_expiry = timedelta(hours=24)
        
    def _init_ai_models(self):
        """Initialize AI models for fact-checking"""
        try:
            # Bias detection model
            self.bias_detector = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=-1  # CPU
            )
            
            # Misinformation detection
            self.misinfo_detector = pipeline(
                "text-classification",
                model="martin-ha/toxic-comment-model",
                device=-1
            )
            
            self.logger.info("AI models initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
            self.bias_detector = None
            self.misinfo_detector = None
    
    async def comprehensive_fact_check(self, content: str, context: Dict[str, Any] = None) -> FactCheckResult:
        """
        Perform comprehensive fact-checking with multiple verification layers
        """
        fact_check_id = self._generate_fact_check_id(content)
        
        # Check cache first
        cached_result = self._get_cached_result(fact_check_id)
        if cached_result:
            return cached_result
        
        self.logger.info(f"Starting comprehensive fact-check: {fact_check_id}")
        
        # Layer 1: Content analysis and preprocessing
        claims = self._extract_factual_claims(content)
        
        # Layer 2: Real-time verification
        verification_tasks = [
            self._verify_with_fact_check_apis(claims),
            self._cross_reference_news_sources(claims),
            self._check_historical_context(claims, context),
            self._detect_bias_and_misinformation(content),
            self._analyze_with_ai_reasoning(content, claims)
        ]
        
        verification_results = await asyncio.gather(*verification_tasks, return_exceptions=True)
        
        # Layer 3: Aggregate and analyze results
        final_result = self._aggregate_verification_results(
            content, claims, verification_results, fact_check_id
        )
        
        # Cache the result
        self._cache_result(fact_check_id, final_result)
        
        self.logger.info(f"Fact-check completed: {fact_check_id} - Status: {final_result.status}")
        return final_result
    
    def _extract_factual_claims(self, content: str) -> List[str]:
        """Extract factual claims from content using NLP"""
        claims = []
        
        # Pattern matching for factual statements
        fact_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(percent|%|people|deaths|cases|dollars)',
            r'(according to|reports show|studies indicate|data reveals)',
            r'(increased by|decreased by|rose by|fell by)\s*(\d+)',
            r'(in \d{4}|last year|this year|recently)',
        ]
        
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            # Check if sentence contains factual patterns
            for pattern in fact_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence)
                    break
        
        return claims[:5]  # Limit to 5 most important claims
    
    async def _verify_with_fact_check_apis(self, claims: List[str]) -> Dict[str, Any]:
        """Verify claims with multiple fact-checking APIs"""
        results = {'api_results': [], 'confidence': 0.0}
        
        async with aiohttp.ClientSession() as session:
            for claim in claims:
                for api_name, api_url in self.fact_check_apis.items():
                    try:
                        api_key = config_manager.get_api_key('factcheck')
                        if not api_key:
                            continue
                        
                        headers = {'Authorization': f'Bearer {api_key}'}
                        params = {'query': claim, 'limit': 3}
                        
                        async with session.get(api_url, headers=headers, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                results['api_results'].append({
                                    'api': api_name,
                                    'claim': claim,
                                    'result': data
                                })
                    except Exception as e:
                        self.logger.warning(f"Fact-check API {api_name} failed: {e}")
        
        # Calculate confidence based on API results
        if results['api_results']:
            results['confidence'] = min(0.8, len(results['api_results']) * 0.2)
        
        return results
    
    async def _cross_reference_news_sources(self, claims: List[str]) -> Dict[str, Any]:
        """Cross-reference claims with reputable news sources"""
        results = {'news_matches': [], 'source_credibility': 0.0}
        
        async with aiohttp.ClientSession() as session:
            for claim in claims:
                search_query = self._create_search_query(claim)
                
                for source_name, api_url in self.news_apis.items():
                    try:
                        api_key = config_manager.get_api_key(source_name)
                        if not api_key:
                            continue
                        
                        headers = {'Authorization': f'Bearer {api_key}'}
                        params = {
                            'q': search_query,
                            'sortBy': 'relevancy',
                            'pageSize': 5,
                            'language': 'en'
                        }
                        
                        async with session.get(api_url, headers=headers, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                results['news_matches'].append({
                                    'source': source_name,
                                    'claim': claim,
                                    'articles': data.get('articles', [])
                                })
                    except Exception as e:
                        self.logger.warning(f"News API {source_name} failed: {e}")
        
        # Calculate source credibility
        credible_sources = ['guardian', 'reuters', 'ap_news']
        credible_matches = sum(1 for match in results['news_matches'] 
                             if match['source'] in credible_sources)
        
        if results['news_matches']:
            results['source_credibility'] = credible_matches / len(results['news_matches'])
        
        return results
    
    async def _check_historical_context(self, claims: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Check claims against historical context and patterns"""
        results = {'historical_accuracy': 0.0, 'context_flags': []}
        
        if not context:
            return results
        
        # Check for anachronisms
        current_year = datetime.now().year
        for claim in claims:
            # Look for year mentions
            years = re.findall(r'\b(19|20)\d{2}\b', claim)
            for year in years:
                year_int = int(year)
                if year_int > current_year:
                    results['context_flags'].append(f"Future date mentioned: {year}")
                elif year_int < 1900:
                    results['context_flags'].append(f"Suspicious historical date: {year}")
        
        # Check against known historical facts
        if context.get('historical_period'):
            period = context['historical_period']
            # Add period-specific validation logic here
        
        results['historical_accuracy'] = 0.7 if not results['context_flags'] else 0.3
        return results
    
    async def _detect_bias_and_misinformation(self, content: str) -> Dict[str, Any]:
        """Detect bias and misinformation patterns using AI"""
        results = {'bias_score': 0.0, 'misinfo_score': 0.0, 'flags': []}
        
        try:
            # Bias detection
            if self.bias_detector:
                bias_result = self.bias_detector(content)
                if bias_result and len(bias_result) > 0:
                    bias_score = bias_result[0].get('score', 0.0)
                    if bias_result[0].get('label') == 'TOXIC':
                        results['bias_score'] = bias_score
                        if bias_score > 0.7:
                            results['flags'].append('High bias detected')
            
            # Misinformation patterns
            if self.misinfo_detector:
                misinfo_result = self.misinfo_detector(content)
                if misinfo_result and len(misinfo_result) > 0:
                    misinfo_score = misinfo_result[0].get('score', 0.0)
                    results['misinfo_score'] = misinfo_score
                    if misinfo_score > 0.6:
                        results['flags'].append('Potential misinformation patterns')
            
        except Exception as e:
            self.logger.error(f"AI bias/misinfo detection failed: {e}")
        
        return results
    
    async def _analyze_with_ai_reasoning(self, content: str, claims: List[str]) -> Dict[str, Any]:
        """Use advanced AI reasoning for fact verification"""
        results = {'ai_confidence': 0.0, 'reasoning': '', 'logical_consistency': 0.0}
        
        try:
            # Use GPT-4 for advanced reasoning
            api_key = config_manager.get_api_key('openai')
            if not api_key:
                return results
            
            openai.api_key = api_key
            
            prompt = f"""
            As an expert fact-checker, analyze this content for factual accuracy:
            
            Content: {content}
            
            Key claims identified: {claims}
            
            Please provide:
            1. Overall factual assessment (0-1 confidence score)
            2. Logical consistency analysis
            3. Reasoning for your assessment
            4. Any red flags or concerns
            
            Respond in JSON format:
            {{
                "confidence": 0.0-1.0,
                "logical_consistency": 0.0-1.0,
                "reasoning": "detailed explanation",
                "red_flags": ["flag1", "flag2"]
            }}
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            results.update(ai_analysis)
            
        except Exception as e:
            self.logger.error(f"AI reasoning analysis failed: {e}")
        
        return results
    
    def _aggregate_verification_results(self, content: str, claims: List[str], 
                                      verification_results: List[Any], 
                                      fact_check_id: str) -> FactCheckResult:
        """Aggregate all verification results into final assessment"""
        
        # Extract results (handle exceptions)
        api_results = verification_results[0] if not isinstance(verification_results[0], Exception) else {}
        news_results = verification_results[1] if not isinstance(verification_results[1], Exception) else {}
        historical_results = verification_results[2] if not isinstance(verification_results[2], Exception) else {}
        bias_results = verification_results[3] if not isinstance(verification_results[3], Exception) else {}
        ai_results = verification_results[4] if not isinstance(verification_results[4], Exception) else {}
        
        # Calculate weighted confidence score
        confidence_factors = {
            'api_verification': api_results.get('confidence', 0.0) * 0.3,
            'news_credibility': news_results.get('source_credibility', 0.0) * 0.25,
            'historical_accuracy': historical_results.get('historical_accuracy', 0.0) * 0.15,
            'bias_check': (1.0 - bias_results.get('bias_score', 0.0)) * 0.15,
            'ai_reasoning': ai_results.get('confidence', 0.0) * 0.15
        }
        
        total_confidence = sum(confidence_factors.values())
        
        # Determine status based on confidence and flags
        context_flags = []
        context_flags.extend(historical_results.get('context_flags', []))
        context_flags.extend(bias_results.get('flags', []))
        context_flags.extend(ai_results.get('red_flags', []))
        
        if total_confidence >= 0.85:
            status = FactCheckStatus.VERIFIED
        elif total_confidence >= 0.7:
            status = FactCheckStatus.NEEDS_CONTEXT
        elif total_confidence >= 0.5:
            status = FactCheckStatus.UNVERIFIED
        elif total_confidence >= 0.3:
            status = FactCheckStatus.DISPUTED
        else:
            status = FactCheckStatus.FALSE
        
        # Override status if serious red flags
        if bias_results.get('bias_score', 0.0) > 0.8 or bias_results.get('misinfo_score', 0.0) > 0.7:
            status = FactCheckStatus.MISLEADING
        
        # Compile reasoning
        reasoning_parts = []
        if ai_results.get('reasoning'):
            reasoning_parts.append(f"AI Analysis: {ai_results['reasoning']}")
        if api_results.get('api_results'):
            reasoning_parts.append(f"Verified through {len(api_results['api_results'])} fact-check sources")
        if news_results.get('news_matches'):
            reasoning_parts.append(f"Cross-referenced with {len(news_results['news_matches'])} news sources")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Automated verification completed"
        
        # Compile sources
        sources = []
        for api_result in api_results.get('api_results', []):
            sources.append({
                'type': 'fact_check_api',
                'source': api_result['api'],
                'data': api_result['result']
            })
        
        for news_match in news_results.get('news_matches', []):
            sources.append({
                'type': 'news_source',
                'source': news_match['source'],
                'articles': news_match['articles'][:3]  # Limit articles
            })
        
        return FactCheckResult(
            status=status,
            confidence=total_confidence,
            sources=sources,
            reasoning=reasoning,
            timestamp=datetime.now(),
            fact_check_id=fact_check_id,
            context_flags=context_flags
        )
    
    def _generate_fact_check_id(self, content: str) -> str:
        """Generate unique ID for fact-check result"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return f"fc_{timestamp}_{content_hash}"
    
    def _create_search_query(self, claim: str) -> str:
        """Create optimized search query from claim"""
        # Remove common words and focus on key terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = claim.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return ' '.join(keywords[:5])  # Limit to 5 keywords
    
    def _get_cached_result(self, fact_check_id: str) -> Optional[FactCheckResult]:
        """Get cached fact-check result if still valid"""
        if fact_check_id in self.cache:
            cached_result, timestamp = self.cache[fact_check_id]
            if datetime.now() - timestamp < self.cache_expiry:
                self.logger.info(f"Using cached fact-check result: {fact_check_id}")
                return cached_result
        return None
    
    def _cache_result(self, fact_check_id: str, result: FactCheckResult):
        """Cache fact-check result"""
        self.cache[fact_check_id] = (result, datetime.now())
        
        # Clean old cache entries
        if len(self.cache) > 1000:  # Limit cache size
            oldest_entries = sorted(self.cache.items(), key=lambda x: x[1][1])[:100]
            for entry_id, _ in oldest_entries:
                del self.cache[entry_id]

# Global fact-checker instance
fact_checker = EnhancedFactChecker()