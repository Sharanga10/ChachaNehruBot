"""
Enhanced Twitter Client with OAuth1/OAuth2 Support and Token Refresh
Handles both user context (OAuth1) and app context (OAuth2) authentication
"""

import os
import time
import json
import logging
import requests
import tweepy
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import base64
import hashlib
import hmac
from urllib.parse import quote, urlencode

from config.main_config import config_manager
from core.security_manager import security_manager

@dataclass
class TwitterCredentials:
    """Twitter API credentials container"""
    consumer_key: str
    consumer_secret: str
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

class EnhancedTwitterClient:
    """
    Enhanced Twitter client with:
    1. OAuth 1.0a (User Context) support
    2. OAuth 2.0 (App Context) support
    3. Automatic token refresh
    4. Rate limit handling
    5. Error recovery
    6. Security integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.credentials = self._load_credentials()
        self.api_v1 = None  # OAuth 1.0a API
        self.api_v2 = None  # OAuth 2.0 API
        self.client_v2 = None  # Tweepy v2 client
        
        # Token management
        self.token_file = "security/twitter_tokens.json"
        self.last_token_refresh = None
        
        # Rate limiting
        self.rate_limits = {}
        self.last_rate_limit_check = {}
        
        # Initialize clients
        self._initialize_clients()
    
    def _load_credentials(self) -> TwitterCredentials:
        """Load Twitter credentials from environment"""
        return TwitterCredentials(
            consumer_key=os.getenv("X_CONSUMER_KEY", ""),
            consumer_secret=os.getenv("X_CONSUMER_SECRET", ""),
            access_token=os.getenv("X_ACCESS_TOKEN", ""),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET", ""),
            bearer_token=os.getenv("X_BEARER_TOKEN", ""),
            refresh_token=os.getenv("X_REFRESH_TOKEN", "")
        )
    
    def _initialize_clients(self):
        """Initialize Twitter API clients"""
        try:
            # Load saved tokens
            self._load_saved_tokens()
            
            # Initialize OAuth 1.0a (User Context) - for posting tweets
            if all([self.credentials.consumer_key, self.credentials.consumer_secret,
                   self.credentials.access_token, self.credentials.access_token_secret]):
                
                # Tweepy v1 API (OAuth 1.0a)
                auth_v1 = tweepy.OAuth1UserHandler(
                    consumer_key=self.credentials.consumer_key,
                    consumer_secret=self.credentials.consumer_secret,
                    access_token=self.credentials.access_token,
                    access_token_secret=self.credentials.access_token_secret
                )
                self.api_v1 = tweepy.API(auth_v1, wait_on_rate_limit=True)
                
                # Tweepy v2 Client (OAuth 1.0a for user context)
                self.client_v2 = tweepy.Client(
                    consumer_key=self.credentials.consumer_key,
                    consumer_secret=self.credentials.consumer_secret,
                    access_token=self.credentials.access_token,
                    access_token_secret=self.credentials.access_token_secret,
                    wait_on_rate_limit=True
                )
                
                self.logger.info("✅ OAuth 1.0a Twitter clients initialized")
            
            # Initialize OAuth 2.0 (App Context) - for reading data
            if self.credentials.bearer_token:
                self.api_v2 = tweepy.Client(
                    bearer_token=self.credentials.bearer_token,
                    wait_on_rate_limit=True
                )
                self.logger.info("✅ OAuth 2.0 Twitter client initialized")
            
            # Verify credentials
            self._verify_credentials()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Twitter clients: {e}")
            raise
    
    def _load_saved_tokens(self):
        """Load saved tokens from secure storage"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    encrypted_data = f.read()
                
                # Decrypt token data
                decrypted_data = security_manager.decrypt_sensitive_data(encrypted_data)
                token_data = json.loads(decrypted_data)
                
                # Update credentials
                if token_data.get('access_token'):
                    self.credentials.access_token = token_data['access_token']
                if token_data.get('access_token_secret'):
                    self.credentials.access_token_secret = token_data['access_token_secret']
                if token_data.get('bearer_token'):
                    self.credentials.bearer_token = token_data['bearer_token']
                if token_data.get('refresh_token'):
                    self.credentials.refresh_token = token_data['refresh_token']
                if token_data.get('expires_at'):
                    self.credentials.token_expires_at = datetime.fromisoformat(token_data['expires_at'])
                
                self.logger.info("✅ Loaded saved Twitter tokens")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load saved tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to secure storage"""
        try:
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            
            token_data = {
                'access_token': self.credentials.access_token,
                'access_token_secret': self.credentials.access_token_secret,
                'bearer_token': self.credentials.bearer_token,
                'refresh_token': self.credentials.refresh_token,
                'expires_at': self.credentials.token_expires_at.isoformat() if self.credentials.token_expires_at else None,
                'updated_at': datetime.now().isoformat()
            }
            
            # Encrypt and save
            json_data = json.dumps(token_data)
            encrypted_data = security_manager.encrypt_sensitive_data(json_data)
            
            with open(self.token_file, 'w') as f:
                f.write(encrypted_data)
            
            # Secure file permissions
            os.chmod(self.token_file, 0o600)
            
            self.logger.info("✅ Twitter tokens saved securely")
        except Exception as e:
            self.logger.error(f"❌ Failed to save tokens: {e}")
    
    def _verify_credentials(self):
        """Verify Twitter credentials are working"""
        try:
            if self.api_v1:
                # Test OAuth 1.0a
                user = self.api_v1.verify_credentials()
                if user:
                    self.logger.info(f"✅ OAuth 1.0a verified for user: @{user.screen_name}")
                    return True
            
            if self.client_v2:
                # Test with v2 client
                me = self.client_v2.get_me()
                if me.data:
                    self.logger.info(f"✅ OAuth verified for user: @{me.data.username}")
                    return True
            
            self.logger.error("❌ Could not verify Twitter credentials")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Credential verification failed: {e}")
            return False
    
    def _check_token_expiry(self) -> bool:
        """Check if tokens need refresh"""
        if not self.credentials.token_expires_at:
            return False
        
        # Refresh if expires within 5 minutes
        return datetime.now() + timedelta(minutes=5) >= self.credentials.token_expires_at
    
    def _refresh_oauth2_token(self) -> bool:
        """Refresh OAuth 2.0 bearer token"""
        try:
            if not self.credentials.refresh_token:
                self.logger.warning("⚠️ No refresh token available")
                return False
            
            # OAuth 2.0 token refresh endpoint
            token_url = "https://api.twitter.com/2/oauth2/token"
            
            # Prepare refresh request
            auth_header = base64.b64encode(
                f"{self.credentials.consumer_key}:{self.credentials.consumer_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.credentials.refresh_token
            }
            
            response = requests.post(token_url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update credentials
                self.credentials.bearer_token = token_data.get('access_token')
                if token_data.get('refresh_token'):
                    self.credentials.refresh_token = token_data['refresh_token']
                
                # Calculate expiry
                if token_data.get('expires_in'):
                    self.credentials.token_expires_at = datetime.now() + timedelta(
                        seconds=int(token_data['expires_in'])
                    )
                
                # Save updated tokens
                self._save_tokens()
                
                # Reinitialize clients
                self._initialize_clients()
                
                self.last_token_refresh = datetime.now()
                self.logger.info("✅ OAuth 2.0 token refreshed successfully")
                return True
            else:
                self.logger.error(f"❌ Token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Token refresh error: {e}")
            return False
    
    def _check_rate_limits(self, endpoint: str) -> bool:
        """Check rate limits for specific endpoint"""
        try:
            if endpoint not in self.rate_limits:
                return True
            
            rate_limit_info = self.rate_limits[endpoint]
            reset_time = rate_limit_info.get('reset', 0)
            remaining = rate_limit_info.get('remaining', 1)
            
            # Check if rate limit has reset
            if time.time() > reset_time:
                return True
            
            # Check if we have remaining requests
            if remaining > 0:
                return True
            
            # Calculate wait time
            wait_time = reset_time - time.time()
            self.logger.warning(f"⚠️ Rate limit exceeded for {endpoint}, waiting {wait_time:.0f}s")
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Rate limit check error: {e}")
            return True  # Allow request if check fails
    
    def _update_rate_limits(self, response_headers: Dict[str, str], endpoint: str):
        """Update rate limit information from response headers"""
        try:
            if 'x-rate-limit-limit' in response_headers:
                self.rate_limits[endpoint] = {
                    'limit': int(response_headers.get('x-rate-limit-limit', 0)),
                    'remaining': int(response_headers.get('x-rate-limit-remaining', 0)),
                    'reset': int(response_headers.get('x-rate-limit-reset', 0))
                }
        except Exception as e:
            self.logger.error(f"❌ Rate limit update error: {e}")
    
    def post_tweet(self, content: str, media_ids: Optional[list] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Post a tweet with enhanced error handling and retry logic
        """
        if not content or len(content.strip()) == 0:
            return False, {"error": "Empty content"}
        
        # Security check
        if not security_manager.check_rate_limit("twitter_posts", 24, 86400):  # 24 posts per day
            return False, {"error": "Daily post limit exceeded"}
        
        # Content security scan
        is_safe, threats = security_manager.scan_content_security(content)
        if not is_safe:
            self.logger.warning(f"⚠️ Content blocked by security scan: {threats}")
            return False, {"error": "Content security violation", "threats": threats}
        
        # Check token expiry
        if self._check_token_expiry():
            self.logger.info("🔄 Refreshing expired tokens")
            if not self._refresh_oauth2_token():
                self.logger.error("❌ Token refresh failed")
        
        # Try multiple methods for posting
        methods = [
            self._post_with_client_v2,
            self._post_with_api_v1,
            self._post_with_direct_api
        ]
        
        for method in methods:
            try:
                success, result = method(content, media_ids)
                if success:
                    self.logger.info(f"✅ Tweet posted successfully via {method.__name__}")
                    return True, result
                else:
                    self.logger.warning(f"⚠️ {method.__name__} failed: {result}")
            except Exception as e:
                self.logger.error(f"❌ {method.__name__} error: {e}")
        
        return False, {"error": "All posting methods failed"}
    
    def _post_with_client_v2(self, content: str, media_ids: Optional[list] = None) -> Tuple[bool, Dict[str, Any]]:
        """Post using Tweepy v2 client (OAuth 1.0a)"""
        if not self.client_v2:
            return False, {"error": "Client v2 not initialized"}
        
        try:
            response = self.client_v2.create_tweet(
                text=content,
                media_ids=media_ids
            )
            
            if response.data:
                return True, {
                    "tweet_id": response.data['id'],
                    "method": "client_v2",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return False, {"error": "No response data"}
                
        except Exception as e:
            return False, {"error": str(e)}
    
    def _post_with_api_v1(self, content: str, media_ids: Optional[list] = None) -> Tuple[bool, Dict[str, Any]]:
        """Post using Tweepy v1 API (OAuth 1.0a)"""
        if not self.api_v1:
            return False, {"error": "API v1 not initialized"}
        
        try:
            tweet = self.api_v1.update_status(
                status=content,
                media_ids=media_ids
            )
            
            if tweet:
                return True, {
                    "tweet_id": tweet.id_str,
                    "method": "api_v1",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return False, {"error": "No tweet object returned"}
                
        except Exception as e:
            return False, {"error": str(e)}
    
    def _post_with_direct_api(self, content: str, media_ids: Optional[list] = None) -> Tuple[bool, Dict[str, Any]]:
        """Post using direct API calls with OAuth 1.0a"""
        if not all([self.credentials.consumer_key, self.credentials.consumer_secret,
                   self.credentials.access_token, self.credentials.access_token_secret]):
            return False, {"error": "OAuth 1.0a credentials incomplete"}
        
        try:
            # Twitter API v1.1 endpoint
            url = "https://api.twitter.com/1.1/statuses/update.json"
            
            # Prepare parameters
            params = {"status": content}
            if media_ids:
                params["media_ids"] = ",".join(media_ids)
            
            # Create OAuth 1.0a signature
            oauth_params = self._create_oauth_signature("POST", url, params)
            
            # Make request
            response = requests.post(
                url,
                data=params,
                headers={"Authorization": oauth_params},
                timeout=30
            )
            
            if response.status_code == 200:
                tweet_data = response.json()
                return True, {
                    "tweet_id": tweet_data.get("id_str"),
                    "method": "direct_api",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return False, {
                    "error": f"API error: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return False, {"error": str(e)}
    
    def _create_oauth_signature(self, method: str, url: str, params: Dict[str, str]) -> str:
        """Create OAuth 1.0a signature for direct API calls"""
        # OAuth parameters
        oauth_params = {
            "oauth_consumer_key": self.credentials.consumer_key,
            "oauth_token": self.credentials.access_token,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": base64.b64encode(os.urandom(32)).decode().rstrip('='),
            "oauth_version": "1.0"
        }
        
        # Combine all parameters
        all_params = {**params, **oauth_params}
        
        # Create parameter string
        param_string = "&".join([
            f"{quote(str(k))}={quote(str(v))}"
            for k, v in sorted(all_params.items())
        ])
        
        # Create signature base string
        base_string = f"{method}&{quote(url)}&{quote(param_string)}"
        
        # Create signing key
        signing_key = f"{quote(self.credentials.consumer_secret)}&{quote(self.credentials.access_token_secret)}"
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode(),
                base_string.encode(),
                hashlib.sha1
            ).digest()
        ).decode()
        
        oauth_params["oauth_signature"] = signature
        
        # Create authorization header
        auth_header = "OAuth " + ", ".join([
            f'{quote(str(k))}="{quote(str(v))}"'
            for k, v in sorted(oauth_params.items())
        ])
        
        return auth_header
    
    def get_tweet_analytics(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a tweet"""
        try:
            if self.client_v2:
                tweet = self.client_v2.get_tweet(
                    tweet_id,
                    tweet_fields=['public_metrics', 'created_at', 'author_id']
                )
                
                if tweet.data:
                    return {
                        "tweet_id": tweet_id,
                        "metrics": tweet.data.public_metrics,
                        "created_at": tweet.data.created_at.isoformat() if tweet.data.created_at else None,
                        "author_id": tweet.data.author_id
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Analytics error: {e}")
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Twitter client health status"""
        return {
            "oauth1_available": self.api_v1 is not None and self.client_v2 is not None,
            "oauth2_available": self.api_v2 is not None,
            "credentials_verified": self._verify_credentials(),
            "token_expires_at": self.credentials.token_expires_at.isoformat() if self.credentials.token_expires_at else None,
            "last_token_refresh": self.last_token_refresh.isoformat() if self.last_token_refresh else None,
            "rate_limits": self.rate_limits
        }

# Global Twitter client instance
enhanced_twitter_client = EnhancedTwitterClient()