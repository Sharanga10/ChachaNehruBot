"""
Enhanced Main Application - World's Most Ethical AI Bot
Zero-downtime, fact-checked, secure automated social media bot
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import signal
import json

# Enhanced imports
from config.main_config import config_manager
from core.enhanced_content_generator import enhanced_content_generator, ContentType
from core.fact_checker import fact_checker, FactCheckStatus
from core.security_manager import security_manager
from post_to_twitter import post_to_twitter

# Monitoring and scheduling
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

class EnhancedBotOrchestrator:
    """
    World-class bot orchestrator with:
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
            'start_time': datetime.now()
        }
        
        # Circuit breaker for emergency shutdown
        self.emergency_shutdown = False
        
        # Health check status
        self.health_status = {
            'status': 'starting',
            'last_successful_post': None,
            'last_health_check': datetime.now(),
            'components': {
                'content_generator': 'unknown',
                'fact_checker': 'unknown',
                'security_manager': 'unknown',
                'twitter_api': 'unknown'
            }
        }
    
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
        self.logger.info("🚀 Initializing Enhanced Ethical Bot System")
        
        try:
            # Validate configuration
            if not self.config.validate_configuration():
                raise RuntimeError("Configuration validation failed")
            
            # Initialize components
            await self._initialize_components()
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Setup scheduled tasks
            self._setup_scheduler()
            
            # Start health monitoring
            asyncio.create_task(self._health_monitor())
            
            # Start metrics collection
            asyncio.create_task(self._metrics_collector())
            
            self.health_status['status'] = 'running'
            self.logger.info("✅ Bot system initialized successfully")
            
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
    
    def _setup_scheduler(self):
        """Setup automated posting schedule"""
        # Regular posting schedule - customize based on your needs
        self.scheduler.add_job(
            self.generate_and_post_content,
            CronTrigger(hour="8,12,16,20", minute=0),  # 4 times a day
            id="regular_posting",
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
        
        # Daily metrics report
        self.scheduler.add_job(
            self.generate_daily_report,
            CronTrigger(hour=0, minute=0),  # Daily at midnight
            id="daily_report",
            max_instances=1
        )
        
        # Start scheduler
        self.scheduler.start()
        self.logger.info("📅 Scheduler initialized with automated tasks")
    
    async def generate_and_post_content(self, manual_topic: str = None, 
                                      content_type: ContentType = ContentType.SATIRICAL):
        """
        Main content generation and posting pipeline with full validation
        """
        post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger.info("🎯 Starting content generation pipeline", post_id=post_id)
        
        try:
            # Check if we're in emergency shutdown
            if self.emergency_shutdown:
                self.logger.warning("Emergency shutdown active, skipping post generation")
                return False
            
            # Rate limiting check
            if not security_manager.check_rate_limit("daily_posts", self.config.security.max_daily_posts, 86400):
                self.logger.warning("Daily post limit exceeded")
                self.metrics['failed_posts'] += 1
                return False
            
            # Determine current mode
            current_hour = datetime.now().hour
            mode = "NIGHT" if current_hour < 6 or current_hour > 22 else "DAY"
            
            # Select content type based on time if not specified
            if not manual_topic:
                if current_hour in [8, 12]:  # Morning and noon - informative
                    content_type = ContentType.INFORMATIVE
                elif current_hour in [16]:  # Evening - cultural/reflective
                    content_type = ContentType.CULTURAL
                else:  # Night - satirical/reflective
                    content_type = ContentType.SATIRICAL
            
            # Generate ethical content
            self.logger.info("🤖 Generating ethical content", content_type=content_type.value, mode=mode)
            content, metadata = await enhanced_content_generator.generate_ethical_content(
                topic=manual_topic,
                content_type=content_type,
                language="hi",  # Primary language
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
                self.health_status['last_successful_post'] = datetime.now()
                
                # Log successful post for audit
                await self._log_successful_post(content, metadata, post_id)
                
                self.logger.info("✅ Content posted successfully", 
                               post_id=post_id,
                               model_used=metadata.model_used,
                               quality_score=metadata.quality_score)
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
            'validation_passed': True
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
            if time_since_last_post > timedelta(hours=8):  # Alert if no post in 8 hours
                health_issues.append(f"No successful post in {time_since_last_post}")
        
        # Check error rates
        if self.metrics['total_posts'] > 0:
            error_rate = self.metrics['failed_posts'] / self.metrics['total_posts']
            if error_rate > 0.3:  # More than 30% failure rate
                health_issues.append(f"High error rate: {error_rate:.2%}")
        
        # Update health status
        self.health_status['last_health_check'] = datetime.now()
        self.health_status['status'] = 'healthy' if not health_issues else 'warning'
        
        if health_issues:
            self.logger.warning("⚠️ Health check found issues", issues=health_issues)
        else:
            self.logger.info("✅ Health check passed")
    
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
            'uptime': (datetime.now() - self.metrics['start_time']).total_seconds() / 3600
        }
        
        # Save report
        report_file = f"logs/daily_reports/report_{datetime.now().strftime('%Y%m%d')}.json"
        os.makedirs('logs/daily_reports', exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(daily_report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info("📋 Daily report generated", report_file=report_file)
    
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
            
            self.logger.info("🎯 Enhanced Ethical Bot System is now running")
            self.logger.info("📊 Monitoring dashboard: http://localhost:8080/health")  # If you implement web dashboard
            
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