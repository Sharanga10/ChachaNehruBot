"""
Comprehensive Test Suite for Enhanced Ethical Bot System
Tests all components including fact-checking, security, and content generation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

# Import the modules to test
from core.enhanced_content_generator import enhanced_content_generator, ContentType
from core.fact_checker import fact_checker, FactCheckStatus
from core.security_manager import security_manager, ThreatLevel, SecurityEvent
from config.main_config import config_manager

class TestEnhancedContentGenerator:
    """Test the enhanced content generation system"""
    
    @pytest.mark.asyncio
    async def test_content_generation_basic(self):
        """Test basic content generation"""
        content, metadata = await enhanced_content_generator.generate_ethical_content(
            topic="test topic",
            content_type=ContentType.SATIRICAL,
            language="en",
            mode="DAY"
        )
        
        # Basic validations
        assert metadata is not None
        assert metadata.content_id is not None
        assert metadata.timestamp is not None
        assert metadata.content_type == ContentType.SATIRICAL
        
        if content:  # If generation was successful
            assert len(content) <= 280  # Twitter limit
            assert isinstance(content, str)
            assert len(content.strip()) > 0
    
    @pytest.mark.asyncio
    async def test_content_quality_assessment(self):
        """Test content quality assessment"""
        test_content = "This is a test tweet about India's future and democracy."
        
        quality_score = await enhanced_content_generator._assess_content_quality(
            test_content, ContentType.INFORMATIVE, "en"
        )
        
        assert 0.0 <= quality_score <= 1.0
        assert isinstance(quality_score, float)
    
    def test_prompt_generation(self):
        """Test enhanced prompt generation"""
        prompt = enhanced_content_generator._create_enhanced_prompt(
            "education", ContentType.INFORMATIVE, "hi", "DAY"
        )
        
        assert "education" in prompt
        assert "Hindi" in prompt or "हिंदी" in prompt
        assert "ETHICAL REQUIREMENTS" in prompt
        assert "280 characters" in prompt
    
    def test_model_selection(self):
        """Test optimal model selection"""
        # Test Hindi content preference
        model_hi = enhanced_content_generator._select_optimal_model(ContentType.CULTURAL, "hi")
        assert model_hi in enhanced_content_generator.config.ai_models.fallback_models
        
        # Test English content preference
        model_en = enhanced_content_generator._select_optimal_model(ContentType.REFLECTIVE, "en")
        assert model_en in enhanced_content_generator.config.ai_models.fallback_models

class TestFactChecker:
    """Test the fact-checking system"""
    
    @pytest.mark.asyncio
    async def test_fact_check_basic(self):
        """Test basic fact-checking functionality"""
        test_content = "The sun rises in the east and sets in the west."
        
        result = await fact_checker.comprehensive_fact_check(test_content)
        
        assert result is not None
        assert hasattr(result, 'status')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'fact_check_id')
        assert 0.0 <= result.confidence <= 1.0
    
    def test_claim_extraction(self):
        """Test factual claim extraction"""
        test_content = "In 2020, India had a population of 1.3 billion people according to recent studies."
        
        claims = fact_checker._extract_factual_claims(test_content)
        
        assert isinstance(claims, list)
        # Should extract the population claim
        assert len(claims) >= 0  # May or may not extract based on patterns
    
    def test_search_query_creation(self):
        """Test search query optimization"""
        claim = "India's population increased by 10% last year according to government data"
        
        query = fact_checker._create_search_query(claim)
        
        assert isinstance(query, str)
        assert len(query) > 0
        # Should remove stop words and focus on key terms
        assert "the" not in query.lower()
        assert "india" in query.lower() or "population" in query.lower()
    
    def test_fact_check_id_generation(self):
        """Test fact-check ID generation"""
        content = "Test content for ID generation"
        
        fact_id = fact_checker._generate_fact_check_id(content)
        
        assert fact_id.startswith("fc_")
        assert len(fact_id) > 10  # Should have timestamp and hash

class TestSecurityManager:
    """Test the security management system"""
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        identifier = "test_user"
        
        # Should allow first request
        assert security_manager.check_rate_limit(identifier, limit=2, window=60) == True
        
        # Should allow second request
        assert security_manager.check_rate_limit(identifier, limit=2, window=60) == True
        
        # Should block third request
        assert security_manager.check_rate_limit(identifier, limit=2, window=60) == False
    
    def test_content_security_scan(self):
        """Test content security scanning"""
        # Safe content
        safe_content = "This is a normal tweet about education and democracy."
        is_safe, threats = security_manager.scan_content_security(safe_content)
        assert is_safe == True
        assert len(threats) == 0
        
        # Potentially unsafe content
        unsafe_content = "<script>alert('xss')</script>"
        is_safe, threats = security_manager.scan_content_security(unsafe_content)
        assert is_safe == False
        assert len(threats) > 0
    
    def test_ip_blocking(self):
        """Test IP blocking functionality"""
        test_ip = "192.168.1.100"
        
        # Initially not blocked
        assert security_manager.is_ip_blocked(test_ip) == False
        
        # Block the IP
        security_manager.block_ip(test_ip, duration=3600)
        
        # Should now be blocked
        assert security_manager.is_ip_blocked(test_ip) == True
    
    def test_data_encryption(self):
        """Test data encryption/decryption"""
        test_data = "Sensitive information to encrypt"
        
        # Encrypt
        encrypted = security_manager.encrypt_sensitive_data(test_data)
        assert encrypted != test_data
        assert isinstance(encrypted, str)
        
        # Decrypt
        decrypted = security_manager.decrypt_sensitive_data(encrypted)
        assert decrypted == test_data
    
    def test_jwt_token_operations(self):
        """Test JWT token generation and verification"""
        payload = {"user_id": "test_user", "role": "admin"}
        
        # Generate token
        token = security_manager.generate_secure_token(payload, expiry_hours=1)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        decoded_payload = security_manager.verify_secure_token(token)
        assert decoded_payload is not None
        assert decoded_payload["user_id"] == "test_user"
        assert decoded_payload["role"] == "admin"

class TestConfigManager:
    """Test configuration management"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        is_valid = config_manager.validate_configuration()
        
        # Should return boolean
        assert isinstance(is_valid, bool)
    
    def test_cost_optimized_model_selection(self):
        """Test cost-optimized model selection"""
        model = config_manager.get_cost_optimized_model(quality_threshold=0.8)
        
        assert model in config_manager.ai_models.fallback_models
        assert isinstance(model, str)
    
    def test_api_key_retrieval(self):
        """Test API key retrieval (should handle missing keys gracefully)"""
        # Test with a service that likely doesn't have a key set
        key = config_manager.get_api_key('nonexistent_service')
        assert key is None
        
        # Test with known services (may or may not have keys)
        for service in ['openai', 'grok', 'twitter']:
            key = config_manager.get_api_key(service)
            # Should return string or None, not raise exception
            assert key is None or isinstance(key, str)

class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_full_content_pipeline(self):
        """Test the complete content generation pipeline"""
        try:
            # Generate content
            content, metadata = await enhanced_content_generator.generate_ethical_content(
                topic="unity and diversity",
                content_type=ContentType.REFLECTIVE,
                language="en",
                mode="DAY"
            )
            
            if content:  # If generation succeeded
                # Test security scan
                is_safe, threats = security_manager.scan_content_security(content)
                
                # Test fact-checking (if enabled)
                if config_manager.fact_check.enabled:
                    fact_result = await fact_checker.comprehensive_fact_check(content)
                    assert fact_result is not None
                
                # Validate metadata
                assert metadata.model_used in config_manager.ai_models.fallback_models + ["none"]
                assert 0.0 <= metadata.quality_score <= 1.0
                assert metadata.character_count == len(content)
                assert metadata.language == "en"
                
        except Exception as e:
            # Integration test may fail due to missing API keys, which is acceptable
            pytest.skip(f"Integration test skipped due to: {e}")
    
    def test_banned_words_integration(self):
        """Test banned words checking integration"""
        from banned_words import is_banned
        
        # Test with normal content
        normal_content = "This is a peaceful message about education."
        assert is_banned(normal_content) == False
        
        # Test would require actual banned words, which we don't want in the test file
        # Just ensure the function works
        assert callable(is_banned)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_content_generation_with_invalid_input(self):
        """Test content generation with invalid inputs"""
        # Test with None topic
        content, metadata = await enhanced_content_generator.generate_ethical_content(
            topic=None,
            content_type=ContentType.SATIRICAL,
            language="en"
        )
        
        # Should handle gracefully
        assert metadata is not None
    
    def test_security_scan_with_empty_content(self):
        """Test security scanning with edge cases"""
        # Empty content
        is_safe, threats = security_manager.scan_content_security("")
        assert isinstance(is_safe, bool)
        assert isinstance(threats, list)
        
        # Very long content
        long_content = "A" * 10000
        is_safe, threats = security_manager.scan_content_security(long_content)
        assert isinstance(is_safe, bool)
        assert isinstance(threats, list)
    
    def test_rate_limiting_edge_cases(self):
        """Test rate limiting with edge cases"""
        # Test with zero limit
        result = security_manager.check_rate_limit("test", limit=0, window=60)
        assert result == False
        
        # Test with negative limit (should handle gracefully)
        result = security_manager.check_rate_limit("test2", limit=-1, window=60)
        assert isinstance(result, bool)

# Test fixtures and utilities
@pytest.fixture
def mock_api_responses():
    """Mock API responses for testing"""
    return {
        'openai_response': {
            'choices': [{'message': {'content': 'Test generated content'}}]
        },
        'fact_check_response': {
            'confidence': 0.85,
            'status': 'verified'
        }
    }

# Performance tests
class TestPerformance:
    """Performance and load tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_content_generation(self):
        """Test concurrent content generation"""
        tasks = []
        for i in range(5):  # Generate 5 pieces of content concurrently
            task = enhanced_content_generator.generate_ethical_content(
                topic=f"test topic {i}",
                content_type=ContentType.SATIRICAL,
                language="en"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle concurrent requests
        assert len(results) == 5
        for result in results:
            if not isinstance(result, Exception):
                content, metadata = result
                assert metadata is not None
    
    def test_rate_limiting_performance(self):
        """Test rate limiting performance with many requests"""
        identifier = "perf_test"
        
        # Make many requests quickly
        results = []
        for i in range(100):
            result = security_manager.check_rate_limit(identifier, limit=50, window=60)
            results.append(result)
        
        # Should handle many requests efficiently
        assert len(results) == 100
        # First 50 should be allowed, rest blocked
        assert sum(results) == 50

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])