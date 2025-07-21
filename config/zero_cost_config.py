"""
Zero-Cost Experimental Configuration with Bhojpuri Support
Uses only free services and existing APIs with strict cost controls
Perfect for personal experimentation and learning
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

@dataclass
class ZeroCostConfig:
    """Zero-cost configuration for personal experimentation"""
    
    # Budget constraints (from your grok_tracker.py)
    max_monthly_budget_inr: float = 250.0  # ₹250 (~$3)
    max_monthly_budget_usd: float = 3.0
    
    # Free tier limits
    chatgpt_free_requests_per_month: int = 100  # Conservative estimate
    grok_monthly_budget_inr: float = 250.0  # Your existing budget
    
    # Enabled services (FREE ONLY + ESSENTIAL BHOJPURI)
    enabled_services: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.enabled_services is None:
            self.enabled_services = {
                # AI Models (Use your existing APIs with cost controls)
                "chatgpt": True,    # Your existing API with cost control
                "grok": True,       # Your existing API with ₹250 budget
                "sarvam": False,    # Disable paid model
                "claude": False,    # Disable paid model
                "gemini": False,    # Disable paid model
                
                # Future AI Models (PROVISIONED)
                "dalle": False,         # Image generation - provision for future
                "midjourney": False,    # Image generation - provision for future
                "stable_diffusion": True,  # Open source image generation - FREE
                "runway": False,        # Video generation - provision for future
                "pika_labs": False,     # Video generation - provision for future
                "luma_ai": False,       # Video generation - provision for future
                "kling": False,         # Video generation - provision for future
                
                # Fact-checking (FREE ONLY)
                "google_factcheck": True,   # Free tier available
                "snopes": False,            # Paid service - disable
                "politifact": False,        # Paid service - disable
                "factcheck_org": False,     # Paid service - disable
                
                # News APIs (FREE ONLY)
                "newsapi": True,            # Free tier: 1000 requests/month
                "times_of_india": False,    # Paid service - disable
                "guardian": False,          # Paid service - disable
                "reuters": False,           # Paid service - disable
                "ap_news": False,           # Paid service - disable
                
                # Security Tools (FREE/BUILT-IN ONLY)
                "content_security_scanner": True,   # Built-in, no cost
                "malicious_url_checker": False,     # Usually paid - disable
                "sentiment_analysis": True,         # Built-in, no cost
                "hate_speech_detection": True,      # Built-in, no cost
                "bias_detection": False,            # AI-powered, costs money
                
                # Language Processing (FREE + ESSENTIAL BHOJPURI)
                "google_translate": True,   # Free tier: 500,000 chars/month
                "bhojpuri_model": True,     # ESSENTIAL - Keep enabled even in zero-cost
                "hindi_sentiment": True,    # Built-in, no cost
                "indic_nlp": True,         # Open source, no cost
                "azure_cognitive": False,   # Paid service - disable
                
                # Infrastructure (FREE/LOCAL ONLY)
                "local_storage": True,      # Use local files instead of cloud DB
                "local_cache": True,        # Use local cache instead of Redis
                "local_backup": True,       # Local backup instead of cloud
                "mongodb": False,           # Paid hosting - use local SQLite
                "redis_cache": False,       # Paid hosting - use local cache
                "backup_storage": False,    # Paid cloud storage - use local
                "cdn": False,               # Paid service - disable
                "load_balancer": False,     # Paid service - disable
                
                # Monitoring (FREE ONLY)
                "local_logging": True,      # Local log files
                "uptime_monitoring": False, # Paid service - disable
                "performance_metrics": False, # Paid service - disable
                "twitter_analytics": False,  # Paid service - disable
                "custom_dashboard": False,   # Paid service - disable
                
                # Future Multimedia Features (PROVISIONED)
                "image_generation": False,      # Ready for DALL-E, Midjourney
                "video_generation": False,      # Ready for Runway, Pika
                "audio_generation": False,      # Ready for ElevenLabs, Murf
                "3d_generation": False,         # Ready for future 3D AI
                "avatar_generation": False,     # Ready for avatar creation
                "animation_generation": False,  # Ready for AI animation
            }

@dataclass
class LocalInfrastructureConfig:
    """Configuration for local infrastructure (zero cost)"""
    
    # Local storage paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    cache_dir: str = "cache"
    backup_dir: str = "backups"
    media_dir: str = "media"  # For future image/video storage
    
    # Local database (SQLite instead of MongoDB)
    database_file: str = "data/bot_database.sqlite"
    
    # Local cache (dict/file instead of Redis)
    cache_file: str = "cache/content_cache.json"
    cache_max_size: int = 1000  # Maximum cached items
    
    # Posting frequency (balanced for cost vs engagement)
    tweets_per_day: int = 15    # Increased from 10 to accommodate Bhojpuri
    posting_interval_hours: float = 1.6  # Every 1.6 hours
    
    # Language distribution (WITH BHOJPURI - ESSENTIAL)
    language_distribution: Dict[str, float] = None
    
    def __post_init__(self):
        if self.language_distribution is None:
            # Include Bhojpuri as essential
            self.language_distribution = {
                "hi": 0.60,   # Hindi: 60% (9 tweets/day)
                "bho": 0.30,  # Bhojpuri: 30% (4-5 tweets/day) - ESSENTIAL
                "en": 0.10    # English: 10% (1-2 tweets/day)
            }

@dataclass
class MultimediaConfig:
    """Configuration for future AI image/video generation"""
    
    # Image generation settings
    image_models: Dict[str, Dict] = None
    default_image_size: str = "1024x1024"
    max_images_per_day: int = 5  # Conservative limit
    
    # Video generation settings  
    video_models: Dict[str, Dict] = None
    default_video_duration: int = 10  # seconds
    max_videos_per_day: int = 2  # Very conservative
    
    # Local storage for media
    local_media_storage: bool = True
    media_cache_size_mb: int = 500  # 500MB cache
    
    def __post_init__(self):
        if self.image_models is None:
            self.image_models = {
                "stable_diffusion": {
                    "enabled": True,
                    "cost_per_image": 0.0,  # Open source, free to run locally
                    "quality": "high",
                    "speed": "medium",
                    "local_install": True
                },
                "dalle": {
                    "enabled": False,  # Provision for future
                    "cost_per_image": 0.02,  # $0.02 per image
                    "quality": "very_high", 
                    "speed": "fast",
                    "local_install": False
                },
                "midjourney": {
                    "enabled": False,  # Provision for future
                    "cost_per_image": 0.03,  # ~$0.03 per image
                    "quality": "artistic",
                    "speed": "medium",
                    "local_install": False
                }
            }
        
        if self.video_models is None:
            self.video_models = {
                "runway": {
                    "enabled": False,  # Provision for future
                    "cost_per_second": 0.10,  # ~$0.10 per second
                    "quality": "high",
                    "max_duration": 30
                },
                "pika_labs": {
                    "enabled": False,  # Provision for future
                    "cost_per_second": 0.08,
                    "quality": "medium",
                    "max_duration": 15
                },
                "luma_ai": {
                    "enabled": False,  # Provision for future
                    "cost_per_second": 0.12,
                    "quality": "very_high",
                    "max_duration": 10
                },
                "kling": {
                    "enabled": False,  # Provision for future
                    "cost_per_second": 0.05,  # More affordable
                    "quality": "good",
                    "max_duration": 20
                }
            }

class ZeroCostBotManager:
    """Zero-cost bot configuration manager with Bhojpuri and multimedia support"""
    
    def __init__(self):
        self.zero_cost = ZeroCostConfig()
        self.local_infra = LocalInfrastructureConfig()
        self.multimedia = MultimediaConfig()
        self.setup_local_directories()
        self.setup_logging()
    
    def setup_local_directories(self):
        """Create local directories for zero-cost operation"""
        directories = [
            self.local_infra.data_dir,
            self.local_infra.logs_dir,
            self.local_infra.cache_dir,
            self.local_infra.backup_dir,
            self.local_infra.media_dir,
            f"{self.local_infra.media_dir}/images",
            f"{self.local_infra.media_dir}/videos",
            f"{self.local_infra.media_dir}/audio"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Setup local logging (free)"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{self.local_infra.logs_dir}/zero_cost_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API keys for enabled services only"""
        if not self.is_service_enabled(service):
            return None
        
        key_mapping = {
            'openai': 'OPENAI_API_KEY',      # Your existing ChatGPT API
            'grok': 'XAI_API_KEY',           # Your existing Grok API
            'google_translate': 'GOOGLE_API_KEY',  # Free tier
            'newsapi': 'NEWS_API_KEY',       # Free tier
            'dalle': 'OPENAI_API_KEY',       # Same as OpenAI
            'runway': 'RUNWAY_API_KEY',      # Future provision
            'pika': 'PIKA_API_KEY',          # Future provision
            'luma': 'LUMA_API_KEY',          # Future provision
        }
        
        env_var = key_mapping.get(service)
        if env_var:
            return os.getenv(env_var)
        return None
    
    def is_service_enabled(self, service: str) -> bool:
        """Check if service is enabled in zero-cost mode"""
        return self.zero_cost.enabled_services.get(service, False)
    
    def get_daily_tweet_quota(self) -> int:
        """Get daily tweet quota (increased for Bhojpuri support)"""
        return self.local_infra.tweets_per_day
    
    def get_language_for_tweet(self, tweet_number: int) -> str:
        """Get language for tweet (Hindi 60%, Bhojpuri 30%, English 10%)"""
        # Distribute based on tweet number
        if tweet_number % 10 < 6:
            return "hi"      # Hindi (60%)
        elif tweet_number % 10 < 9:
            return "bho"     # Bhojpuri (30%)
        else:
            return "en"      # English (10%)
    
    def get_daily_language_distribution(self) -> Dict[str, int]:
        """Get daily tweet count by language"""
        total_daily = self.local_infra.tweets_per_day
        return {
            "hi": int(total_daily * self.local_infra.language_distribution["hi"]),    # 9 tweets
            "bho": int(total_daily * self.local_infra.language_distribution["bho"]),  # 4-5 tweets  
            "en": int(total_daily * self.local_infra.language_distribution["en"])     # 1-2 tweets
        }
    
    def get_monthly_cost_estimate(self) -> Dict[str, float]:
        """Estimate monthly costs (should be near zero but include Bhojpuri)"""
        costs = {
            "ai_models": 0.0,
            "fact_checking": 0.0,
            "news_apis": 0.0,
            "security_tools": 0.0,
            "language_processing": 0.0,
            "multimedia_generation": 0.0,
            "infrastructure": 0.0,
            "monitoring": 0.0,
            "total_usd": 0.0
        }
        
        # Only count your existing API usage (with cost controls)
        # ChatGPT: Free tier or your existing credits
        # Grok: Your ₹250 budget = ~$3
        costs["ai_models"] = 3.0  # Maximum from your Grok budget
        
        # Bhojpuri language processing (essential cost)
        if self.is_service_enabled("bhojpuri_model"):
            costs["language_processing"] = 5.0  # Minimal cost for Bhojpuri support
        
        # Future multimedia (provisioned but not active)
        costs["multimedia_generation"] = 0.0  # Ready but not enabled
        
        costs["total_usd"] = sum(costs.values())
        
        return costs
    
    def get_multimedia_cost_estimate(self) -> Dict[str, float]:
        """Estimate future multimedia costs when enabled"""
        multimedia_costs = {
            "daily_images": 0.0,
            "daily_videos": 0.0,
            "monthly_total": 0.0
        }
        
        # Image generation costs (when enabled)
        if self.is_service_enabled("image_generation"):
            daily_image_cost = self.multimedia.max_images_per_day * 0.02  # DALL-E pricing
            multimedia_costs["daily_images"] = daily_image_cost
        
        # Video generation costs (when enabled)  
        if self.is_service_enabled("video_generation"):
            daily_video_cost = self.multimedia.max_videos_per_day * 10 * 0.08  # 10 sec videos
            multimedia_costs["daily_videos"] = daily_video_cost
        
        multimedia_costs["monthly_total"] = (
            multimedia_costs["daily_images"] + multimedia_costs["daily_videos"]
        ) * 30
        
        return multimedia_costs
    
    def get_cost_report(self) -> str:
        """Generate zero-cost configuration report with Bhojpuri and multimedia provisions"""
        costs = self.get_monthly_cost_estimate()
        multimedia_costs = self.get_multimedia_cost_estimate()
        
        report = f"""
🆓 ZERO-COST EXPERIMENTAL CONFIGURATION (WITH BHOJPURI)
{'='*60}

💰 CURRENT MONTHLY COST: ${costs['total_usd']:.2f}
   (Including essential Bhojpuri language support)

🎯 DAILY OPERATIONS:
   • {self.local_infra.tweets_per_day} tweets per day (every {self.local_infra.posting_interval_hours} hours)
   • {self.local_infra.language_distribution['hi']*100:.0f}% Hindi, {self.local_infra.language_distribution['bho']*100:.0f}% Bhojpuri, {self.local_infra.language_distribution['en']*100:.0f}% English
   • Local storage (no cloud costs)
   • Free-tier services only

✅ ENABLED SERVICES (FREE + ESSENTIAL):
   • ChatGPT API (your existing)
   • Grok API (₹250 budget)
   • 🏘️ Bhojpuri Language Model (ESSENTIAL)
   • Google Translate (free tier)
   • NewsAPI (free tier)
   • Local logging & storage
   • Built-in security scanning
   • Stable Diffusion (free, local install)

❌ DISABLED SERVICES (COST SAVINGS):
   • All paid fact-checking APIs
   • Premium news sources
   • Cloud infrastructure
   • Advanced monitoring

🚀 PROVISIONED FOR FUTURE (READY TO ENABLE):
   • 🎨 AI Image Generation (DALL-E, Midjourney)
   • 🎬 AI Video Generation (Runway, Pika, Luma, Kling)
   • 🎵 AI Audio Generation (ElevenLabs, Murf)
   • 🎭 Avatar & Animation Generation

🏠 LOCAL INFRASTRUCTURE:
   • SQLite database (instead of MongoDB)
   • Local file cache (instead of Redis)
   • Local backup storage
   • Media storage for future images/videos
   • No hosting costs

📊 LANGUAGE DISTRIBUTION (15 tweets/day):
   • Hindi: 9 tweets/day ({self.local_infra.language_distribution['hi']*100:.0f}%)
   • Bhojpuri: 4-5 tweets/day ({self.local_infra.language_distribution['bho']*100:.0f}%)
   • English: 1-2 tweets/day ({self.local_infra.language_distribution['en']*100:.0f}%)

💡 FUTURE MULTIMEDIA COSTS (when enabled):
   • Images: ${multimedia_costs['daily_images']:.2f}/day
   • Videos: ${multimedia_costs['daily_videos']:.2f}/day
   • Monthly: ${multimedia_costs['monthly_total']:.2f}

📈 COST SAVINGS: ~$130/month compared to full deployment
"""
        return report

# Global zero-cost configuration instance
zero_cost_manager = ZeroCostBotManager()