"""
Enhanced Configuration Management System
Centralized, secure, and environment-aware configuration
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    rate_limit_requests_per_minute: int = 10
    max_daily_posts: int = 50  # Updated to match original target
    content_retention_days: int = 30
    encryption_key_rotation_days: int = 7
    audit_log_retention_days: int = 90
    api_timeout_seconds: int = 30
    max_retry_attempts: int = 3

@dataclass
class FactCheckConfig:
    """Fact-checking configuration"""
    enabled: bool = True
    confidence_threshold: float = 0.85
    sources_required: int = 3
    verification_timeout: int = 15
    fallback_to_conservative: bool = True
    real_time_verification: bool = True
    historical_context_check: bool = True

@dataclass
class AIModelConfig:
    """AI Model configuration with fallback hierarchy"""
    primary_model: str = "grok"
    fallback_models: list = None
    cost_per_request: Dict[str, float] = None
    rate_limits: Dict[str, int] = None
    quality_scores: Dict[str, float] = None
    
    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = ["grok", "claude", "chatgpt", "gemini", "sarvam"]
        if self.cost_per_request is None:
            self.cost_per_request = {
                "grok": 0.002, "claude": 0.003, "chatgpt": 0.002,
                "gemini": 0.001, "sarvam": 0.0005
            }
        if self.rate_limits is None:
            self.rate_limits = {
                "grok": 100, "claude": 50, "chatgpt": 60,
                "gemini": 120, "sarvam": 200
            }
        if self.quality_scores is None:
            self.quality_scores = {
                "grok": 0.92, "claude": 0.95, "chatgpt": 0.90,
                "gemini": 0.88, "sarvam": 0.85
            }

@dataclass
class EthicsConfig:
    """Ethical guidelines configuration"""
    bias_detection_enabled: bool = True
    cultural_sensitivity_check: bool = True
    misinformation_prevention: bool = True
    hate_speech_detection: bool = True
    political_neutrality_check: bool = True
    fact_verification_required: bool = True
    human_review_threshold: float = 0.7

@dataclass
class SchedulerConfig:
    """Scheduler configuration for automated posting"""
    daily_tweet_quota: int = 50
    tweet_gap_minutes: int = 30  # 30 minutes between tweets
    active_hours_start: str = "06:00"
    active_hours_end: str = "23:30"
    timezone: str = "Asia/Kolkata"
    enforce_exact_quota: bool = True
    
    # Distribution blocks for 50 tweets/day
    schedule_blocks: list = None
    
    def __post_init__(self):
        if self.schedule_blocks is None:
            # Distribute 50 tweets across active hours (17.5 hours = 6:00-23:30)
            # Morning: 15 tweets (6:00-11:30)
            # Afternoon: 15 tweets (11:30-17:30) 
            # Evening: 20 tweets (17:30-23:30)
            self.schedule_blocks = [
                {"start": "06:00", "end": "11:30", "max": 15, "interval_minutes": 22},
                {"start": "11:30", "end": "17:30", "max": 15, "interval_minutes": 24},
                {"start": "17:30", "end": "23:30", "max": 20, "interval_minutes": 18}
            ]

@dataclass
class LanguageConfig:
    """Language configuration with Bhojpuri support"""
    primary_language: str = "hi"  # Hindi
    supported_languages: list = None
    language_distribution: Dict[str, float] = None
    bhojpuri_model_enabled: bool = True
    translation_api_key: str = ""
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["hi", "bho", "en"]  # Hindi, Bhojpuri, English
        
        if self.language_distribution is None:
            self.language_distribution = {
                "hi": 0.70,   # Hindi: 70% (35 tweets/day)
                "bho": 0.20,  # Bhojpuri: 20% (10 tweets/day)
                "en": 0.10    # English: 10% (5 tweets/day)
            }

@dataclass
class CostOptimizationConfig:
    """Cost optimization and service provisioning configuration"""
    deployment_phase: str = "phase1"  # phase1, phase2, phase3
    
    # Service provisioning flags
    premium_fact_check_enabled: bool = False
    advanced_news_apis_enabled: bool = False
    bias_detection_enabled: bool = False
    performance_monitoring_enabled: bool = False
    high_availability_enabled: bool = False
    advanced_analytics_enabled: bool = False
    
    # Cost tracking
    monthly_budget_limit: float = 150.00  # Phase 1 budget
    cost_alerts_enabled: bool = True
    usage_monitoring_enabled: bool = True
    
    # API service configurations
    enabled_services: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.enabled_services is None:
            # Phase 1 - Essential services only
            if self.deployment_phase == "phase1":
                self.enabled_services = {
                    # AI Models (Essential)
                    "grok": True,
                    "chatgpt": True,
                    "sarvam": True,
                    "claude": False,  # Provision for future
                    "gemini": False,  # Provision for future
                    
                    # Fact-checking (Basic)
                    "google_factcheck": True,
                    "snopes": True,
                    "politifact": False,  # Provision for future
                    "factcheck_org": False,  # Provision for future
                    
                    # News APIs (Basic)
                    "newsapi": True,
                    "times_of_india": True,
                    "guardian": False,  # Provision for future
                    "reuters": False,  # Provision for future
                    "ap_news": False,  # Provision for future
                    
                    # Security (Essential)
                    "content_security_scanner": True,
                    "malicious_url_checker": True,
                    "sentiment_analysis": True,
                    "hate_speech_detection": True,
                    "bias_detection": False,  # Provision for future
                    
                    # Language Processing
                    "google_translate": True,
                    "bhojpuri_model": True,
                    "hindi_sentiment": True,
                    "indic_nlp": True,
                    "azure_cognitive": False,  # Provision for future
                    
                    # Infrastructure (Basic)
                    "redis_cache": True,
                    "mongodb": True,
                    "backup_storage": True,
                    "cdn": False,  # Provision for future
                    "load_balancer": False,  # Provision for future
                    
                    # Monitoring (Basic)
                    "uptime_monitoring": True,
                    "basic_logging": True,
                    "performance_metrics": False,  # Provision for future
                    "twitter_analytics": False,  # Provision for future
                    "custom_dashboard": False,  # Provision for future
                }
            
            # Phase 2 - Growth features
            elif self.deployment_phase == "phase2":
                self.enabled_services.update({
                    "claude": True,
                    "politifact": True,
                    "guardian": True,
                    "bias_detection": True,
                    "performance_metrics": True,
                    "azure_cognitive": True,
                })
            
            # Phase 3 - Full deployment
            elif self.deployment_phase == "phase3":
                # Enable all services
                self.enabled_services = {key: True for key in self.enabled_services.keys()}

class EnhancedConfigManager:
    """Advanced configuration management with environment awareness"""
    
    def __init__(self, env: str = "production"):
        self.env = env
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize configurations
        self.security = SecurityConfig()
        self.fact_check = FactCheckConfig()
        self.ai_models = AIModelConfig()
        self.ethics = EthicsConfig()
        self.scheduler = SchedulerConfig()
        self.language = LanguageConfig()
        self.cost_optimization = CostOptimizationConfig()
        
        self._load_configurations()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/config_{self.env}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_configurations(self):
        """Load configurations from files with environment overrides"""
        # Load from existing JSON files
        self._load_scheduler_config()
        self._load_tweet_schedule()
        
        config_files = {
            'security': f'security_{self.env}.yaml',
            'fact_check': f'fact_check_{self.env}.yaml',
            'ai_models': f'ai_models_{self.env}.yaml',
            'ethics': f'ethics_{self.env}.yaml'
        }
        
        for config_type, filename in config_files.items():
            config_path = self.config_dir / filename
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                    self._update_config(config_type, config_data)
                except Exception as e:
                    self.logger.warning(f"Failed to load {filename}: {e}")
    
    def _load_scheduler_config(self):
        """Load scheduler configuration from existing JSON file"""
        try:
            with open("scheduler_config.json", "r") as f:
                config_data = json.load(f)
            
            self.scheduler.daily_tweet_quota = config_data.get("daily_tweet_quota", 50)
            self.scheduler.tweet_gap_minutes = config_data.get("tweet_gap_minutes", 30)
            
            active_hours = config_data.get("active_hours", {})
            self.scheduler.active_hours_start = active_hours.get("start", "06:00")
            self.scheduler.active_hours_end = active_hours.get("end", "23:30")
            self.scheduler.timezone = config_data.get("timezone", "Asia/Kolkata")
            self.scheduler.enforce_exact_quota = config_data.get("enforce_exact_quota", True)
            
        except Exception as e:
            self.logger.warning(f"Could not load scheduler_config.json: {e}")
    
    def _load_tweet_schedule(self):
        """Load tweet schedule from existing JSON file"""
        try:
            with open("tweet_schedule.json", "r") as f:
                config_data = json.load(f)
            
            # Override daily limit from tweet_schedule.json
            if config_data.get("daily_limit"):
                self.scheduler.daily_tweet_quota = config_data["daily_limit"]
                self.security.max_daily_posts = config_data["daily_limit"]
            
            # Load schedule blocks
            if config_data.get("schedule_blocks"):
                self.scheduler.schedule_blocks = config_data["schedule_blocks"]
            
        except Exception as e:
            self.logger.warning(f"Could not load tweet_schedule.json: {e}")
    
    def _update_config(self, config_type: str, data: Dict[str, Any]):
        """Update configuration with loaded data"""
        if config_type == 'security':
            for key, value in data.items():
                if hasattr(self.security, key):
                    setattr(self.security, key, value)
        elif config_type == 'fact_check':
            for key, value in data.items():
                if hasattr(self.fact_check, key):
                    setattr(self.fact_check, key, value)
        # Add similar updates for other config types
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Securely retrieve API keys from environment"""
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'grok': 'XAI_API_KEY',
            'claude': 'ANTHROPIC_API_KEY',
            'gemini': 'GOOGLE_API_KEY',
            'sarvam': 'SARVAM_API_KEY',
            'twitter': 'X_BEARER_TOKEN',
            'factcheck': 'FACTCHECK_API_KEY'
        }
        
        env_var = key_mapping.get(service)
        if not env_var:
            self.logger.error(f"Unknown service: {service}")
            return None
        
        api_key = os.getenv(env_var)
        if not api_key:
            self.logger.error(f"API key not found for {service}")
        
        return api_key
    
    def validate_configuration(self) -> bool:
        """Validate all configurations"""
        validations = [
            self.security.rate_limit_requests_per_minute > 0,
            self.fact_check.confidence_threshold >= 0.5,
            len(self.ai_models.fallback_models) >= 2,
            self.ethics.bias_detection_enabled is True,
            self.scheduler.daily_tweet_quota > 0,
            self.scheduler.daily_tweet_quota <= 100  # Reasonable upper limit
        ]
        
        return all(validations)
    
    def get_cost_optimized_model(self, quality_threshold: float = 0.85) -> str:
        """Get the most cost-effective model meeting quality threshold"""
        eligible_models = {
            model: score for model, score in self.ai_models.quality_scores.items()
            if score >= quality_threshold
        }
        
        if not eligible_models:
            return self.ai_models.primary_model
        
        # Sort by cost (ascending) among eligible models
        cost_sorted = sorted(
            eligible_models.keys(),
            key=lambda x: self.ai_models.cost_per_request[x]
        )
        
        return cost_sorted[0]
    
    def get_posting_schedule(self) -> Dict[str, Any]:
        """Get the complete posting schedule for 50 tweets/day"""
        return {
            "daily_quota": self.scheduler.daily_tweet_quota,
            "active_hours": f"{self.scheduler.active_hours_start}-{self.scheduler.active_hours_end}",
            "schedule_blocks": self.scheduler.schedule_blocks,
            "timezone": self.scheduler.timezone,
            "average_interval_minutes": (17.5 * 60) / self.scheduler.daily_tweet_quota  # ~21 minutes
        }

    def get_language_for_tweet(self, tweet_number: int) -> str:
        """Get language for specific tweet based on distribution"""
        # Use deterministic distribution based on tweet number
        distribution = self.language.language_distribution
        
        if tweet_number % 10 < 7:  # 70% Hindi
            return "hi"
        elif tweet_number % 10 < 9:  # 20% Bhojpuri (positions 7-8)
            return "bho"
        else:  # 10% English (positions 9)
            return "en"
    
    def get_daily_language_distribution(self) -> Dict[str, int]:
        """Get daily tweet count by language"""
        total_daily = self.scheduler.daily_tweet_quota
        return {
            "hi": int(total_daily * self.language.language_distribution["hi"]),    # 35 tweets
            "bho": int(total_daily * self.language.language_distribution["bho"]),  # 10 tweets  
            "en": int(total_daily * self.language.language_distribution["en"])     # 5 tweets
        }
    
    def is_service_enabled(self, service_name: str) -> bool:
        """Check if a service is enabled in current deployment phase"""
        return self.cost_optimization.enabled_services.get(service_name, False)
    
    def get_monthly_cost_estimate(self) -> Dict[str, float]:
        """Calculate estimated monthly costs based on enabled services"""
        costs = {
            "ai_models": 0.0,
            "fact_checking": 0.0,
            "news_apis": 0.0,
            "security_tools": 0.0,
            "language_processing": 0.0,
            "infrastructure": 0.0,
            "monitoring": 0.0,
            "security_compliance": 0.0
        }
        
        # AI Models
        if self.is_service_enabled("grok"):
            costs["ai_models"] += 2.10  # $2.10/month
        if self.is_service_enabled("chatgpt"):
            costs["ai_models"] += 0.60  # $0.60/month
        if self.is_service_enabled("sarvam"):
            costs["ai_models"] += 0.075  # $0.075/month
        if self.is_service_enabled("claude"):
            costs["ai_models"] += 0.90  # $0.90/month (future)
        if self.is_service_enabled("gemini"):
            costs["ai_models"] += 0.30  # $0.30/month (future)
        
        # Fact-checking
        if self.is_service_enabled("google_factcheck"):
            costs["fact_checking"] += 5.00
        if self.is_service_enabled("snopes"):
            costs["fact_checking"] += 15.00
        if self.is_service_enabled("politifact"):
            costs["fact_checking"] += 12.00
        if self.is_service_enabled("factcheck_org"):
            costs["fact_checking"] += 10.00
        
        # News APIs
        if self.is_service_enabled("newsapi"):
            costs["news_apis"] += 10.00
        if self.is_service_enabled("times_of_india"):
            costs["news_apis"] += 6.00
        if self.is_service_enabled("guardian"):
            costs["news_apis"] += 8.00
        if self.is_service_enabled("reuters"):
            costs["news_apis"] += 15.00
        if self.is_service_enabled("ap_news"):
            costs["news_apis"] += 12.00
        
        # Security Tools
        if self.is_service_enabled("content_security_scanner"):
            costs["security_tools"] += 5.00
        if self.is_service_enabled("malicious_url_checker"):
            costs["security_tools"] += 3.00
        if self.is_service_enabled("sentiment_analysis"):
            costs["security_tools"] += 4.00
        if self.is_service_enabled("hate_speech_detection"):
            costs["security_tools"] += 6.00
        if self.is_service_enabled("bias_detection"):
            costs["security_tools"] += 8.00
        
        # Language Processing
        if self.is_service_enabled("google_translate"):
            costs["language_processing"] += 8.00
        if self.is_service_enabled("bhojpuri_model"):
            costs["language_processing"] += 15.00
        if self.is_service_enabled("hindi_sentiment"):
            costs["language_processing"] += 6.00
        if self.is_service_enabled("indic_nlp"):
            costs["language_processing"] += 4.00
        if self.is_service_enabled("azure_cognitive"):
            costs["language_processing"] += 12.00
        
        # Infrastructure
        costs["infrastructure"] += 20.00  # VPS (always needed)
        if self.is_service_enabled("mongodb"):
            costs["infrastructure"] += 5.00
        if self.is_service_enabled("redis_cache"):
            costs["infrastructure"] += 3.00
        if self.is_service_enabled("backup_storage"):
            costs["infrastructure"] += 4.00
        if self.is_service_enabled("cdn"):
            costs["infrastructure"] += 2.00
        if self.is_service_enabled("load_balancer"):
            costs["infrastructure"] += 15.00
        
        # Monitoring
        if self.is_service_enabled("uptime_monitoring"):
            costs["monitoring"] += 5.00
        if self.is_service_enabled("performance_metrics"):
            costs["monitoring"] += 8.00
        if self.is_service_enabled("twitter_analytics"):
            costs["monitoring"] += 10.00
        if self.is_service_enabled("custom_dashboard"):
            costs["monitoring"] += 12.00
        
        # Security & Compliance
        costs["security_compliance"] += 2.00  # SSL (always needed)
        costs["security_compliance"] += 6.00  # Audit logging (always needed)
        costs["security_compliance"] += 4.00  # Data encryption (always needed)
        
        return costs
    
    def get_total_monthly_cost(self) -> float:
        """Get total estimated monthly cost"""
        costs = self.get_monthly_cost_estimate()
        return sum(costs.values())
    
    def get_cost_breakdown_report(self) -> str:
        """Generate detailed cost breakdown report"""
        costs = self.get_monthly_cost_estimate()
        total = sum(costs.values())
        
        report = f"""
💰 MONTHLY COST BREAKDOWN - {self.cost_optimization.deployment_phase.upper()}
{'='*60}

📊 By Category:
"""
        for category, cost in costs.items():
            if cost > 0:
                percentage = (cost / total) * 100
                report += f"   {category.replace('_', ' ').title()}: ${cost:.2f} ({percentage:.1f}%)\n"
        
        report += f"""
💵 TOTAL MONTHLY COST: ${total:.2f}

🌐 Language Distribution (50 tweets/day):
   Hindi (70%): 35 tweets/day
   Bhojpuri (20%): 10 tweets/day  
   English (10%): 5 tweets/day

📈 Cost per Tweet: ${total/1500:.3f}
📅 Cost per Day: ${total/30:.2f}

🎯 Budget Status: {'✅ WITHIN BUDGET' if total <= self.cost_optimization.monthly_budget_limit else '⚠️ OVER BUDGET'}
"""
        
        return report

# Global configuration instance
config_manager = EnhancedConfigManager()