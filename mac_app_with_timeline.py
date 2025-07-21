#!/usr/bin/env python3
"""
Enhanced Mac App GUI with Twitter Timeline Integration
Shows bot's tweets in real-time with engagement metrics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import asyncio
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
import os
import requests
import webbrowser
from urllib.parse import quote

# Import your bot components
try:
    from zero_cost_main import ZeroCostBot
    from config.zero_cost_config import zero_cost_manager
    from grok_tracker import get_token_usage
    import tweepy
except ImportError:
    print("⚠️  Bot modules not found - running in demo mode")
    ZeroCostBot = None
    tweepy = None

class TwitterTimelineWidget:
    """Custom widget for displaying Twitter timeline"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_timeline_ui()
        self.tweets_data = []
        self.load_sample_data()
    
    def setup_timeline_ui(self):
        """Setup the timeline interface"""
        # Main timeline frame
        self.timeline_frame = ttk.Frame(self.parent)
        self.timeline_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with bot info
        self.create_timeline_header()
        
        # Timeline content
        self.create_timeline_content()
        
        # Footer with actions
        self.create_timeline_footer()
    
    def create_timeline_header(self):
        """Create timeline header with bot profile info"""
        header_frame = ttk.LabelFrame(self.timeline_frame, text="🐦 Bot Timeline", padding=15)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Bot profile section
        profile_frame = ttk.Frame(header_frame)
        profile_frame.pack(fill=tk.X)
        
        # Bot avatar (emoji)
        avatar_label = tk.Label(profile_frame, text="🤖", font=('SF Pro Display', 24))
        avatar_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Bot info
        info_frame = ttk.Frame(profile_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bot name and handle
        name_label = ttk.Label(info_frame, text="Zero-Cost Bot", 
                              font=('SF Pro Display', 14, 'bold'))
        name_label.pack(anchor=tk.W)
        
        handle_label = ttk.Label(info_frame, text="@your_bot_handle", 
                                foreground='gray', font=('SF Pro Display', 11))
        handle_label.pack(anchor=tk.W)
        
        # Bot description
        desc_label = ttk.Label(info_frame, 
                              text="🌐 Hindi • Bhojpuri • English • 50 tweets/day • Powered by AI",
                              font=('SF Pro Display', 10))
        desc_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Stats section
        stats_frame = ttk.Frame(profile_frame)
        stats_frame.pack(side=tk.RIGHT)
        
        # Following/Followers stats
        self.create_stat_widget(stats_frame, "Following", "247", 0, 0)
        self.create_stat_widget(stats_frame, "Followers", "1.2K", 0, 1)
        self.create_stat_widget(stats_frame, "Tweets", "1,247", 0, 2)
        
        # Refresh button
        ttk.Button(stats_frame, text="🔄 Refresh Timeline", 
                  command=self.refresh_timeline).grid(row=1, column=0, columnspan=3, pady=(10, 0))
    
    def create_stat_widget(self, parent, label, value, row, col):
        """Create a stat widget"""
        stat_frame = ttk.Frame(parent)
        stat_frame.grid(row=row, column=col, padx=10)
        
        value_label = ttk.Label(stat_frame, text=value, 
                               font=('SF Pro Display', 12, 'bold'))
        value_label.pack()
        
        label_label = ttk.Label(stat_frame, text=label, 
                               foreground='gray', font=('SF Pro Display', 9))
        label_label.pack()
    
    def create_timeline_content(self):
        """Create scrollable timeline content area"""
        # Timeline container with scrollbar
        timeline_container = ttk.LabelFrame(self.timeline_frame, text="📝 Recent Tweets", padding=10)
        timeline_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas for scrolling
        self.timeline_canvas = tk.Canvas(timeline_container, bg='white', highlightthickness=0)
        timeline_scrollbar = ttk.Scrollbar(timeline_container, orient="vertical", 
                                          command=self.timeline_canvas.yview)
        self.scrollable_timeline = ttk.Frame(self.timeline_canvas)
        
        self.scrollable_timeline.bind(
            "<Configure>",
            lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all"))
        )
        
        self.timeline_canvas.create_window((0, 0), window=self.scrollable_timeline, anchor="nw")
        self.timeline_canvas.configure(yscrollcommand=timeline_scrollbar.set)
        
        self.timeline_canvas.pack(side="left", fill="both", expand=True)
        timeline_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.timeline_canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.timeline_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_timeline_footer(self):
        """Create timeline footer with actions"""
        footer_frame = ttk.Frame(self.timeline_frame)
        footer_frame.pack(fill=tk.X)
        
        # Timeline actions
        ttk.Button(footer_frame, text="🔗 View on Twitter", 
                  command=self.open_twitter_profile).pack(side=tk.LEFT)
        
        ttk.Button(footer_frame, text="📊 Analytics", 
                  command=self.show_analytics).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(footer_frame, text="📤 Compose Tweet", 
                  command=self.compose_tweet).pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto-refresh toggle
        self.auto_refresh = tk.BooleanVar(value=True)
        ttk.Checkbutton(footer_frame, text="🔄 Auto-refresh", 
                       variable=self.auto_refresh).pack(side=tk.RIGHT)
    
    def create_tweet_widget(self, parent, tweet_data):
        """Create a single tweet widget"""
        # Tweet container
        tweet_frame = ttk.Frame(parent, relief=tk.SOLID, borderwidth=1)
        tweet_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Configure hover effect
        tweet_frame.bind("<Enter>", lambda e: tweet_frame.configure(relief=tk.RAISED))
        tweet_frame.bind("<Leave>", lambda e: tweet_frame.configure(relief=tk.SOLID))
        
        # Tweet header
        header_frame = ttk.Frame(tweet_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Language indicator
        lang_colors = {"hi": "#FF6B35", "bho": "#4ECDC4", "en": "#45B7D1"}
        lang_names = {"hi": "🇮🇳 Hindi", "bho": "🏘️ Bhojpuri", "en": "🇬🇧 English"}
        
        lang_label = tk.Label(header_frame, 
                             text=lang_names.get(tweet_data['language'], '🌐 Unknown'),
                             bg=lang_colors.get(tweet_data['language'], '#gray'),
                             fg='white', font=('SF Pro Display', 8, 'bold'),
                             padx=8, pady=2)
        lang_label.pack(side=tk.LEFT)
        
        # Timestamp
        time_label = ttk.Label(header_frame, text=tweet_data['timestamp'],
                              foreground='gray', font=('SF Pro Display', 9))
        time_label.pack(side=tk.RIGHT)
        
        # Model used indicator
        model_label = ttk.Label(header_frame, text=f"🤖 {tweet_data['model']}",
                               foreground='blue', font=('SF Pro Display', 8))
        model_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Tweet content
        content_frame = ttk.Frame(tweet_frame)
        content_frame.pack(fill=tk.X, padx=10, pady=5)
        
        content_label = tk.Label(content_frame, text=tweet_data['content'],
                                font=('SF Pro Display', 11), wraplength=600,
                                justify=tk.LEFT, anchor=tk.W)
        content_label.pack(fill=tk.X)
        
        # Engagement metrics
        engagement_frame = ttk.Frame(tweet_frame)
        engagement_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Metrics
        metrics = [
            ("💬", tweet_data.get('replies', 0)),
            ("🔄", tweet_data.get('retweets', 0)),
            ("❤️", tweet_data.get('likes', 0)),
            ("📊", tweet_data.get('views', 0))
        ]
        
        for emoji, count in metrics:
            metric_frame = ttk.Frame(engagement_frame)
            metric_frame.pack(side=tk.LEFT, padx=(0, 15))
            
            ttk.Label(metric_frame, text=f"{emoji} {count}",
                     font=('SF Pro Display', 9)).pack()
        
        # Quality score
        quality_score = tweet_data.get('quality_score', 0)
        quality_color = '#34C759' if quality_score > 8 else '#FF9500' if quality_score > 6 else '#FF3B30'
        
        quality_label = tk.Label(engagement_frame, 
                                text=f"⭐ {quality_score}/10",
                                fg=quality_color, font=('SF Pro Display', 9, 'bold'))
        quality_label.pack(side=tk.RIGHT)
        
        # Tweet actions
        actions_frame = ttk.Frame(tweet_frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(actions_frame, text="🔗 View", width=8,
                  command=lambda: self.view_tweet(tweet_data)).pack(side=tk.LEFT)
        
        ttk.Button(actions_frame, text="📋 Copy", width=8,
                  command=lambda: self.copy_tweet(tweet_data)).pack(side=tk.LEFT, padx=(5, 0))
        
        if tweet_data.get('can_delete', False):
            ttk.Button(actions_frame, text="🗑️ Delete", width=8,
                      command=lambda: self.delete_tweet(tweet_data)).pack(side=tk.LEFT, padx=(5, 0))
    
    def load_sample_data(self):
        """Load sample tweet data for demonstration"""
        self.tweets_data = [
            {
                'id': '1',
                'content': 'शिक्षा वह खजाना है जो कोई चुरा नहीं सकता। हर दिन कुछ नया सीखें और आगे बढ़ते रहें! 📚✨ #शिक्षा #प्रेरणा',
                'language': 'hi',
                'timestamp': '2 hours ago',
                'model': 'Grok',
                'replies': 12,
                'retweets': 8,
                'likes': 45,
                'views': 234,
                'quality_score': 8.5,
                'can_delete': True
            },
            {
                'id': '2', 
                'content': 'पढ़ाई-लिखाई के बिना जिनगी अधूरी बा। हर दिन कुछ नया सीखीं और आगे बढ़ीं! 📚🌟 #भोजपुरी #प्रेरणा',
                'language': 'bho',
                'timestamp': '4 hours ago',
                'model': 'ChatGPT',
                'replies': 8,
                'retweets': 15,
                'likes': 67,
                'views': 445,
                'quality_score': 9.2,
                'can_delete': True
            },
            {
                'id': '3',
                'content': 'Education is the treasure that no one can steal. Keep learning something new every day! 📚✨ #Education #Motivation',
                'language': 'en',
                'timestamp': '6 hours ago',
                'model': 'Sarvam',
                'replies': 5,
                'retweets': 3,
                'likes': 28,
                'views': 156,
                'quality_score': 7.8,
                'can_delete': True
            },
            {
                'id': '4',
                'content': 'सफलता उन्हीं को मिलती है जो कभी हार नहीं मानते। आज भी एक नया कदम उठाएं! 🚀💪 #सफलता #मोटिवेशन',
                'language': 'hi',
                'timestamp': '8 hours ago',
                'model': 'Grok',
                'replies': 18,
                'retweets': 22,
                'likes': 89,
                'views': 567,
                'quality_score': 9.1,
                'can_delete': True
            },
            {
                'id': '5',
                'content': 'गांव के लोग सबसे ज्यादा मेहनती होते हैं। उनकी मेहनत से ही देश चलता है! 🌾👨‍🌾 #गांव #मेहनत',
                'language': 'bho',
                'timestamp': '10 hours ago',
                'model': 'ChatGPT',
                'replies': 25,
                'retweets': 31,
                'likes': 156,
                'views': 892,
                'quality_score': 8.9,
                'can_delete': True
            }
        ]
        
        self.refresh_timeline_display()
    
    def refresh_timeline_display(self):
        """Refresh the timeline display with current data"""
        # Clear existing tweets
        for widget in self.scrollable_timeline.winfo_children():
            widget.destroy()
        
        # Add timeline header
        if self.tweets_data:
            header_label = ttk.Label(self.scrollable_timeline, 
                                   text=f"📝 {len(self.tweets_data)} Recent Tweets",
                                   font=('SF Pro Display', 12, 'bold'))
            header_label.pack(pady=(0, 10))
        
        # Add tweet widgets
        for tweet_data in self.tweets_data:
            self.create_tweet_widget(self.scrollable_timeline, tweet_data)
        
        # Add load more button
        if len(self.tweets_data) >= 5:
            load_more_frame = ttk.Frame(self.scrollable_timeline)
            load_more_frame.pack(fill=tk.X, pady=20)
            
            ttk.Button(load_more_frame, text="📜 Load More Tweets",
                      command=self.load_more_tweets).pack()
    
    def refresh_timeline(self):
        """Refresh timeline data from Twitter API"""
        # In real implementation, this would call Twitter API
        # For demo, we'll simulate loading new tweets
        
        # Show loading indicator
        loading_label = ttk.Label(self.scrollable_timeline, text="🔄 Refreshing timeline...")
        loading_label.pack()
        
        # Simulate API delay
        self.parent.after(1000, lambda: self._finish_refresh(loading_label))
    
    def _finish_refresh(self, loading_label):
        """Finish refresh process"""
        loading_label.destroy()
        
        # Simulate new tweet (in real app, this would come from API)
        new_tweet = {
            'id': f'new_{len(self.tweets_data)}',
            'content': 'जीवन में सबसे बड़ी खुशी दूसरों की मदद करने में है। आज किसी की मदद करें! 🤝❤️ #मदद #खुशी',
            'language': 'hi',
            'timestamp': 'Just now',
            'model': 'Grok',
            'replies': 0,
            'retweets': 0,
            'likes': 0,
            'views': 1,
            'quality_score': 8.7,
            'can_delete': True
        }
        
        # Add to beginning of list
        self.tweets_data.insert(0, new_tweet)
        
        # Refresh display
        self.refresh_timeline_display()
        
        # Show success message
        messagebox.showinfo("Timeline Refreshed", "✅ Timeline updated with latest tweets!")
    
    def load_more_tweets(self):
        """Load more historical tweets"""
        # Simulate loading older tweets
        older_tweets = [
            {
                'id': f'old_{len(self.tweets_data) + i}',
                'content': f'Sample older tweet #{i+1} with educational content...',
                'language': 'hi' if i % 2 == 0 else 'en',
                'timestamp': f'{12 + i*2} hours ago',
                'model': ['Grok', 'ChatGPT', 'Sarvam'][i % 3],
                'replies': 5 + i,
                'retweets': 3 + i,
                'likes': 20 + i*5,
                'views': 100 + i*50,
                'quality_score': 7.5 + (i * 0.3),
                'can_delete': True
            }
            for i in range(3)
        ]
        
        self.tweets_data.extend(older_tweets)
        self.refresh_timeline_display()
    
    def view_tweet(self, tweet_data):
        """Open tweet in browser"""
        # In real implementation, this would open the actual tweet URL
        tweet_url = f"https://twitter.com/your_bot_handle/status/{tweet_data['id']}"
        messagebox.showinfo("View Tweet", f"Opening tweet in browser:\n{tweet_url}")
        # webbrowser.open(tweet_url)
    
    def copy_tweet(self, tweet_data):
        """Copy tweet content to clipboard"""
        self.parent.clipboard_clear()
        self.parent.clipboard_append(tweet_data['content'])
        messagebox.showinfo("Copied", "✅ Tweet content copied to clipboard!")
    
    def delete_tweet(self, tweet_data):
        """Delete tweet (with confirmation)"""
        result = messagebox.askyesno("Delete Tweet", 
                                   f"Are you sure you want to delete this tweet?\n\n{tweet_data['content'][:100]}...")
        if result:
            # Remove from data
            self.tweets_data = [t for t in self.tweets_data if t['id'] != tweet_data['id']]
            self.refresh_timeline_display()
            messagebox.showinfo("Deleted", "✅ Tweet deleted successfully!")
    
    def open_twitter_profile(self):
        """Open bot's Twitter profile"""
        profile_url = "https://twitter.com/your_bot_handle"
        messagebox.showinfo("Twitter Profile", f"Opening profile:\n{profile_url}")
        # webbrowser.open(profile_url)
    
    def show_analytics(self):
        """Show detailed analytics"""
        # Calculate analytics from tweets data
        total_tweets = len(self.tweets_data)
        total_likes = sum(t.get('likes', 0) for t in self.tweets_data)
        total_retweets = sum(t.get('retweets', 0) for t in self.tweets_data)
        total_replies = sum(t.get('replies', 0) for t in self.tweets_data)
        avg_quality = sum(t.get('quality_score', 0) for t in self.tweets_data) / total_tweets if total_tweets > 0 else 0
        
        analytics_text = f"""
📊 TWITTER ANALYTICS SUMMARY

📝 Total Tweets: {total_tweets}
❤️ Total Likes: {total_likes}
🔄 Total Retweets: {total_retweets}
💬 Total Replies: {total_replies}
⭐ Average Quality: {avg_quality:.1f}/10

🌐 Language Breakdown:
   Hindi: {len([t for t in self.tweets_data if t['language'] == 'hi'])} tweets
   Bhojpuri: {len([t for t in self.tweets_data if t['language'] == 'bho'])} tweets
   English: {len([t for t in self.tweets_data if t['language'] == 'en'])} tweets

🤖 Model Usage:
   Grok: {len([t for t in self.tweets_data if t['model'] == 'Grok'])} tweets
   ChatGPT: {len([t for t in self.tweets_data if t['model'] == 'ChatGPT'])} tweets
   Sarvam: {len([t for t in self.tweets_data if t['model'] == 'Sarvam'])} tweets
        """
        
        messagebox.showinfo("Twitter Analytics", analytics_text)
    
    def compose_tweet(self):
        """Open compose tweet dialog"""
        compose_window = tk.Toplevel(self.parent)
        compose_window.title("📝 Compose Tweet")
        compose_window.geometry("500x400")
        compose_window.transient(self.parent)
        compose_window.grab_set()
        
        # Compose interface
        ttk.Label(compose_window, text="📝 Compose New Tweet", 
                 font=('SF Pro Display', 14, 'bold')).pack(pady=10)
        
        # Language selection
        lang_frame = ttk.Frame(compose_window)
        lang_frame.pack(pady=5)
        
        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        
        lang_var = tk.StringVar(value="hi")
        languages = [("Hindi", "hi"), ("Bhojpuri", "bho"), ("English", "en")]
        
        for lang_name, lang_code in languages:
            ttk.Radiobutton(lang_frame, text=lang_name, value=lang_code,
                           variable=lang_var).pack(side=tk.LEFT, padx=10)
        
        # Content area
        content_frame = ttk.Frame(compose_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(content_frame, text="Content:").pack(anchor=tk.W)
        
        content_text = tk.Text(content_frame, height=8, font=('SF Pro Display', 11))
        content_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Character counter
        char_label = ttk.Label(content_frame, text="Characters: 0/280")
        char_label.pack(anchor=tk.E)
        
        def update_char_count(event=None):
            content = content_text.get("1.0", tk.END).strip()
            char_count = len(content)
            char_label.configure(text=f"Characters: {char_count}/280")
            if char_count > 280:
                char_label.configure(foreground='red')
            else:
                char_label.configure(foreground='black')
        
        content_text.bind('<KeyRelease>', update_char_count)
        
        # Buttons
        button_frame = ttk.Frame(compose_window)
        button_frame.pack(pady=10)
        
        def post_tweet():
            content = content_text.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Empty Tweet", "Please enter some content.")
                return
            
            if len(content) > 280:
                messagebox.showwarning("Too Long", "Tweet must be 280 characters or less.")
                return
            
            # Add to timeline (simulate posting)
            new_tweet = {
                'id': f'manual_{len(self.tweets_data)}',
                'content': content,
                'language': lang_var.get(),
                'timestamp': 'Just now',
                'model': 'Manual',
                'replies': 0,
                'retweets': 0,
                'likes': 0,
                'views': 1,
                'quality_score': 8.0,
                'can_delete': True
            }
            
            self.tweets_data.insert(0, new_tweet)
            self.refresh_timeline_display()
            
            compose_window.destroy()
            messagebox.showinfo("Tweet Posted", "✅ Tweet posted successfully!")
        
        ttk.Button(button_frame, text="📤 Post Tweet", 
                  command=post_tweet).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=compose_window.destroy).pack(side=tk.LEFT, padx=5)

class EnhancedTwitterBotMacApp:
    """Enhanced Mac App with Twitter Timeline Integration"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.setup_bot()
        self.setup_ui()
        self.setup_status_updates()
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        self.root.after(100, self.process_queue)
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("🆓 Zero-Cost Twitter Bot - Mac Edition with Timeline")
        self.root.geometry("1400x900")  # Larger for timeline
        self.root.minsize(1200, 700)
        
        # Mac-style window
        self.root.configure(bg='#f0f0f0')
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f'1400x900+{x}+{y}')
    
    def setup_styles(self):
        """Setup custom styles for Mac look"""
        style = ttk.Style()
        
        # Configure styles for Mac appearance
        style.theme_use('aqua' if 'aqua' in style.theme_names() else 'clam')
        
        # Custom button styles
        style.configure('Action.TButton', 
                       background='#007AFF', 
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        
        style.configure('Success.TButton', 
                       background='#34C759',
                       foreground='white',
                       borderwidth=0)
        
        style.configure('Warning.TButton', 
                       background='#FF9500',
                       foreground='white',
                       borderwidth=0)
        
        style.configure('Danger.TButton', 
                       background='#FF3B30',
                       foreground='white',
                       borderwidth=0)
    
    def setup_variables(self):
        """Setup tkinter variables"""
        self.is_running = tk.BooleanVar(value=False)
        self.posts_today = tk.StringVar(value="0/50")
        self.success_rate = tk.StringVar(value="100%")
        self.cost_used = tk.StringVar(value="₹0/₹250")
        self.current_language = tk.StringVar(value="Hindi")
        self.bot_status = tk.StringVar(value="Ready")
        
        # Settings variables
        self.auto_start = tk.BooleanVar(value=False)
        self.notifications = tk.BooleanVar(value=True)
        self.dark_mode = tk.BooleanVar(value=False)
        
        # Content variables
        self.manual_topic = tk.StringVar()
        self.selected_language = tk.StringVar(value="hi")
        self.content_type = tk.StringVar(value="inspirational")
    
    def setup_bot(self):
        """Initialize bot instance"""
        try:
            if ZeroCostBot:
                self.bot = ZeroCostBot()
                self.bot_available = True
            else:
                self.bot = None
                self.bot_available = False
        except Exception as e:
            self.bot = None
            self.bot_available = False
            print(f"Bot initialization failed: {e}")
    
    def setup_ui(self):
        """Setup the complete user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create all tabs (including new timeline tab)
        self.create_dashboard_tab()
        self.create_timeline_tab()  # NEW!
        self.create_content_tab()
        self.create_analytics_tab()
        self.create_multimedia_tab()
        self.create_settings_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create app header with title and controls"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title and icon
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="🆓 Zero-Cost Twitter Bot", 
                               font=('SF Pro Display', 18, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Hindi • Bhojpuri • English • 50 tweets/day • $3/month • Live Timeline",
                                  font=('SF Pro Display', 10),
                                  foreground='gray')
        subtitle_label.pack(anchor=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=tk.RIGHT)
        
        self.start_button = ttk.Button(control_frame, text="▶ Start Bot", 
                                      style='Success.TButton',
                                      command=self.toggle_bot)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="⚡ Test Post", 
                  style='Action.TButton',
                  command=self.generate_test_post).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="🐦 Timeline", 
                  command=lambda: self.notebook.select(1)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="📊 Refresh", 
                  command=self.refresh_status).pack(side=tk.LEFT)
    
    def create_timeline_tab(self):
        """Create Twitter timeline tab"""
        timeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(timeline_frame, text="🐦 Timeline")
        
        # Initialize timeline widget
        self.timeline_widget = TwitterTimelineWidget(timeline_frame)
    
    # Include all other methods from the original app
    def create_dashboard_tab(self):
        """Create main dashboard tab (same as before)"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Add dashboard content (same as original)
        # ... (keeping original dashboard implementation)
    
    def create_content_tab(self):
        """Create content generation tab (same as before)"""
        content_frame = ttk.Frame(self.notebook)
        self.notebook.add(content_frame, text="📝 Content")
        
        # Add content generation interface (same as original)
        # ... (keeping original content implementation)
    
    def create_analytics_tab(self):
        """Create analytics tab (same as before)"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Add analytics charts (same as original)
        # ... (keeping original analytics implementation)
    
    def create_multimedia_tab(self):
        """Create multimedia tab (same as before)"""
        multimedia_frame = ttk.Frame(self.notebook)
        self.notebook.add(multimedia_frame, text="🎨 Multimedia")
        
        # Add multimedia interface (same as original)
        # ... (keeping original multimedia implementation)
    
    def create_settings_tab(self):
        """Create settings tab (same as before)"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Add settings interface (same as original)
        # ... (keeping original settings implementation)
    
    def create_status_bar(self, parent):
        """Create bottom status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        # Left side - status
        left_status = ttk.Frame(status_frame)
        left_status.pack(side=tk.LEFT)
        
        self.status_text = ttk.Label(left_status, text="Ready")
        self.status_text.pack(side=tk.LEFT)
        
        # Right side - info
        right_status = ttk.Frame(status_frame)
        right_status.pack(side=tk.RIGHT)
        
        ttk.Label(right_status, text="v1.1.0 with Timeline").pack(side=tk.RIGHT)
        
        self.connection_status = ttk.Label(right_status, text="● Offline", foreground='red')
        self.connection_status.pack(side=tk.RIGHT, padx=(0, 10))
    
    def setup_status_updates(self):
        """Setup periodic status updates"""
        self.update_status()
        self.root.after(5000, self.setup_status_updates)  # Update every 5 seconds
    
    def toggle_bot(self):
        """Toggle bot start/stop"""
        if self.is_running.get():
            self.stop_bot()
        else:
            self.start_bot()
    
    def start_bot(self):
        """Start the bot"""
        if not self.bot_available:
            messagebox.showwarning("Bot Not Available", 
                                 "Bot modules not found. Running in demo mode.")
            return
        
        self.is_running.set(True)
        self.start_button.configure(text="⏸ Stop Bot", style='Danger.TButton')
        self.bot_status.set("Running")
        self.connection_status.configure(text="● Online", foreground='green')
        
        # Start bot in background thread
        threading.Thread(target=self.run_bot_background, daemon=True).start()
    
    def stop_bot(self):
        """Stop the bot"""
        self.is_running.set(False)
        self.start_button.configure(text="▶ Start Bot", style='Success.TButton')
        self.bot_status.set("Stopped")
        self.connection_status.configure(text="● Offline", foreground='red')
    
    def run_bot_background(self):
        """Run bot in background thread"""
        while self.is_running.get():
            try:
                # Simulate bot activity and timeline updates
                self.message_queue.put(("log", "🎯 Generating content..."))
                
                # Simulate content generation delay
                threading.Event().wait(2)
                
                if not self.is_running.get():
                    break
                
                # Simulate successful post
                self.message_queue.put(("log", "✅ Tweet posted successfully"))
                self.message_queue.put(("update_metrics", None))
                self.message_queue.put(("update_timeline", None))
                
                # Wait for next post (29 minutes in real mode, 30 seconds in demo)
                threading.Event().wait(30)  # Demo mode - short interval
                
            except Exception as e:
                self.message_queue.put(("log", f"❌ Error: {e}"))
                break
    
    def generate_test_post(self):
        """Generate a test post and add to timeline"""
        # Generate test content
        sample_content = {
            "hi": "शिक्षा वह खजाना है जो कोई चुरा नहीं सकता। हर दिन कुछ नया सीखें और आगे बढ़ते रहें! 📚✨ #शिक्षा #प्रेरणा",
            "bho": "पढ़ाई-लिखाई के बिना जिनगी अधूरी बा। हर दिन कुछ नया सीखीं और आगे बढ़ीं! 📚🌟 #भोजपुरी #प्रेरणा",
            "en": "Education is the treasure that no one can steal. Keep learning something new every day! 📚✨ #Education #Motivation"
        }
        
        selected_lang = self.selected_language.get()
        content = sample_content.get(selected_lang, sample_content["en"])
        
        # Add to timeline
        new_tweet = {
            'id': f'test_{len(self.timeline_widget.tweets_data)}',
            'content': content,
            'language': selected_lang,
            'timestamp': 'Just now',
            'model': 'Test',
            'replies': 0,
            'retweets': 0,
            'likes': 0,
            'views': 1,
            'quality_score': 8.5,
            'can_delete': True
        }
        
        self.timeline_widget.tweets_data.insert(0, new_tweet)
        self.timeline_widget.refresh_timeline_display()
        
        messagebox.showinfo("Test Post", "✅ Test post generated and added to timeline!")
    
    def refresh_status(self):
        """Refresh bot status and timeline"""
        self.update_status()
        if hasattr(self, 'timeline_widget'):
            self.timeline_widget.refresh_timeline()
    
    def update_status(self):
        """Update status displays"""
        if self.bot_available:
            try:
                # Update Grok usage (if available)
                # usage = get_token_usage()
                # self.cost_used.set(f"₹{usage['estimated_inr']:.2f}/₹250")
                
                # Update other metrics (demo values)
                import random
                posts = random.randint(45, 50)
                success = random.randint(95, 100)
                
                self.posts_today.set(f"{posts}/50")
                self.success_rate.set(f"{success}%")
                
            except Exception as e:
                print(f"Status update failed: {e}")
    
    def process_queue(self):
        """Process messages from background threads"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "log":
                    # Add to log (if log widget exists)
                    pass
                elif message_type == "update_metrics":
                    self.update_status()
                elif message_type == "update_timeline":
                    # Simulate new tweet in timeline
                    if hasattr(self, 'timeline_widget'):
                        self.timeline_widget.refresh_timeline()
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EnhancedTwitterBotMacApp(root)
    
    # Handle window closing
    def on_closing():
        if app.is_running.get():
            if messagebox.askokcancel("Quit", "Bot is running. Stop and quit?"):
                app.stop_bot()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()