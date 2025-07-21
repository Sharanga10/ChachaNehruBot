"""
Zero-Cost Experimental Configuration
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
    
    # Enabled services (FREE ONLY)
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
                
                # Language Processing (FREE ONLY)
                "google_translate": True,   # Free tier: 500,000 chars/month
                "bhojpuri_model": False,    # Paid service - disable for now
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
            }

@dataclass
class LocalInfrastructureConfig:
    """Configuration for local infrastructure (zero cost)"""
    
    # Local storage paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    cache_dir: str = "cache"
    backup_dir: str = "backups"
    
    # Local database (SQLite instead of MongoDB)
    database_file: str = "data/bot_database.sqlite"
    
    # Local cache (dict/file instead of Redis)
    cache_file: str = "cache/content_cache.json"
    cache_max_size: int = 1000  # Maximum cached items
    
    # Reduced posting frequency (to save API costs)
    tweets_per_day: int = 10    # Reduced from 50 to save costs
    posting_interval_hours: int = 2.4  # Every 2.4 hours
    
    # Language distribution (simplified)
    language_distribution: Dict[str, float] = None
    
    def __post_init__(self):
        if self.language_distribution is None:
            # Simplified to reduce translation costs
            self.language_distribution = {
                "hi": 0.70,   # Hindi: 70% (7 tweets/day)
                "en": 0.30    # English: 30% (3 tweets/day)
                # Bhojpuri disabled for now to save costs
            }

class ZeroCostBotManager:
    """Zero-cost bot configuration manager"""
    
    def __init__(self):
        self.zero_cost = ZeroCostConfig()
        self.local_infra = LocalInfrastructureConfig()
        self.setup_local_directories()
        self.setup_logging()
    
    def setup_local_directories(self):
        """Create local directories for zero-cost operation"""
        directories = [
            self.local_infra.data_dir,
            self.local_infra.logs_dir,
            self.local_infra.cache_dir,
            self.local_infra.backup_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
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
        }
        
        env_var = key_mapping.get(service)
        if env_var:
            return os.getenv(env_var)
        return None
    
    def is_service_enabled(self, service: str) -> bool:
        """Check if service is enabled in zero-cost mode"""
        return self.zero_cost.enabled_services.get(service, False)
    
    def get_daily_tweet_quota(self) -> int:
        """Get reduced daily tweet quota for cost savings"""
        return self.local_infra.tweets_per_day
    
    def get_language_for_tweet(self, tweet_number: int) -> str:
        """Get language for tweet (simplified distribution)"""
        # 70% Hindi, 30% English (no Bhojpuri for now to save costs)
        if tweet_number % 10 < 7:
            return "hi"
        else:
            return "en"
    
    def get_monthly_cost_estimate(self) -> Dict[str, float]:
        """Estimate monthly costs (should be near zero)"""
        costs = {
            "ai_models": 0.0,
            "fact_checking": 0.0,
            "news_apis": 0.0,
            "security_tools": 0.0,
            "language_processing": 0.0,
            "infrastructure": 0.0,
            "monitoring": 0.0,
            "total_usd": 0.0
        }
        
        # Only count your existing API usage (with cost controls)
        # ChatGPT: Free tier or your existing credits
        # Grok: Your ₹250 budget = ~$3
        costs["ai_models"] = 3.0  # Maximum from your Grok budget
        costs["total_usd"] = 3.0
        
        return costs
    
    def get_cost_report(self) -> str:
        """Generate zero-cost configuration report"""
        costs = self.get_monthly_cost_estimate()
        
        report = f"""
🆓 ZERO-COST EXPERIMENTAL CONFIGURATION
{'='*50}

💰 MONTHLY COST ESTIMATE: ${costs['total_usd']:.2f}
   (Using your existing ChatGPT + Grok APIs only)

🎯 DAILY OPERATIONS:
   • {self.local_infra.tweets_per_day} tweets per day (reduced from 50)
   • {self.local_infra.language_distribution['hi']*100:.0f}% Hindi, {self.local_infra.language_distribution['en']*100:.0f}% English
   • Local storage (no cloud costs)
   • Free-tier services only

✅ ENABLED SERVICES (FREE):
   • ChatGPT API (your existing)
   • Grok API (₹250 budget)
   • Google Translate (free tier)
   • NewsAPI (free tier)
   • Local logging & storage
   • Built-in security scanning

❌ DISABLED SERVICES (COST SAVINGS):
   • All paid fact-checking APIs
   • Premium news sources
   • Cloud infrastructure
   • Advanced monitoring
   • Bhojpuri language model (for now)

🏠 LOCAL INFRASTRUCTURE:
   • SQLite database (instead of MongoDB)
   • Local file cache (instead of Redis)
   • Local backup storage
   • No hosting costs

📈 COST SAVINGS: ~$135/month compared to full deployment
"""
        return report

# Global zero-cost configuration instance
zero_cost_manager = ZeroCostBotManager()