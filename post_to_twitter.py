# ✅ Enhanced post_to_twitter.py with OAuth1/OAuth2 Support

import logging
from typing import Tuple, Dict, Any
from core.enhanced_twitter_client import enhanced_twitter_client

logger = logging.getLogger(__name__)

def post_to_twitter(text: str) -> bool:
    """
    Post tweet using enhanced Twitter client with OAuth1/OAuth2 support
    
    Args:
        text: Tweet content
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"📤 Attempting to post tweet: {text[:50]}...")
        
        # Use enhanced Twitter client
        success, result = enhanced_twitter_client.post_tweet(text)
        
        if success:
            tweet_id = result.get("tweet_id")
            method = result.get("method", "unknown")
            logger.info(f"✅ Tweet posted successfully via {method}: {tweet_id}")
            
            # Log analytics if available
            if tweet_id:
                analytics = enhanced_twitter_client.get_tweet_analytics(tweet_id)
                if analytics:
                    logger.info(f"📊 Tweet analytics: {analytics}")
            
            return True
        else:
            error = result.get("error", "Unknown error")
            threats = result.get("threats", [])
            
            if threats:
                logger.warning(f"🛡️ Tweet blocked by security: {threats}")
            else:
                logger.error(f"❌ Failed to post tweet: {error}")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception in post_to_twitter: {e}", exc_info=True)
        return False

def get_twitter_health() -> Dict[str, Any]:
    """Get Twitter client health status"""
    try:
        return enhanced_twitter_client.get_health_status()
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {"error": str(e), "healthy": False}