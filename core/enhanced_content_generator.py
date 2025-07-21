"""
Enhanced Content Generation System
Multi-model AI with ethical checks, context awareness, and quality assurance
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re
import openai
import anthropic
import google.generativeai as genai

from config.main_config import config_manager
from core.fact_checker import fact_checker, FactCheckStatus
from core.security_manager import security_manager
from banned_words import is_banned

class ContentQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    REJECTED = "rejected"

class ContentType(Enum):
    SATIRICAL = "satirical"
    INFORMATIVE = "informative"
    REFLECTIVE = "reflective"
    CULTURAL = "cultural"
    HISTORICAL = "historical"

@dataclass
class ContentMetadata:
    model_used: str
    quality_score: float
    fact_check_result: Optional[Dict[str, Any]]
    security_scan_result: Dict[str, Any]
    generation_time: float
    content_type: ContentType
    language: str
    character_count: int
    timestamp: datetime
    content_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['content_type'] = self.content_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result

class EnhancedContentGenerator:
    """
    World-class content generation system with:
    1. Multi-model AI integration (Grok, Claude, GPT, Gemini, Sarvam)
    2. Real-time fact-checking
    3. Ethical content validation
    4. Context-aware generation
    5. Quality scoring and optimization
    6. Cost-efficient model selection
    7. Zero-downtime fallback system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Content generation cache
        self.generation_cache = {}
        self.cache_expiry = timedelta(hours=1)
        
        # Quality metrics tracking
        self.model_performance = {
            model: {'success_rate': 0.9, 'avg_quality': 0.8, 'avg_time': 2.0}
            for model in self.config.ai_models.fallback_models
        }
        
        # Context awareness
        self.historical_context = self._load_historical_context()
        self.current_events_cache = {}
    
    def _init_ai_clients(self):
        """Initialize all AI model clients"""
        try:
            # OpenAI (GPT)
            openai_key = self.config.get_api_key('openai')
            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
            
            # Anthropic (Claude)
            claude_key = self.config.get_api_key('claude')
            if claude_key:
                self.claude_client = anthropic.Anthropic(api_key=claude_key)
            
            # Google (Gemini)
            gemini_key = self.config.get_api_key('gemini')
            if gemini_key:
                genai.configure(api_key=gemini_key)
                self.gemini_client = genai
            
            self.logger.info("AI clients initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI clients: {e}")
    
    def _load_historical_context(self) -> Dict[str, Any]:
        """Load historical context for Nehru persona"""
        return {
            "birth_year": 1889,
            "death_year": 1964,
            "key_periods": {
                "independence_movement": "1920-1947",
                "prime_minister": "1947-1964",
                "congress_leadership": "1929-1964"
            },
            "key_themes": [
                "secularism", "socialism", "non_alignment", 
                "scientific_temper", "unity_in_diversity",
                "democratic_values", "education", "industrialization"
            ],
            "speaking_style": {
                "characteristics": ["eloquent", "philosophical", "idealistic", "emotional"],
                "common_phrases": ["my dear countrymen", "children of India", "tryst with destiny"],
                "tone": "paternal, visionary, passionate"
            }
        }
    
    async def generate_ethical_content(self, topic: str = None, content_type: ContentType = ContentType.SATIRICAL,
                                     language: str = "hi", mode: str = "DAY") -> Tuple[Optional[str], ContentMetadata]:
        """
        Generate ethical, fact-checked content with full validation pipeline
        """
        start_time = datetime.now()
        content_id = self._generate_content_id(topic, content_type, language)
        
        self.logger.info(f"Starting ethical content generation: {content_id}")
        
        try:
            # Step 1: Check cache
            cached_content = self._get_cached_content(content_id)
            if cached_content:
                return cached_content
            
            # Step 2: Generate content with optimal model selection
            content, model_used, generation_time = await self._generate_with_optimal_model(
                topic, content_type, language, mode
            )
            
            if not content:
                return None, self._create_failed_metadata(content_id, "generation_failed")
            
            # Step 3: Security scan
            security_scan = security_manager.scan_content_security(content)
            if not security_scan[0]:  # Not safe
                self.logger.warning(f"Content failed security scan: {security_scan[1]}")
                return None, self._create_failed_metadata(content_id, "security_failed")
            
            # Step 4: Banned words check
            if is_banned(content):
                self.logger.warning("Content contains banned words")
                return None, self._create_failed_metadata(content_id, "banned_words")
            
            # Step 5: Fact-checking (if enabled)
            fact_check_result = None
            if self.config.fact_check.enabled:
                context = {
                    "historical_period": "modern_india",
                    "persona": "nehru",
                    "content_type": content_type.value
                }
                fact_check_result = await fact_checker.comprehensive_fact_check(content, context)
                
                # Reject content with low fact-check confidence
                if fact_check_result.confidence < self.config.fact_check.confidence_threshold:
                    self.logger.warning(f"Content failed fact-check: {fact_check_result.status}")
                    return None, self._create_failed_metadata(content_id, "fact_check_failed")
            
            # Step 6: Quality assessment
            quality_score = await self._assess_content_quality(content, content_type, language)
            
            # Step 7: Create metadata
            metadata = ContentMetadata(
                model_used=model_used,
                quality_score=quality_score,
                fact_check_result=fact_check_result.to_dict() if fact_check_result else None,
                security_scan_result={"is_safe": security_scan[0], "threats": security_scan[1]},
                generation_time=generation_time,
                content_type=content_type,
                language=language,
                character_count=len(content),
                timestamp=datetime.now(),
                content_id=content_id
            )
            
            # Step 8: Cache successful result
            self._cache_content(content_id, (content, metadata))
            
            # Step 9: Update model performance metrics
            self._update_model_performance(model_used, True, quality_score, generation_time)
            
            total_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Content generated successfully: {content_id} in {total_time:.2f}s")
            
            return content, metadata
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}", exc_info=True)
            return None, self._create_failed_metadata(content_id, f"exception: {str(e)}")
    
    async def _generate_with_optimal_model(self, topic: str, content_type: ContentType, 
                                         language: str, mode: str) -> Tuple[Optional[str], str, float]:
        """Generate content using the optimal model based on performance and cost"""
        
        # Select optimal model
        optimal_model = self._select_optimal_model(content_type, language)
        
        # Try models in order of preference
        for model in [optimal_model] + [m for m in self.config.ai_models.fallback_models if m != optimal_model]:
            try:
                start_time = datetime.now()
                
                content = await self._generate_with_model(model, topic, content_type, language, mode)
                
                generation_time = (datetime.now() - start_time).total_seconds()
                
                if content and len(content.strip()) > 10:  # Valid content
                    return content, model, generation_time
                
            except Exception as e:
                self.logger.warning(f"Model {model} failed: {e}")
                self._update_model_performance(model, False, 0.0, 0.0)
        
        return None, "none", 0.0
    
    async def _generate_with_model(self, model: str, topic: str, content_type: ContentType,
                                 language: str, mode: str) -> Optional[str]:
        """Generate content with specific model"""
        
        # Create context-aware prompt
        prompt = self._create_enhanced_prompt(topic, content_type, language, mode)
        
        if model == "grok":
            return await self._generate_with_grok(prompt)
        elif model == "claude":
            return await self._generate_with_claude(prompt)
        elif model == "chatgpt":
            return await self._generate_with_openai(prompt)
        elif model == "gemini":
            return await self._generate_with_gemini(prompt)
        elif model == "sarvam":
            return await self._generate_with_sarvam(prompt)
        else:
            raise ValueError(f"Unknown model: {model}")
    
    def _create_enhanced_prompt(self, topic: str, content_type: ContentType, language: str, mode: str) -> str:
        """Create context-aware, ethical prompt for content generation"""
        
        # Base persona context
        persona_context = f"""
        You are Jawaharlal Nehru (1889-1964), India's first Prime Minister, writing in the modern era.
        Your voice should reflect: {', '.join(self.historical_context['speaking_style']['characteristics'])}
        
        Key themes to potentially incorporate: {', '.join(self.historical_context['key_themes'][:3])}
        """
        
        # Content type specific instructions
        type_instructions = {
            ContentType.SATIRICAL: "Write with gentle humor and wit, making thoughtful observations about modern life",
            ContentType.INFORMATIVE: "Share knowledge or insights in an educational but accessible manner",
            ContentType.REFLECTIVE: "Reflect philosophically on life, society, or human nature",
            ContentType.CULTURAL: "Celebrate Indian culture, diversity, or traditions",
            ContentType.HISTORICAL: "Draw parallels between historical events and contemporary situations"
        }
        
        # Language specific instructions
        if language == "hi":
            language_instruction = """
            Write in Hindi with:
            - Natural, conversational tone
            - Appropriate cultural context
            - Emotional warmth typical of Nehru's style
            - Simple yet elegant language
            """
        else:
            language_instruction = """
            Write in English with:
            - Nehru's characteristic eloquence
            - Philosophical depth
            - Emotional resonance
            - Accessible language for modern readers
            """
        
        # Mode-specific tone
        mode_instruction = "Write with a reflective, evening tone" if mode == "NIGHT" else "Write with an energetic, optimistic tone"
        
        # Ethical guidelines
        ethical_guidelines = """
        ETHICAL REQUIREMENTS (MANDATORY):
        - Promote unity, peace, and understanding
        - Avoid divisive, hateful, or discriminatory content
        - Respect all religions, communities, and individuals
        - Focus on positive values and constructive ideas
        - Fact-check any specific claims or statistics
        - Maintain dignity and respect in all communications
        """
        
        # Final prompt construction
        if topic:
            topic_instruction = f"Topic focus: {topic}"
        else:
            topic_instruction = "Choose an appropriate topic that resonates with current times while staying true to Nehru's values"
        
        full_prompt = f"""
        {persona_context}
        
        {language_instruction}
        
        Content Type: {type_instructions.get(content_type, '')}
        
        {mode_instruction}
        
        {topic_instruction}
        
        {ethical_guidelines}
        
        Requirements:
        - Maximum 280 characters for Twitter
        - Natural, human-like expression
        - No hashtags or excessive emojis
        - Authentic to Nehru's voice and values
        - Appropriate for public social media
        
        Generate the tweet now:
        """
        
        return full_prompt
    
    async def _generate_with_grok(self, prompt: str) -> Optional[str]:
        """Generate content using Grok (xAI)"""
        try:
            import requests
            
            api_key = self.config.get_api_key('grok')
            if not api_key:
                return None
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'grok-4-0709',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 100,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            self.logger.error(f"Grok generation failed: {e}")
        
        return None
    
    async def _generate_with_claude(self, prompt: str) -> Optional[str]:
        """Generate content using Claude (Anthropic)"""
        try:
            if not hasattr(self, 'claude_client'):
                return None
            
            response = await self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            self.logger.error(f"Claude generation failed: {e}")
        
        return None
    
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Generate content using OpenAI GPT"""
        try:
            if not hasattr(self, 'openai_client'):
                return None
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
        
        return None
    
    async def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Generate content using Google Gemini"""
        try:
            if not hasattr(self, 'gemini_client'):
                return None
            
            model = self.gemini_client.GenerativeModel('gemini-pro')
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=100,
                    temperature=0.7
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
        
        return None
    
    async def _generate_with_sarvam(self, prompt: str) -> Optional[str]:
        """Generate content using Sarvam AI"""
        try:
            import requests
            
            api_key = self.config.get_api_key('sarvam')
            if not api_key:
                return None
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'prompt': prompt,
                'max_tokens': 100,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.sarvam.ai/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('text', '').strip()
            
        except Exception as e:
            self.logger.error(f"Sarvam generation failed: {e}")
        
        return None
    
    def _select_optimal_model(self, content_type: ContentType, language: str) -> str:
        """Select optimal model based on performance, cost, and requirements"""
        
        # Language-specific preferences
        if language == "hi":
            # Prefer models with better Hindi support
            preferred_models = ["sarvam", "gemini", "grok", "claude", "chatgpt"]
        else:
            # For English, prioritize quality
            preferred_models = ["claude", "grok", "chatgpt", "gemini", "sarvam"]
        
        # Content type specific adjustments
        if content_type in [ContentType.SATIRICAL, ContentType.REFLECTIVE]:
            # For creative content, prefer Claude and GPT
            preferred_models = ["claude", "chatgpt"] + [m for m in preferred_models if m not in ["claude", "chatgpt"]]
        
        # Select based on performance and cost
        best_model = self.config.get_cost_optimized_model(quality_threshold=0.8)
        
        # If best model is in preferred list, use it; otherwise use first preferred
        if best_model in preferred_models:
            return best_model
        else:
            return preferred_models[0]
    
    async def _assess_content_quality(self, content: str, content_type: ContentType, language: str) -> float:
        """Assess content quality using multiple metrics"""
        quality_factors = {}
        
        # Length appropriateness (Twitter limit)
        if len(content) <= 280:
            quality_factors['length'] = 1.0
        elif len(content) <= 300:
            quality_factors['length'] = 0.8
        else:
            quality_factors['length'] = 0.5
        
        # Language appropriateness
        if language == "hi":
            # Check for proper Hindi script and structure
            hindi_chars = len(re.findall(r'[\u0900-\u097F]', content))
            total_chars = len(content.replace(' ', ''))
            if total_chars > 0:
                quality_factors['language'] = min(1.0, hindi_chars / total_chars * 1.5)
            else:
                quality_factors['language'] = 0.0
        else:
            # Check for proper English structure
            english_words = len(re.findall(r'\b[A-Za-z]+\b', content))
            quality_factors['language'] = min(1.0, english_words / 10)  # Normalize
        
        # Coherence and readability
        sentences = len(re.split(r'[.!?]+', content))
        if sentences >= 1:
            quality_factors['coherence'] = min(1.0, sentences / 3)  # Optimal 1-3 sentences
        else:
            quality_factors['coherence'] = 0.3
        
        # Persona authenticity (basic keyword matching)
        nehru_keywords = ['india', 'children', 'nation', 'future', 'democracy', 'unity', 'peace']
        keyword_matches = sum(1 for keyword in nehru_keywords if keyword.lower() in content.lower())
        quality_factors['authenticity'] = min(1.0, keyword_matches / 3)
        
        # Calculate weighted score
        weights = {
            'length': 0.3,
            'language': 0.25,
            'coherence': 0.25,
            'authenticity': 0.2
        }
        
        total_score = sum(quality_factors[factor] * weight for factor, weight in weights.items())
        return min(1.0, max(0.0, total_score))
    
    def _update_model_performance(self, model: str, success: bool, quality: float, time: float):
        """Update model performance metrics"""
        if model not in self.model_performance:
            self.model_performance[model] = {'success_rate': 0.5, 'avg_quality': 0.5, 'avg_time': 5.0}
        
        perf = self.model_performance[model]
        
        # Exponential moving average
        alpha = 0.1  # Learning rate
        
        if success:
            perf['success_rate'] = (1 - alpha) * perf['success_rate'] + alpha * 1.0
            perf['avg_quality'] = (1 - alpha) * perf['avg_quality'] + alpha * quality
            if time > 0:
                perf['avg_time'] = (1 - alpha) * perf['avg_time'] + alpha * time
        else:
            perf['success_rate'] = (1 - alpha) * perf['success_rate'] + alpha * 0.0
    
    def _generate_content_id(self, topic: str, content_type: ContentType, language: str) -> str:
        """Generate unique content ID"""
        content_str = f"{topic}_{content_type.value}_{language}_{datetime.now().strftime('%Y%m%d_%H')}"
        content_hash = hashlib.md5(content_str.encode()).hexdigest()[:12]
        return f"content_{content_hash}"
    
    def _get_cached_content(self, content_id: str) -> Optional[Tuple[str, ContentMetadata]]:
        """Get cached content if still valid"""
        if content_id in self.generation_cache:
            content, metadata, timestamp = self.generation_cache[content_id]
            if datetime.now() - timestamp < self.cache_expiry:
                self.logger.info(f"Using cached content: {content_id}")
                return content, metadata
        return None
    
    def _cache_content(self, content_id: str, result: Tuple[str, ContentMetadata]):
        """Cache content result"""
        self.generation_cache[content_id] = (*result, datetime.now())
        
        # Clean old cache entries
        if len(self.generation_cache) > 100:
            oldest_entries = sorted(
                self.generation_cache.items(),
                key=lambda x: x[1][2]
            )[:20]
            for entry_id, _ in oldest_entries:
                del self.generation_cache[entry_id]
    
    def _create_failed_metadata(self, content_id: str, reason: str) -> ContentMetadata:
        """Create metadata for failed generation"""
        return ContentMetadata(
            model_used="none",
            quality_score=0.0,
            fact_check_result=None,
            security_scan_result={"is_safe": False, "threats": [reason]},
            generation_time=0.0,
            content_type=ContentType.SATIRICAL,
            language="unknown",
            character_count=0,
            timestamp=datetime.now(),
            content_id=content_id
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all models"""
        return {
            "model_performance": self.model_performance,
            "cache_stats": {
                "cached_items": len(self.generation_cache),
                "cache_hit_rate": "N/A"  # Implement cache hit tracking
            },
            "generation_stats": {
                "total_generations": "N/A",  # Implement generation counting
                "success_rate": "N/A",
                "avg_quality": "N/A"
            }
        }

# Global content generator instance
enhanced_content_generator = EnhancedContentGenerator()