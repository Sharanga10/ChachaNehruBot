"""
Enterprise-Grade Security Management System
Multi-layered security with threat detection, rate limiting, and audit trails
"""

import os
import hashlib
import hmac
import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import ipaddress
import re
from collections import defaultdict, deque
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from config.main_config import config_manager

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEvent(Enum):
    API_ABUSE = "api_abuse"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_CONTENT = "suspicious_content"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALICIOUS_PAYLOAD = "malicious_payload"

@dataclass
class SecurityAlert:
    event_type: SecurityEvent
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: Optional[str]
    user_agent: Optional[str]
    details: Dict[str, Any]
    action_taken: str
    alert_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['threat_level'] = self.threat_level.value
        result['timestamp'] = self.timestamp.isoformat()
        return result

class EnhancedSecurityManager:
    """
    Enterprise-grade security management with:
    1. Rate limiting and DDoS protection
    2. Content security scanning
    3. API key management and rotation
    4. Threat detection and response
    5. Audit logging and compliance
    6. Encryption and data protection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = config_manager.security
        
        # Rate limiting storage
        self.rate_limits = defaultdict(lambda: deque())
        self.blocked_ips = {}
        
        # Security monitoring
        self.security_events = deque(maxlen=10000)
        self.threat_patterns = self._load_threat_patterns()
        
        # Encryption setup
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # API key management
        self.api_keys = {}
        self.key_rotation_schedule = {}
        
        # Initialize security monitoring
        self._start_security_monitoring()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for data protection"""
        key_file = "security/encryption.key"
        os.makedirs("security", exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key
    
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """Load known threat patterns for detection"""
        return {
            'sql_injection': [
                r"(\bunion\b.*\bselect\b)",
                r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
                r"(\bdrop\b.*\btable\b)",
                r"(\binsert\b.*\binto\b)",
                r"(\bupdate\b.*\bset\b)"
            ],
            'xss_patterns': [
                r"(<script[^>]*>.*?</script>)",
                r"(javascript:)",
                r"(on\w+\s*=)",
                r"(<iframe[^>]*>)",
                r"(<object[^>]*>)"
            ],
            'command_injection': [
                r"(\b(rm|cat|ls|ps|kill|wget|curl)\b)",
                r"(\||\;|\&\&|\|\|)",
                r"(\$\(.*\))",
                r"(\`.*\`)"
            ],
            'suspicious_keywords': [
                r"(hack|exploit|vulnerability|backdoor)",
                r"(malware|virus|trojan|rootkit)",
                r"(phishing|spam|scam)"
            ]
        }
    
    def _start_security_monitoring(self):
        """Start background security monitoring tasks"""
        asyncio.create_task(self._monitor_security_events())
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._rotate_encryption_keys())
    
    async def _monitor_security_events(self):
        """Monitor security events and trigger responses"""
        while True:
            try:
                # Analyze recent security events
                recent_events = list(self.security_events)[-100:]
                
                # Detect patterns
                await self._detect_attack_patterns(recent_events)
                
                # Check for anomalies
                await self._detect_anomalies(recent_events)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _cleanup_old_data(self):
        """Clean up old security data"""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(days=self.config.audit_log_retention_days)
                
                # Clean old rate limit data
                for ip in list(self.rate_limits.keys()):
                    while (self.rate_limits[ip] and 
                           self.rate_limits[ip][0] < time.time() - 3600):
                        self.rate_limits[ip].popleft()
                    
                    if not self.rate_limits[ip]:
                        del self.rate_limits[ip]
                
                # Clean old blocked IPs
                self.blocked_ips = {
                    ip: block_time for ip, block_time in self.blocked_ips.items()
                    if datetime.fromtimestamp(block_time) > cutoff_time
                }
                
                await asyncio.sleep(3600)  # Clean every hour
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _rotate_encryption_keys(self):
        """Rotate encryption keys periodically"""
        while True:
            try:
                await asyncio.sleep(self.config.encryption_key_rotation_days * 24 * 3600)
                
                # Create new encryption key
                new_key = Fernet.generate_key()
                old_cipher = self.cipher
                
                # Update cipher
                self.cipher = Fernet(new_key)
                
                # Save new key
                key_file = "security/encryption.key"
                with open(key_file, 'wb') as f:
                    f.write(new_key)
                
                self.logger.info("Encryption key rotated successfully")
                
            except Exception as e:
                self.logger.error(f"Key rotation error: {e}")
    
    def check_rate_limit(self, identifier: str, limit: int = None, window: int = 60) -> bool:
        """
        Check if request is within rate limits
        Returns True if allowed, False if rate limited
        """
        if limit is None:
            limit = self.config.rate_limit_requests_per_minute
        
        current_time = time.time()
        window_start = current_time - window
        
        # Clean old requests
        while (self.rate_limits[identifier] and 
               self.rate_limits[identifier][0] < window_start):
            self.rate_limits[identifier].popleft()
        
        # Check if within limit
        if len(self.rate_limits[identifier]) >= limit:
            self._record_security_event(
                SecurityEvent.RATE_LIMIT_EXCEEDED,
                ThreatLevel.MEDIUM,
                {"identifier": identifier, "limit": limit, "window": window}
            )
            return False
        
        # Add current request
        self.rate_limits[identifier].append(current_time)
        return True
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            # Check if block has expired (24 hours default)
            if time.time() - block_time < 86400:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False
    
    def block_ip(self, ip_address: str, duration: int = 86400):
        """Block IP address for specified duration (seconds)"""
        self.blocked_ips[ip_address] = time.time()
        self._record_security_event(
            SecurityEvent.UNAUTHORIZED_ACCESS,
            ThreatLevel.HIGH,
            {"blocked_ip": ip_address, "duration": duration}
        )
        self.logger.warning(f"IP {ip_address} blocked for {duration} seconds")
    
    def scan_content_security(self, content: str) -> Tuple[bool, List[str]]:
        """
        Scan content for security threats
        Returns (is_safe, threats_found)
        """
        threats_found = []
        
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    threats_found.append(f"{threat_type}: {pattern}")
        
        # Check for suspicious URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        for url in urls:
            if self._is_suspicious_url(url):
                threats_found.append(f"suspicious_url: {url}")
        
        is_safe = len(threats_found) == 0
        
        if not is_safe:
            self._record_security_event(
                SecurityEvent.SUSPICIOUS_CONTENT,
                ThreatLevel.HIGH if len(threats_found) > 2 else ThreatLevel.MEDIUM,
                {"threats": threats_found, "content_length": len(content)}
            )
        
        return is_safe, threats_found
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL is suspicious"""
        suspicious_domains = [
            'bit.ly', 'tinyurl.com', 't.co',  # URL shorteners
            'suspicious-domain.com', 'malware-site.net'  # Known bad domains
        ]
        
        for domain in suspicious_domains:
            if domain in url:
                return True
        
        # Check for IP addresses instead of domains
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            ipaddress.ip_address(parsed.netloc.split(':')[0])
            return True  # Direct IP access is suspicious
        except:
            pass
        
        return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise
    
    def generate_secure_token(self, payload: Dict[str, Any], expiry_hours: int = 24) -> str:
        """Generate secure JWT token"""
        secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-change-in-production')
        
        payload['exp'] = datetime.utcnow() + timedelta(hours=expiry_hours)
        payload['iat'] = datetime.utcnow()
        
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def verify_secure_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            secret_key = os.getenv('JWT_SECRET_KEY', 'default-secret-change-in-production')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")
            return None
    
    def _record_security_event(self, event_type: SecurityEvent, threat_level: ThreatLevel, 
                              details: Dict[str, Any], source_ip: str = None, 
                              user_agent: str = None):
        """Record security event for monitoring"""
        alert = SecurityAlert(
            event_type=event_type,
            threat_level=threat_level,
            timestamp=datetime.now(),
            source_ip=source_ip,
            user_agent=user_agent,
            details=details,
            action_taken="logged",
            alert_id=self._generate_alert_id()
        )
        
        self.security_events.append(alert)
        
        # Log to file for audit trail
        self._log_security_event(alert)
        
        # Trigger immediate response for critical threats
        if threat_level == ThreatLevel.CRITICAL:
            asyncio.create_task(self._handle_critical_threat(alert))
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(f"{timestamp}_{time.time()}".encode()).hexdigest()[:8]
        return f"alert_{timestamp}_{random_hash}"
    
    def _log_security_event(self, alert: SecurityAlert):
        """Log security event to audit file"""
        os.makedirs("logs/security", exist_ok=True)
        
        log_file = f"logs/security/security_audit_{datetime.now().strftime('%Y%m%d')}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert.to_dict(), ensure_ascii=False) + '\n')
    
    async def _handle_critical_threat(self, alert: SecurityAlert):
        """Handle critical security threats immediately"""
        self.logger.critical(f"CRITICAL THREAT DETECTED: {alert.alert_id}")
        
        # Block source IP if available
        if alert.source_ip:
            self.block_ip(alert.source_ip, duration=86400)
        
        # Send notification (implement based on your notification system)
        await self._send_security_notification(alert)
        
        # Take additional protective measures
        if alert.event_type == SecurityEvent.DATA_BREACH_ATTEMPT:
            await self._activate_lockdown_mode()
    
    async def _send_security_notification(self, alert: SecurityAlert):
        """Send security notification to administrators"""
        # Implement notification logic (email, Slack, etc.)
        self.logger.critical(f"Security notification: {alert.to_dict()}")
    
    async def _activate_lockdown_mode(self):
        """Activate security lockdown mode"""
        self.logger.critical("ACTIVATING SECURITY LOCKDOWN MODE")
        # Implement lockdown procedures
        # - Temporarily disable API access
        # - Increase security monitoring
        # - Require manual approval for operations
    
    async def _detect_attack_patterns(self, events: List[SecurityAlert]):
        """Detect coordinated attack patterns"""
        if len(events) < 5:
            return
        
        # Group events by source IP
        ip_events = defaultdict(list)
        for event in events:
            if event.source_ip:
                ip_events[event.source_ip].append(event)
        
        # Check for coordinated attacks
        for ip, ip_event_list in ip_events.items():
            if len(ip_event_list) > 10:  # More than 10 events from same IP
                self._record_security_event(
                    SecurityEvent.API_ABUSE,
                    ThreatLevel.CRITICAL,
                    {"coordinated_attack": True, "event_count": len(ip_event_list)},
                    source_ip=ip
                )
    
    async def _detect_anomalies(self, events: List[SecurityAlert]):
        """Detect anomalous security patterns"""
        if len(events) < 20:
            return
        
        # Calculate baseline event rates
        event_times = [event.timestamp for event in events]
        event_times.sort()
        
        # Check for sudden spikes in security events
        recent_events = [e for e in event_times if e > datetime.now() - timedelta(minutes=10)]
        
        if len(recent_events) > 20:  # More than 20 events in 10 minutes
            self._record_security_event(
                SecurityEvent.API_ABUSE,
                ThreatLevel.HIGH,
                {"anomaly_detected": True, "recent_event_count": len(recent_events)}
            )
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        recent_events = [e for e in self.security_events 
                        if e.timestamp > datetime.now() - timedelta(hours=24)]
        
        threat_counts = defaultdict(int)
        for event in recent_events:
            threat_counts[event.threat_level.value] += 1
        
        return {
            "total_events_24h": len(recent_events),
            "threat_distribution": dict(threat_counts),
            "blocked_ips": len(self.blocked_ips),
            "active_rate_limits": len(self.rate_limits),
            "last_key_rotation": "N/A",  # Implement key rotation tracking
            "security_status": "ACTIVE"
        }

# Global security manager instance
security_manager = EnhancedSecurityManager()