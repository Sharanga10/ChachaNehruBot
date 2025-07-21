"""
Enhanced Main Application - World's Most Ethical AI Bot
Zero-downtime, fact-checked, secure automated social media bot
Configured for 50 tweets per day with intelligent distribution
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import signal
import json
import random

# Enhanced imports
from config.main_config import config_manager
from core.enhanced_content_generator import enhanced_content_generator, ContentType
from core.fact_checker import fact_checker, FactCheckStatus
from core.security_manager import security_manager
from post_to_twitter import post_to_twitter

# Monitoring and scheduling
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import structlog

class EnhancedBotOrchestrator:
    """
    World-class bot orchestrator configured for 50 tweets/day with:
    1. Ethical content generation
    2. Multi-layered fact-checking
    3. Enterprise security
    4. Zero-downtime operations
    5. Cost optimization
    6. Comprehensive monitoring
    """
    
    def __init__(self):
        self.setup_logging()
        self.logger = structlog.get_logger(__name__)
        
        # Configuration
        self.config = config_manager
        
        # Scheduler for automated operations
        self.scheduler = AsyncIOScheduler()
        
        # Performance metrics
        self.metrics = {
            'total_posts': 0,
            'successful_posts': 0,
            'failed_posts': 0,
            'fact_check_passes': 0,
            'fact_check_failures': 0,
            'security_blocks': 0,
            'start_time': datetime.now(),
            'daily_quota': self.config.scheduler.daily_tweet_quota,
            'posts_today': 0,
            'last_reset_date': datetime.now().date()
        }
        
        # Circuit breaker for emergency shutdown
        self.emergency_shutdown = False
        
        # Health check status
        self.health_status = {
            'status': 'starting',
            'last_successful_post': None,
            'last_health_check': datetime.now(),
            'daily_progress': '0/50',
            'components': {
                'content_generator': 'unknown',
                'fact_checker': 'unknown',
                'security_manager': 'unknown',
                'twitter_api': 'unknown'
            }
        }
        
        # Content type rotation for variety
        self.content_types = [
            ContentType.SATIRICAL,
            ContentType.INFORMATIVE,
            ContentType.REFLECTIVE,
            ContentType.CULTURAL,
            ContentType.HISTORICAL
        ]
        self.current_content_index = 0
    
    def setup_logging(self):
        """Setup structured logging with multiple outputs"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        os.makedirs('logs/security', exist_ok=True)
        os.makedirs('logs/audit', exist_ok=True)
        
        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Setup file handlers
        logging.basicConfig(
            level=logging.INFO,
            handlers=[
                logging.FileHandler('logs/bot_main.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    async def initialize(self):
        """Initialize all bot components"""
        self.logger.info("🚀 Initializing Enhanced Ethical Bot System (50 tweets/day)")
        
        try:
            # Validate configuration
            if not self.config.validate_configuration():
                raise RuntimeError("Configuration validation failed")
            
            # Initialize components
            await self._initialize_components()
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Setup 50 tweets/day scheduler
            self._setup_high_volume_scheduler()
            
            # Start health monitoring
            asyncio.create_task(self._health_monitor())
            
            # Start metrics collection
            asyncio.create_task(self._metrics_collector())
            
            # Start daily reset task
            asyncio.create_task(self._daily_reset_task())
            
            self.health_status['status'] = 'running'
            
            # Log the posting schedule
            schedule_info = self.config.get_posting_schedule()
            self.logger.info("✅ Bot system initialized successfully", 
                           daily_quota=schedule_info['daily_quota'],
                           active_hours=schedule_info['active_hours'],
                           avg_interval=f"{schedule_info['average_interval_minutes']:.1f} minutes")
            
        except Exception as e:
            self.logger.error("❌ Failed to initialize bot system", error=str(e))
            raise
    
    async def _initialize_components(self):
        """Initialize and test all components"""
        # Test content generator
        try:
            test_content, metadata = await enhanced_content_generator.generate_ethical_content(
                topic="test initialization",
                content_type=ContentType.REFLECTIVE,
                language="en"
            )
            self.health_status['components']['content_generator'] = 'healthy' if test_content else 'error'
        except Exception as e:
            self.logger.warning("Content generator initialization issue", error=str(e))
            self.health_status['components']['content_generator'] = 'error'
        
        # Test fact checker
        try:
            test_fact_check = await fact_checker.comprehensive_fact_check("Test statement for initialization")
            self.health_status['components']['fact_checker'] = 'healthy' if test_fact_check else 'error'
        except Exception as e:
            self.logger.warning("Fact checker initialization issue", error=str(e))
            self.health_status['components']['fact_checker'] = 'error'
        
        # Test security manager
        try:
            security_status = security_manager.get_security_status()
            self.health_status['components']['security_manager'] = 'healthy' if security_status else 'error'
        except Exception as e:
            self.logger.warning("Security manager initialization issue", error=str(e))
            self.health_status['components']['security_manager'] = 'error'
        
        # Test Twitter API (without posting)
        try:
            # This would be a test connection - implement based on your Twitter API setup
            self.health_status['components']['twitter_api'] = 'healthy'  # Assume healthy for now
        except Exception as e:
            self.logger.warning("Twitter API initialization issue", error=str(e))
            self.health_status['components']['twitter_api'] = 'error'
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
            self.emergency_shutdown = True
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def _setup_high_volume_scheduler(self):
        """Setup scheduler for 50 tweets per day with intelligent distribution"""
        
        schedule_blocks = self.config.scheduler.schedule_blocks
        
        self.logger.info("📅 Setting up high-volume scheduler (50 tweets/day)")
        
        # Schedule for each time block
        for i, block in enumerate(schedule_blocks):
            start_hour, start_minute = map(int, block['start'].split(':'))
            end_hour, end_minute = map(int, block['end'].split(':'))
            max_tweets = block['max']
            interval_minutes = block['interval_minutes']
            
            self.logger.info(f"   Block {i+1}: {block['start']}-{block['end']} "
                           f"({max_tweets} tweets, every {interval_minutes}min)")
            
            # Create interval job for this block
            self.scheduler.add_job(
                self._scheduled_post_with_time_check,
                IntervalTrigger(minutes=interval_minutes),
                args=[block],
                id=f"posting_block_{i+1}",
                max_instances=1,
                coalesce=True
            )
        
        # Health check every 5 minutes
        self.scheduler.add_job(
            self.health_check,
            'interval',
            minutes=5,
            id="health_check",
            max_instances=1
        )
        
        # Daily metrics report at midnight
        self.scheduler.add_job(
            self.generate_daily_report,
            CronTrigger(hour=0, minute=0),
            id="daily_report",
            max_instances=1
        )
        
        # Hourly progress report
        self.scheduler.add_job(
            self._hourly_progress_report,
            CronTrigger(minute=0),  # Every hour
            id="hourly_progress",
            max_instances=1
        )
        
        # Start scheduler
        self.scheduler.start()
        self.logger.info("📅 High-volume scheduler initialized (50 tweets/day)")
    
    async def _scheduled_post_with_time_check(self, block_config: Dict[str, Any]):
        """Generate and post content with time block validation"""
        current_time = datetime.now().time()
        start_time = datetime.strptime(block_config['start'], '%H:%M').time()
        end_time = datetime.strptime(block_config['end'], '%H:%M').time()
        
        # Check if current time is within the block's active hours
        if not (start_time <= current_time <= end_time):
            return  # Skip if outside active hours
        
        # Check daily quota
        await self._reset_daily_counter_if_needed()
        
        if self.metrics['posts_today'] >= self.config.scheduler.daily_tweet_quota:
            self.logger.info(f"📊 Daily quota reached: {self.metrics['posts_today']}/{self.config.scheduler.daily_tweet_quota}")
            return
        
        # Generate and post content
        await self.generate_and_post_content()
    
    async def _reset_daily_counter_if_needed(self):
        """Reset daily counter at midnight"""
        current_date = datetime.now().date()
        if current_date > self.metrics['last_reset_date']:
            self.logger.info(f"🔄 Daily reset: {self.metrics['posts_today']} tweets posted yesterday")
            self.metrics['posts_today'] = 0
            self.metrics['last_reset_date'] = current_date
            self.health_status['daily_progress'] = f"0/{self.config.scheduler.daily_tweet_quota}"
    
    async def _daily_reset_task(self):
        """Background task to handle daily resets"""
        while not self.emergency_shutdown:
            try:
                await self._reset_daily_counter_if_needed()
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                self.logger.error(f"Daily reset task error: {e}")
                await asyncio.sleep(3600)
    
    async def _hourly_progress_report(self):
        """Generate hourly progress report"""
        progress = f"{self.metrics['posts_today']}/{self.config.scheduler.daily_tweet_quota}"
        percentage = (self.metrics['posts_today'] / self.config.scheduler.daily_tweet_quota) * 100
        
        self.logger.info("📊 Hourly Progress Report",
                        posts_today=self.metrics['posts_today'],
                        daily_quota=self.config.scheduler.daily_tweet_quota,
                        progress_percentage=f"{percentage:.1f}%",
                        successful_posts=self.metrics['successful_posts'],
                        failed_posts=self.metrics['failed_posts'])
        
        self.health_status['daily_progress'] = progress
    
    async def generate_and_post_content(self, manual_topic: str = None, 
                                      content_type: ContentType = None):
        """
        Main content generation and posting pipeline optimized for high volume
        """
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger.info("🎯 Starting content generation pipeline", 
                        post_id=post_id,
                        daily_progress=f"{self.metrics['posts_today']}/{self.config.scheduler.daily_tweet_quota}")
        
        try:
            # Check if we're in emergency shutdown
            if self.emergency_shutdown:
                self.logger.warning("Emergency shutdown active, skipping post generation")
                return False
            
            # Rate limiting check (using daily quota)
            if not security_manager.check_rate_limit("daily_posts", self.config.security.max_daily_posts, 86400):
                self.logger.warning("Daily post limit exceeded")
                self.metrics['failed_posts'] += 1
                return False
            
            # Determine current mode and content type
            current_hour = datetime.now().hour
            mode = "NIGHT" if current_hour < 6 or current_hour > 22 else "DAY"
            
            # Select content type with rotation for variety
            if content_type is None:
                content_type = self._get_next_content_type(current_hour)
            
            # Select language (80% Hindi, 20% English for variety)
            language = "hi" if random.random() < 0.8 else "en"
            
            # Generate ethical content
            self.logger.info("🤖 Generating ethical content", 
                           content_type=content_type.value, 
                           mode=mode, 
                           language=language)
            
            content, metadata = await enhanced_content_generator.generate_ethical_content(
                topic=manual_topic,
                content_type=content_type,
                language=language,
                mode=mode
            )
            
            if not content:
                self.logger.warning("❌ Content generation failed", 
                                  reason=metadata.security_scan_result.get('threats', ['unknown']))
                self.metrics['failed_posts'] += 1
                return False
            
            # Additional validation layer
            validation_result = await self._final_content_validation(content, metadata)
            if not validation_result['approved']:
                self.logger.warning("❌ Content failed final validation", 
                                  reason=validation_result['reason'])
                self.metrics['failed_posts'] += 1
                return False
            
            # Post to Twitter
            self.logger.info("📤 Posting to Twitter", content_preview=content[:50])
            post_result = post_to_twitter(content)
            
            if post_result:
                # Success metrics and logging
                self.metrics['successful_posts'] += 1
                self.metrics['total_posts'] += 1
                self.metrics['posts_today'] += 1
                self.health_status['last_successful_post'] = datetime.now()
                
                # Update progress
                self.health_status['daily_progress'] = f"{self.metrics['posts_today']}/{self.config.scheduler.daily_tweet_quota}"
                
                # Log successful post for audit
                await self._log_successful_post(content, metadata, post_id)
                
                self.logger.info("✅ Content posted successfully", 
                               post_id=post_id,
                               model_used=metadata.model_used,
                               quality_score=metadata.quality_score,
                               daily_progress=self.health_status['daily_progress'])
                return True
            else:
                self.metrics['failed_posts'] += 1
                self.logger.error("❌ Failed to post to Twitter", post_id=post_id)
                return False
                
        except Exception as e:
            self.metrics['failed_posts'] += 1
            self.logger.error("❌ Content generation pipeline failed", 
                            post_id=post_id, error=str(e), exc_info=True)
            return False
    
    def _get_next_content_type(self, current_hour: int) -> ContentType:
        """Get next content type with time-based preferences and rotation"""
        # Time-based preferences
        if 6 <= current_hour < 10:  # Morning: Educational
            preferred_types = [ContentType.INFORMATIVE, ContentType.REFLECTIVE]
        elif 10 <= current_hour < 14:  # Late morning: Cultural
            preferred_types = [ContentType.CULTURAL, ContentType.HISTORICAL]
        elif 14 <= current_hour < 18:  # Afternoon: Mixed
            preferred_types = [ContentType.SATIRICAL, ContentType.INFORMATIVE]
        elif 18 <= current_hour < 22:  # Evening: Reflective
            preferred_types = [ContentType.REFLECTIVE, ContentType.CULTURAL]
        else:  # Night: Light content
            preferred_types = [ContentType.SATIRICAL, ContentType.REFLECTIVE]
        
        # 70% time-based preference, 30% rotation for variety
        if random.random() < 0.7:
            content_type = random.choice(preferred_types)
        else:
            content_type = self.content_types[self.current_content_index]
            self.current_content_index = (self.current_content_index + 1) % len(self.content_types)
        
        return content_type
    
    async def _final_content_validation(self, content: str, metadata) -> Dict[str, Any]:
        """Final validation before posting"""
        validation_result = {'approved': True, 'reason': ''}
        
        # Check if fact-check result exists and meets threshold
        if metadata.fact_check_result:
            fact_check_confidence = metadata.fact_check_result.get('confidence', 0.0)
            if fact_check_confidence < self.config.fact_check.confidence_threshold:
                validation_result['approved'] = False
                validation_result['reason'] = f"Fact-check confidence too low: {fact_check_confidence}"
                self.metrics['fact_check_failures'] += 1
                return validation_result
            else:
                self.metrics['fact_check_passes'] += 1
        
        # Check quality score
        if metadata.quality_score < 0.6:  # Minimum quality threshold
            validation_result['approved'] = False
            validation_result['reason'] = f"Quality score too low: {metadata.quality_score}"
            return validation_result
        
        # Check character count
        if len(content) > 280:
            validation_result['approved'] = False
            validation_result['reason'] = f"Content too long: {len(content)} characters"
            return validation_result
        
        # Additional security scan
        is_safe, threats = security_manager.scan_content_security(content)
        if not is_safe:
            validation_result['approved'] = False
            validation_result['reason'] = f"Security threats detected: {threats}"
            self.metrics['security_blocks'] += 1
            return validation_result
        
        return validation_result
    
    async def _log_successful_post(self, content: str, metadata, post_id: str):
        """Log successful post for audit and analysis"""
        audit_entry = {
            'post_id': post_id,
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'metadata': metadata.to_dict(),
            'validation_passed': True,
            'daily_count': self.metrics['posts_today'],
            'total_count': self.metrics['total_posts']
        }
        
        # Write to audit log
        with open(f'logs/audit/successful_posts_{datetime.now().strftime("%Y%m")}.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
    
    async def health_check(self):
        """Comprehensive health check of all systems"""
        self.logger.info("🔍 Performing health check")
        
        health_issues = []
        
        # Check each component
        for component, status in self.health_status['components'].items():
            if status != 'healthy':
                health_issues.append(f"{component}: {status}")
        
        # Check last successful post timing
        if self.health_status['last_successful_post']:
            time_since_last_post = datetime.now() - self.health_status['last_successful_post']
            if time_since_last_post > timedelta(hours=2):  # Alert if no post in 2 hours (for 50/day = ~30min intervals)
                health_issues.append(f"No successful post in {time_since_last_post}")
        
        # Check error rates
        if self.metrics['total_posts'] > 0:
            error_rate = self.metrics['failed_posts'] / self.metrics['total_posts']
            if error_rate > 0.3:  # More than 30% failure rate
                health_issues.append(f"High error rate: {error_rate:.2%}")
        
        # Check daily progress
        expected_posts_by_now = self._calculate_expected_posts()
        if self.metrics['posts_today'] < expected_posts_by_now * 0.8:  # Less than 80% of expected
            health_issues.append(f"Behind schedule: {self.metrics['posts_today']}/{expected_posts_by_now} expected")
        
        # Update health status
        self.health_status['last_health_check'] = datetime.now()
        self.health_status['status'] = 'healthy' if not health_issues else 'warning'
        
        if health_issues:
            self.logger.warning("⚠️ Health check found issues", issues=health_issues)
        else:
            self.logger.info("✅ Health check passed", 
                           daily_progress=self.health_status['daily_progress'])
    
    def _calculate_expected_posts(self) -> int:
        """Calculate expected posts by current time of day"""
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        
        # Active hours: 6:00 (360 min) to 23:30 (1410 min) = 1050 minutes
        active_start = 6 * 60  # 6:00 AM
        active_end = 23 * 60 + 30  # 11:30 PM
        
        if current_minutes < active_start:
            return 0
        elif current_minutes > active_end:
            return self.config.scheduler.daily_tweet_quota
        else:
            # Calculate proportional expected posts
            active_minutes_elapsed = current_minutes - active_start
            total_active_minutes = active_end - active_start
            expected = int((active_minutes_elapsed / total_active_minutes) * self.config.scheduler.daily_tweet_quota)
            return expected
    
    async def _health_monitor(self):
        """Continuous health monitoring"""
        while not self.emergency_shutdown:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                await self.health_check()
            except Exception as e:
                self.logger.error("Health monitor error", error=str(e))
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _metrics_collector(self):
        """Collect and report metrics"""
        while not self.emergency_shutdown:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Calculate uptime
                uptime = datetime.now() - self.metrics['start_time']
                
                # Log metrics
                self.logger.info("📊 Hourly metrics report",
                               uptime_hours=uptime.total_seconds() / 3600,
                               total_posts=self.metrics['total_posts'],
                               posts_today=self.metrics['posts_today'],
                               daily_quota=self.config.scheduler.daily_tweet_quota,
                               success_rate=self.metrics['successful_posts'] / max(1, self.metrics['total_posts']),
                               fact_check_passes=self.metrics['fact_check_passes'],
                               security_blocks=self.metrics['security_blocks'])
                
            except Exception as e:
                self.logger.error("Metrics collector error", error=str(e))
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def generate_daily_report(self):
        """Generate comprehensive daily report"""
        self.logger.info("📋 Generating daily report")
        
        # Collect performance data
        performance_data = enhanced_content_generator.get_performance_report()
        security_data = security_manager.get_security_status()
        
        daily_report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'metrics': self.metrics,
            'health_status': self.health_status,
            'performance': performance_data,
            'security': security_data,
            'uptime': (datetime.now() - self.metrics['start_time']).total_seconds() / 3600,
            'quota_achievement': f"{self.metrics['posts_today']}/{self.config.scheduler.daily_tweet_quota}",
            'quota_percentage': (self.metrics['posts_today'] / self.config.scheduler.daily_tweet_quota) * 100
        }
        
        # Save report
        report_file = f"logs/daily_reports/report_{datetime.now().strftime('%Y%m%d')}.json"
        os.makedirs('logs/daily_reports', exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(daily_report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info("📋 Daily report generated", 
                        report_file=report_file,
                        quota_achievement=daily_report['quota_achievement'])
    
    async def manual_post(self, topic: str, content_type: ContentType = ContentType.SATIRICAL) -> bool:
        """Manually trigger a post with specific topic"""
        self.logger.info("👤 Manual post triggered", topic=topic, content_type=content_type.value)
        return await self.generate_and_post_content(manual_topic=topic, content_type=content_type)
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🛑 Initiating graceful shutdown")
        
        # Stop scheduler
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        
        # Generate final report
        await self.generate_daily_report()
        
        self.logger.info("✅ Graceful shutdown completed")
    
    async def run(self):
        """Main run loop"""
        try:
            await self.initialize()
            
            self.logger.info("🎯 Enhanced Ethical Bot System is now running (50 tweets/day)")
            self.logger.info("📊 Daily quota: 50 tweets distributed across 6:00-23:30")
            self.logger.info("⏱️ Average interval: ~21 minutes between tweets")
            
            # Keep running until shutdown signal
            while not self.emergency_shutdown:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error("Fatal error in main loop", error=str(e), exc_info=True)
        finally:
            await self.shutdown()

# Main execution
async def main():
    """Main entry point"""
    bot = EnhancedBotOrchestrator()
    await bot.run()

if __name__ == "__main__":
    # Set up environment
    os.makedirs('logs', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    os.makedirs('security', exist_ok=True)
    
    # Run the bot
    asyncio.run(main())