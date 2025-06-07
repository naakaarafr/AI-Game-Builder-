import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiConfig:
    """Configuration class for Gemini AI settings with intelligent rate limiting"""
    
    # API Key
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model configuration - Use flash model for lower rate limits
    DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    FALLBACK_MODEL = "gemini-1.5-flash"  # Even cheaper fallback
    
    # Generation parameters - Reduced for rate limiting
    TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))  # Reduced from 4096
    
    # Rate limiting settings
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "3.0"))  # Increased from 2.0
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))  # Increased retries
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "5.0"))
    
    # Quota restoration settings
    QUOTA_WAIT_TIME = 65  # Wait 65 seconds for quota to restore (1 minute + buffer)
    MAX_QUOTA_RETRIES = 10  # Maximum number of quota restoration attempts
    EXPONENTIAL_BACKOFF_BASE = 2
    MAX_BACKOFF_TIME = 300  # Max 5 minutes backoff
    
    @classmethod
    def validate_config(cls):
        """Validate the configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found. Please set it in your .env file or environment variables."
            )
    
    @classmethod
    def get_model_config(cls, use_fallback=False):
        """Get the model configuration dictionary"""
        cls.validate_config()
        model = cls.FALLBACK_MODEL if use_fallback else cls.DEFAULT_MODEL
        return {
            "model": model,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
            "request_timeout": 60,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY
        }
    
    @classmethod
    def add_request_delay(cls):
        """Add delay between requests to respect rate limits"""
        logger.info(f"Adding request delay of {cls.REQUEST_DELAY} seconds")
        time.sleep(cls.REQUEST_DELAY)
    
    @classmethod
    def handle_quota_exceeded(cls, retry_count=0):
        """
        Handle quota exceeded errors with intelligent waiting
        
        Args:
            retry_count: Current retry attempt number
            
        Returns:
            bool: True if should retry, False if max retries exceeded
        """
        if retry_count >= cls.MAX_QUOTA_RETRIES:
            logger.error(f"Maximum quota retry attempts ({cls.MAX_QUOTA_RETRIES}) exceeded")
            return False
        
        # Calculate wait time with exponential backoff
        base_wait = cls.QUOTA_WAIT_TIME
        exponential_factor = min(cls.EXPONENTIAL_BACKOFF_BASE ** retry_count, cls.MAX_BACKOFF_TIME / base_wait)
        wait_time = min(base_wait * exponential_factor, cls.MAX_BACKOFF_TIME)
        
        logger.warning(f"Quota exceeded! Attempt {retry_count + 1}/{cls.MAX_QUOTA_RETRIES}")
        logger.info(f"Waiting {wait_time:.1f} seconds for quota restoration...")
        
        # Show progress during wait
        cls._show_wait_progress(wait_time)
        
        return True
    
    @classmethod
    def _show_wait_progress(cls, wait_time):
        """Show progress bar during wait time"""
        import sys
        
        total_seconds = int(wait_time)
        for remaining in range(total_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02d}:{secs:02d}"
            progress = (total_seconds - remaining) / total_seconds * 100
            bar_length = 30
            filled_length = int(bar_length * progress // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            sys.stdout.write(f'\rWaiting for quota restoration: [{bar}] {progress:.1f}% - {timer}')
            sys.stdout.flush()
            time.sleep(1)
        
        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line
        sys.stdout.flush()
        logger.info("Quota wait completed. Resuming operations...")
    
    @classmethod
    def is_quota_error(cls, error):
        """
        Check if the error is related to quota/rate limiting
        
        Args:
            error: Exception object or string
            
        Returns:
            bool: True if it's a quota/rate limit error
        """
        error_str = str(error).lower()
        quota_indicators = [
            '429',
            'rate limit',
            'quota exceeded',
            'resource_exhausted',
            'resourceexhausted',
            'too many requests',
            'rate_limit_exceeded',
            'quota_exceeded'
        ]
        
        return any(indicator in error_str for indicator in quota_indicators)
    
    @classmethod
    def get_adaptive_delay(cls, error_count=0):
        """
        Get adaptive delay based on error count
        
        Args:
            error_count: Number of consecutive errors
            
        Returns:
            float: Delay time in seconds
        """
        if error_count == 0:
            return cls.REQUEST_DELAY
        
        # Exponential backoff for consecutive errors
        adaptive_delay = cls.REQUEST_DELAY * (cls.EXPONENTIAL_BACKOFF_BASE ** min(error_count, 5))
        return min(adaptive_delay, cls.MAX_BACKOFF_TIME)