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
import random # Added for _select_contextual_topic

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
    
    async def generate_ethical_content(self, topic: str = None, 
                                     content_type: ContentType = ContentType.SATIRICAL,
                                     language: str = "hi", mode: str = "DAY") -> Tuple[str, ContentMetadata]:
        """
        Generate ethical, fact-checked content with multi-language support
        Languages: Hindi (hi), Bhojpuri (bho), English (en)
        """
        
        # Validate language support
        supported_languages = ["hi", "bho", "en"]
        if language not in supported_languages:
            self.logger.warning(f"Unsupported language {language}, defaulting to Hindi")
            language = "hi"
        
        # Auto-select topic if not provided
        if not topic:
            topic = self._select_contextual_topic(content_type, language, mode)
        
        self.logger.info(f"Generating content: {content_type.value} in {language} about {topic}")
        
        # Generate content with optimal model
        content, model_used = await self._generate_with_optimal_model(
            topic, content_type, language, mode
        )
        
        if not content:
            self.logger.error("All content generation models failed")
            return None, None
        
        # Create metadata
        metadata = ContentMetadata(
            topic=topic,
            content_type=content_type,
            language=language,
            model_used=model_used,
            generation_time=datetime.now(),
            mode=mode
        )
        
        # Comprehensive validation pipeline
        validation_passed = True
        
        # 1. Fact-check the content
        if config_manager.fact_check.enabled:
            self.logger.info("🔍 Performing fact-check")
            fact_check_result = await fact_checker.comprehensive_fact_check(content)
            metadata.fact_check_result = fact_check_result
            
            if fact_check_result and fact_check_result.get('confidence', 0) < config_manager.fact_check.confidence_threshold:
                validation_passed = False
                self.logger.warning(f"Content failed fact-check: {fact_check_result.get('confidence', 0)}")
        
        # 2. Security scan
        self.logger.info("🛡️ Performing security scan")
        is_safe, threats = security_manager.scan_content_security(content)
        metadata.security_scan_result = {'safe': is_safe, 'threats': threats}
        
        if not is_safe:
            validation_passed = False
            self.logger.warning(f"Content failed security scan: {threats}")
        
        # 3. Quality assessment
        quality_score = await self._assess_content_quality(content, language, content_type)
        metadata.quality_score = quality_score
        
        if quality_score < 0.6:  # Minimum quality threshold
            validation_passed = False
            self.logger.warning(f"Content quality too low: {quality_score}")
        
        # 4. Length validation
        if len(content) > 280:
            validation_passed = False
            self.logger.warning(f"Content too long: {len(content)} characters")
        
        if not validation_passed:
            return None, metadata
        
        # Update model performance tracking
        await self._update_model_performance(model_used, True, quality_score)
        
        self.logger.info(f"✅ Content generated successfully: quality={quality_score:.2f}, model={model_used}")
        return content, metadata

    async def _generate_with_optimal_model(self, topic: str, content_type: ContentType, 
                                         language: str, mode: str) -> Tuple[Optional[str], str]:
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
                    return content, model
                
            except Exception as e:
                self.logger.warning(f"Model {model} failed: {e}")
                self._update_model_performance(model, False, 0.0, 0.0)
        
        return None, "none"
    
    async def _generate_with_model(self, model_name: str, topic: str, 
                                 content_type: ContentType, language: str, mode: str) -> Optional[str]:
        """Generate content with specific model and language support"""
        
        try:
            if model_name == "grok":
                return await self._generate_with_grok(topic, content_type, language, mode)
            elif model_name == "claude":
                return await self._generate_with_claude(topic, content_type, language, mode)
            elif model_name == "openai":
                return await self._generate_with_openai(topic, content_type, language, mode)
            elif model_name == "gemini":
                return await self._generate_with_gemini(topic, content_type, language, mode)
            elif model_name == "sarvam":
                return await self._generate_with_sarvam(topic, content_type, language, mode)
            else:
                self.logger.error(f"Unknown model: {model_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating with {model_name}: {str(e)}")
            return None

    def _create_enhanced_prompt(self, topic: str, content_type: ContentType, 
                              language: str, mode: str) -> str:
        """Create enhanced prompt with language-specific instructions"""
        
        # Language-specific instructions
        language_instructions = {
            "hi": {
                "instruction": "कृपया हिंदी में एक उच्च गुणवत्ता का ट्वीट लिखें।",
                "guidelines": "देवनागरी लिपि का उपयोग करें, सांस्कृतिक संवेदनशीलता बनाए रखें।",
                "character_limit": "280 अक्षरों के भीतर रखें।"
            },
            "bho": {
                "instruction": "कृपया भोजपुरी में एक प्रामाणिक ट्वीट लिखें।",
                "guidelines": "भोजपुरी की मूल भावना और स्थानीय संदर्भ को बनाए रखें।",
                "character_limit": "280 अक्षरों के भीतर रखें।"
            },
            "en": {
                "instruction": "Please write a high-quality tweet in English.",
                "guidelines": "Use proper grammar, maintain cultural sensitivity.",
                "character_limit": "Keep within 280 characters."
            }
        }
        
        lang_config = language_instructions.get(language, language_instructions["en"])
        
        # Content type specific guidance
        content_guidance = {
            ContentType.SATIRICAL: "व्यंग्यात्मक लेकिन सम्मानजनक" if language in ["hi", "bho"] else "satirical but respectful",
            ContentType.INFORMATIVE: "शिक्षाप्रद और तथ्यपरक" if language in ["hi", "bho"] else "educational and factual",
            ContentType.REFLECTIVE: "चिंतनशील और गहरा" if language in ["hi", "bho"] else "thoughtful and profound",
            ContentType.CULTURAL: "सांस्कृतिक और पारंपरिक" if language in ["hi", "bho"] else "cultural and traditional",
            ContentType.HISTORICAL: "ऐतिहासिक और प्रेरणादायक" if language in ["hi", "bho"] else "historical and inspiring"
        }
        
        prompt = f"""
{lang_config['instruction']}

विषय/Topic: {topic}
शैली/Style: {content_guidance[content_type]}
समय/Mode: {mode}

दिशा-निर्देश/Guidelines:
- {lang_config['guidelines']}
- {lang_config['character_limit']}
- तथ्यपरक और सत्यापित जानकारी का उपयोग करें / Use factual and verified information
- सांस्कृतिक संवेदनशीलता बनाए रखें / Maintain cultural sensitivity
- कोई भेदभावपूर्ण या आपत्तिजनक सामग्री न हो / No discriminatory or offensive content

कृपया केवल ट्वीट का टेक्स्ट दें, कोई अतिरिक्त स्पष्टीकरण नहीं।
Please provide only the tweet text, no additional explanation.
"""
        
        return prompt
    
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

    def _select_contextual_topic(self, content_type: ContentType, language: str, mode: str) -> str:
        """Select contextually appropriate topic based on language and content type"""
        
        # Language-specific topics
        if language == "hi":  # Hindi
            topics_by_type = {
                ContentType.SATIRICAL: ["सामाजिक मुद्दे", "राजनीतिक व्यंग्य", "दैनिक जीवन की समस्याएं"],
                ContentType.INFORMATIVE: ["शिक्षा", "स्वास्थ्य", "तकनीक", "विज्ञान"],
                ContentType.REFLECTIVE: ["जीवन दर्शन", "आत्म-चिंतन", "सामाजिक मूल्य"],
                ContentType.CULTURAL: ["भारतीय संस्कृति", "त्योहार", "परंपराएं", "कला"],
                ContentType.HISTORICAL: ["स्वतंत्रता संग्राम", "महान व्यक्तित्व", "ऐतिहासिक घटनाएं"]
            }
        elif language == "bho":  # Bhojpuri
            topics_by_type = {
                ContentType.SATIRICAL: ["गांव के मुद्दे", "स्थानीय राजनीति", "सामाजिक रीति-रिवाज"],
                ContentType.INFORMATIVE: ["कृषि", "शिक्षा", "स्वास्थ्य", "रोजगार"],
                ContentType.REFLECTIVE: ["जीवन के अनुभव", "पारंपरिक ज्ञान", "पारिवारिक मूल्य"],
                ContentType.CULTURAL: ["भोजपुरी संस्कृति", "लोक गीत", "त्योहार", "पारंपरिक कलाएं"],
                ContentType.HISTORICAL: ["क्षेत्रीय इतिहास", "स्थानीय नायक", "सांस्कृतिक विरासत"]
            }
        else:  # English
            topics_by_type = {
                ContentType.SATIRICAL: ["social issues", "modern life", "technology humor"],
                ContentType.INFORMATIVE: ["education", "technology", "health", "science"],
                ContentType.REFLECTIVE: ["life philosophy", "personal growth", "wisdom"],
                ContentType.CULTURAL: ["diversity", "unity", "traditions", "heritage"],
                ContentType.HISTORICAL: ["freedom struggle", "great personalities", "historical events"]
            }
        
        # Select random topic from appropriate category
        topics = topics_by_type.get(content_type, topics_by_type[ContentType.REFLECTIVE])
        return random.choice(topics)
    
    async def _assess_content_quality(self, content: str, language: str, 
                                    content_type: ContentType) -> float:
        """Assess content quality with language-specific metrics"""
        
        quality_score = 0.0
        
        # Basic length check (0.2 weight)
        if 50 <= len(content) <= 280:
            quality_score += 0.2
        elif len(content) < 50:
            quality_score += 0.1  # Too short
        # Over 280 gets 0 points
        
        # Language-specific quality checks
        if language == "hi":
            # Check for proper Devanagari script
            devanagari_chars = sum(1 for char in content if '\u0900' <= char <= '\u097F')
            if devanagari_chars / len(content) > 0.3:  # At least 30% Devanagari
                quality_score += 0.2
        
        elif language == "bho":
            # Check for Bhojpuri characteristics (mix of Devanagari and regional expressions)
            devanagari_chars = sum(1 for char in content if '\u0900' <= char <= '\u097F')
            if devanagari_chars / len(content) > 0.2:  # At least 20% Devanagari
                quality_score += 0.2
            
            # Check for common Bhojpuri words/patterns
            bhojpuri_indicators = ["के", "बा", "हs", "रहल", "करत", "भइल", "होखे"]
            if any(indicator in content for indicator in bhojpuri_indicators):
                quality_score += 0.1
        
        elif language == "en":
            # Check for proper English structure
            words = content.split()
            if len(words) >= 5:  # Minimum word count
                quality_score += 0.2
            
            # Check for capitalization and punctuation
            if content[0].isupper() and any(char in content for char in '.!?'):
                quality_score += 0.1
        
        # Content relevance and coherence (0.3 weight)
        # This would ideally use NLP models, but for now we use basic heuristics
        words = content.split()
        if len(words) >= 3:  # Minimum coherence
            quality_score += 0.2
        
        # No repetitive patterns (0.1 weight)
        word_variety = len(set(words)) / len(words) if words else 0
        if word_variety > 0.7:  # Good word variety
            quality_score += 0.1
        
        # Engagement potential (0.2 weight)
        engagement_indicators = {
            "hi": ["कैसे", "क्यों", "क्या", "जानिए", "समझिए"],
            "bho": ["कइसे", "काहे", "का", "जानीं", "समझीं"],
            "en": ["how", "why", "what", "discover", "learn", "amazing", "incredible"]
        }
        
        indicators = engagement_indicators.get(language, engagement_indicators["en"])
        if any(indicator.lower() in content.lower() for indicator in indicators):
            quality_score += 0.1
        
        return min(quality_score, 1.0)  # Cap at 1.0
    
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