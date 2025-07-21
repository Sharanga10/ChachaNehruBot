#!/usr/bin/env python3
"""
Zero-Cost Experimental Bot
Personal project for learning and experimentation
Uses only free services + your existing ChatGPT/Grok APIs
"""

import asyncio
import logging
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import random
import time

# Import your existing cost-controlled modules
from grok_tracker import should_use_grok, track_tokens, get_token_usage
from config.zero_cost_config import zero_cost_manager

# Basic imports for free services
import openai
import requests
from pathlib import Path

class ZeroCostBot:
    """
    Zero-cost experimental bot for personal learning
    - Uses only your existing APIs with cost controls
    - Local storage (no cloud costs)
    - Free-tier services only
    - 10 tweets/day (instead of 50) to save costs
    """
    
    def __init__(self):
        self.config = zero_cost_manager
        self.setup_logging()
        self.setup_local_database()
        self.setup_local_cache()
        
        # Performance tracking
        self.metrics = {
            'total_posts': 0,
            'successful_posts': 0,
            'failed_posts': 0,
            'posts_today': 0,
            'last_reset_date': datetime.now().date(),
            'start_time': datetime.now()
        }
        
        # Load your existing API keys
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.grok_key = os.getenv('XAI_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')  # Free tier
        
        if self.openai_key:
            openai.api_key = self.openai_key
        
        self.logger.info("🆓 Zero-cost experimental bot initialized")
    
    def setup_logging(self):
        """Setup local logging (free)"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("📝 Local logging initialized")
    
    def setup_local_database(self):
        """Setup SQLite database (free)"""
        db_path = self.config.local_infra.database_file
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_conn = sqlite3.connect(db_path)
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                language TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN NOT NULL,
                model_used TEXT,
                character_count INTEGER
            )
        ''')
        self.db_conn.commit()
        self.logger.info("🗄️ Local SQLite database initialized")
    
    def setup_local_cache(self):
        """Setup local file cache (free)"""
        cache_path = Path(self.config.local_infra.cache_file)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}
        
        self.logger.info("💾 Local file cache initialized")
    
    def save_cache(self):
        """Save cache to local file"""
        cache_path = Path(self.config.local_infra.cache_file)
        with open(cache_path, 'w') as f:
            json.dump(self.cache, f, indent=2, default=str)
    
    async def generate_content_with_cost_control(self, topic: str = None, language: str = "hi") -> Optional[str]:
        """Generate content using your existing APIs with strict cost controls"""
        
        # Check cache first (free)
        cache_key = f"{topic}_{language}_{datetime.now().date()}"
        if cache_key in self.cache:
            self.logger.info("💾 Using cached content (free)")
            return self.cache[cache_key]
        
        content = None
        model_used = None
        
        # Try Grok first (with your ₹250 budget control)
        if should_use_grok() and self.grok_key:
            self.logger.info("🤖 Trying Grok API (within ₹250 budget)")
            content = await self._generate_with_grok(topic, language)
            if content:
                model_used = "grok"
        
        # Fallback to ChatGPT (your existing API)
        if not content and self.openai_key:
            self.logger.info("🤖 Trying ChatGPT API (your existing)")
            content = await self._generate_with_chatgpt(topic, language)
            if content:
                model_used = "chatgpt"
        
        # Cache successful result (free)
        if content:
            self.cache[cache_key] = content
            self.save_cache()
            
            # Keep cache size manageable
            if len(self.cache) > self.config.local_infra.cache_max_size:
                # Remove oldest entries
                oldest_keys = list(self.cache.keys())[:100]
                for key in oldest_keys:
                    del self.cache[key]
                self.save_cache()
        
        return content
    
    async def _generate_with_grok(self, topic: str, language: str) -> Optional[str]:
        """Generate with Grok using your cost controls"""
        try:
            # Simple topic if none provided
            if not topic:
                topics = {
                    "hi": ["शिक्षा", "प्रेरणा", "जीवन", "सफलता", "खुशी"],
                    "en": ["education", "motivation", "life", "success", "happiness"]
                }
                topic = random.choice(topics.get(language, topics["en"]))
            
            # Create simple prompt
            if language == "hi":
                prompt = f"कृपया '{topic}' के बारे में एक प्रेरणादायक ट्वीट लिखें। 280 अक्षरों के भीतर रखें।"
            else:
                prompt = f"Please write an inspiring tweet about '{topic}'. Keep within 280 characters."
            
            # Make API call (this will be tracked by your grok_tracker.py)
            headers = {
                'Authorization': f'Bearer {self.grok_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messages': [{'role': 'user', 'content': prompt}],
                'model': 'grok-beta',
                'max_tokens': 100  # Keep low to save costs
            }
            
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Track tokens for cost control
                track_tokens(len(prompt) // 4, len(content) // 4)  # Rough estimate
                
                return content[:280]  # Ensure Twitter limit
            
        except Exception as e:
            self.logger.warning(f"Grok API failed: {e}")
        
        return None
    
    async def _generate_with_chatgpt(self, topic: str, language: str) -> Optional[str]:
        """Generate with ChatGPT using your existing API"""
        try:
            if not topic:
                topics = {
                    "hi": ["शिक्षा", "प्रेरणा", "जीवन", "सफलता", "खुशी"],
                    "en": ["education", "motivation", "life", "success", "happiness"]
                }
                topic = random.choice(topics.get(language, topics["en"]))
            
            if language == "hi":
                prompt = f"कृपया '{topic}' के बारे में एक सकारात्मक ट्वीट लिखें। 280 अक्षरों के भीतर रखें।"
            else:
                prompt = f"Please write a positive tweet about '{topic}'. Keep within 280 characters."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Cheaper than GPT-4
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,  # Keep low to save costs
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            return content[:280]  # Ensure Twitter limit
            
        except Exception as e:
            self.logger.warning(f"ChatGPT API failed: {e}")
        
        return None
    
    def basic_content_filter(self, content: str) -> bool:
        """Basic free content filtering"""
        if not content or len(content) < 10:
            return False
        
        # Basic banned words (free)
        banned_words = ['hate', 'violence', 'discrimination', 'offensive']
        content_lower = content.lower()
        
        for word in banned_words:
            if word in content_lower:
                return False
        
        return True
    
    def simple_fact_check(self, content: str) -> bool:
        """Simple fact-checking (free)"""
        # Very basic checks - avoid specific claims
        suspicious_patterns = [
            'statistics show', 'research proves', 'studies confirm',
            'scientists say', '% of people', 'according to data'
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                self.logger.warning(f"Content contains suspicious claim: {pattern}")
                return False
        
        return True
    
    async def post_to_twitter_simulation(self, content: str) -> bool:
        """Simulate Twitter posting (for experimentation)"""
        # For experimentation, we'll just log the tweet instead of actually posting
        # This saves costs and allows you to test the system
        
        self.logger.info("📤 SIMULATED TWITTER POST:")
        self.logger.info(f"Content: {content}")
        self.logger.info(f"Length: {len(content)} characters")
        self.logger.info("✅ Simulated post successful")
        
        # You can enable actual posting by implementing real Twitter API calls
        # when you're ready to test with real posts
        
        return True
    
    def save_post_to_database(self, content: str, language: str, success: bool, model_used: str):
        """Save post to local database"""
        self.db_conn.execute('''
            INSERT INTO posts (content, language, success, model_used, character_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (content, language, success, model_used, len(content)))
        self.db_conn.commit()
    
    async def generate_and_post(self):
        """Main content generation and posting pipeline"""
        try:
            # Reset daily counter if needed
            current_date = datetime.now().date()
            if current_date > self.metrics['last_reset_date']:
                self.metrics['posts_today'] = 0
                self.metrics['last_reset_date'] = current_date
                self.logger.info("🔄 Daily counter reset")
            
            # Check daily quota (reduced to save costs)
            if self.metrics['posts_today'] >= self.config.get_daily_tweet_quota():
                self.logger.info(f"📊 Daily quota reached: {self.metrics['posts_today']}/10")
                return False
            
            # Get language for this tweet
            language = self.config.get_language_for_tweet(self.metrics['posts_today'])
            
            self.logger.info(f"🎯 Generating tweet #{self.metrics['posts_today'] + 1}/10 in {language}")
            
            # Generate content with cost controls
            content = await self.generate_content_with_cost_control(language=language)
            
            if not content:
                self.logger.error("❌ Content generation failed")
                self.metrics['failed_posts'] += 1
                return False
            
            # Basic validation (free)
            if not self.basic_content_filter(content):
                self.logger.warning("❌ Content failed basic filter")
                self.metrics['failed_posts'] += 1
                return False
            
            if not self.simple_fact_check(content):
                self.logger.warning("❌ Content failed basic fact-check")
                self.metrics['failed_posts'] += 1
                return False
            
            # Simulate posting (for experimentation)
            success = await self.post_to_twitter_simulation(content)
            
            # Update metrics
            if success:
                self.metrics['successful_posts'] += 1
                self.metrics['posts_today'] += 1
                self.logger.info(f"✅ Tweet posted successfully ({self.metrics['posts_today']}/10 today)")
            else:
                self.metrics['failed_posts'] += 1
            
            self.metrics['total_posts'] += 1
            
            # Save to database
            self.save_post_to_database(content, language, success, "grok_or_chatgpt")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Generate and post failed: {e}")
            self.metrics['failed_posts'] += 1
            return False
    
    def show_status(self):
        """Show current bot status"""
        grok_usage = get_token_usage()
        
        print("\n🆓 ZERO-COST BOT STATUS")
        print("=" * 40)
        print(f"📊 Posts today: {self.metrics['posts_today']}/10")
        print(f"✅ Successful posts: {self.metrics['successful_posts']}")
        print(f"❌ Failed posts: {self.metrics['failed_posts']}")
        print(f"💰 Grok cost estimate: ₹{grok_usage['estimated_inr']:.2f}/₹250")
        print(f"🕒 Running since: {self.metrics['start_time'].strftime('%Y-%m-%d %H:%M')}")
        
        # Show recent posts from database
        cursor = self.db_conn.execute('''
            SELECT content, language, timestamp FROM posts 
            WHERE success = 1 
            ORDER BY timestamp DESC 
            LIMIT 3
        ''')
        
        print("\n📝 Recent posts:")
        for row in cursor.fetchall():
            content, lang, timestamp = row
            print(f"   {timestamp} [{lang}]: {content[:50]}...")
    
    async def run_experimental_mode(self):
        """Run in experimental mode - generate a few posts for testing"""
        print("\n🧪 EXPERIMENTAL MODE - GENERATING TEST POSTS")
        print("=" * 50)
        
        for i in range(5):  # Generate 5 test posts
            print(f"\n🎯 Generating test post {i+1}/5...")
            success = await self.generate_and_post()
            
            if success:
                print("✅ Post generated successfully")
            else:
                print("❌ Post generation failed")
            
            # Small delay between posts
            await asyncio.sleep(2)
        
        print("\n📊 Experimental session complete!")
        self.show_status()
    
    async def run_scheduled_mode(self):
        """Run in scheduled mode - post every 2.4 hours"""
        print("\n⏰ SCHEDULED MODE - 10 POSTS PER DAY")
        print("=" * 40)
        
        interval_seconds = int(2.4 * 3600)  # 2.4 hours in seconds
        
        while True:
            try:
                await self.generate_and_post()
                self.show_status()
                
                print(f"\n😴 Sleeping for {2.4} hours until next post...")
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n👋 Scheduled mode stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Scheduled mode error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

async def main():
    """Main entry point"""
    print("🆓 ZERO-COST EXPERIMENTAL TWITTER BOT")
    print("🎯 Personal project for learning and experimentation")
    print("=" * 60)
    
    # Show cost report
    print(zero_cost_manager.get_cost_report())
    
    # Initialize bot
    bot = ZeroCostBot()
    
    print("\n🎮 SELECT MODE:")
    print("1. 🧪 Experimental Mode (generate 5 test posts)")
    print("2. ⏰ Scheduled Mode (10 posts/day, every 2.4 hours)")
    print("3. 📊 Show Status Only")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            await bot.run_experimental_mode()
        elif choice == "2":
            await bot.run_scheduled_mode()
        elif choice == "3":
            bot.show_status()
        else:
            print("Invalid choice. Exiting.")
    
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        if hasattr(bot, 'db_conn'):
            bot.db_conn.close()

if __name__ == "__main__":
    asyncio.run(main())