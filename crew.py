from crewai import Crew, Process
from agents import GameBuilderAgents
from tasks import GameBuilderTasks
from tools import GameBuilderTools
from config import GeminiConfig
import time
import logging

# Set up logging to track rate limiting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameBuilderCrew:
    def __init__(self):
        self.agents = GameBuilderAgents()
        self.tasks = GameBuilderTasks()
        self.tools = GameBuilderTools()
        self.consecutive_errors = 0

    def run(self, game_instructions):
        """
        Run the crew with intelligent quota handling and automatic recovery
        """
        quota_retry_count = 0
        
        while quota_retry_count < GeminiConfig.MAX_QUOTA_RETRIES:
            try:
                logger.info(f"Starting crew execution (attempt {quota_retry_count + 1})")
                
                # Add adaptive delay based on previous errors
                adaptive_delay = GeminiConfig.get_adaptive_delay(self.consecutive_errors)
                if adaptive_delay > GeminiConfig.REQUEST_DELAY:
                    logger.info(f"Using adaptive delay of {adaptive_delay} seconds due to previous errors")
                    time.sleep(adaptive_delay)
                else:
                    GeminiConfig.add_request_delay()
                
                # Create agents
                senior_engineer = self.agents.senior_engineer_agent()
                qa_engineer = self.agents.qa_engineer_agent()
                chief_qa_engineer = self.agents.chief_qa_engineer_agent()
                
                # Add tools to agents
                qa_engineer.tools = [self.tools.validate_python_code, self.tools.scan_security_issues]
                chief_qa_engineer.tools = [self.tools.validate_python_code]
                
                # Create tasks
                code_task = self.tasks.code_task(senior_engineer, game_instructions)
                review_task = self.tasks.review_task(qa_engineer, game_instructions)
                evaluate_task = self.tasks.evaluate_task(chief_qa_engineer, game_instructions)
                
                # Create crew with rate limit friendly settings
                crew = Crew(
                    agents=[senior_engineer, qa_engineer, chief_qa_engineer],
                    tasks=[code_task, review_task, evaluate_task],
                    process=Process.sequential,
                    verbose=True,
                    max_rpm=3,  # Very conservative requests per minute - reduced from 5
                    step_callback=self._rate_limit_callback  # Enhanced callback for rate limiting
                )
                
                # Execute the crew with rate limit handling
                logger.info("Executing crew tasks with rate limit protection...")
                result = crew.kickoff()
                
                # Reset error count on success
                self.consecutive_errors = 0
                logger.info("Crew execution completed successfully")
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Enhanced rate limit detection
                is_rate_limit_error = (
                    GeminiConfig.is_quota_error(e) or
                    'rate limit' in error_str or
                    'quota' in error_str or
                    'too many requests' in error_str or
                    '429' in error_str or
                    'resource_exhausted' in error_str or
                    'iteration limit' in error_str or
                    'time limit' in error_str
                )
                
                if is_rate_limit_error:
                    logger.warning(f"Rate limit/quota error detected: {e}")
                    
                    # Handle the error with increasing wait times
                    if quota_retry_count < GeminiConfig.MAX_QUOTA_RETRIES - 1:
                        wait_time = 60 + (quota_retry_count * 30)  # 60s, 90s, 120s, etc.
                        logger.info(f"Rate limit detected - waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        
                        quota_retry_count += 1
                        self.consecutive_errors += 1
                        logger.info(f"Retrying crew execution (attempt {quota_retry_count + 1})")
                        continue
                    else:
                        logger.error("Maximum rate limit retry attempts exceeded")
                        return self._create_error_response("rate_limit_exceeded")
                else:
                    logger.error(f"Non-rate-limit error occurred: {e}")
                    # For non-rate-limit errors, try a few times with exponential backoff
                    if self.consecutive_errors < 3:
                        self.consecutive_errors += 1
                        wait_time = 10 * (2 ** self.consecutive_errors)
                        logger.info(f"Retrying after {wait_time} seconds due to error...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Maximum consecutive errors reached")
                        raise e
        
        # If we exit the loop, we've exceeded max retries
        return self._create_error_response("max_retries_exceeded")
    
    def _rate_limit_callback(self, step):
        """Enhanced callback function to handle rate limits between steps"""
        try:
            logger.info(f"Completed step: {step}")
            
            # Add longer delay between steps to prevent rate limiting
            base_delay = 15  # Base 15 seconds between steps
            adaptive_delay = GeminiConfig.get_adaptive_delay(self.consecutive_errors)
            final_delay = max(base_delay, adaptive_delay)
            
            logger.info(f"Adding {final_delay} second delay between steps to prevent rate limits...")
            time.sleep(final_delay)
            
        except Exception as e:
            logger.warning(f"Step callback error: {e}")
            # Add a safety delay even if callback fails
            time.sleep(20)
    
    def _create_error_response(self, error_type):
        """Create a helpful error response for different error types"""
        if error_type == "rate_limit_exceeded":
            return """
# Game Creation Failed - Rate Limit Exceeded

Unfortunately, the Google Gemini API rate limit has been exceeded and automatic recovery failed.

## What happened:
- The AI agents hit the API rate limit (requests per minute)
- Multiple automatic retry attempts were made with increasing wait times
- Maximum retry attempts were reached

## Solutions:
1. **Wait and retry**: Wait 5-10 minutes and run the program again
2. **Check API quotas**: Visit Google Cloud Console to check your API rate limits
3. **Upgrade plan**: Consider upgrading your Google Cloud billing plan for higher limits
4. **Use different API key**: If you have another API key, try using that
5. **Simplify request**: Try creating a simpler game to reduce API calls

## The system automatically:
- Waits 60+ seconds between retries
- Adds delays between agent steps
- Limits requests per minute to 3
- Uses exponential backoff for retries

## To retry:
Wait 5-10 minutes and run the program again. The rate limits should reset.
"""
        elif error_type == "quota_exceeded":
            return """
# Game Creation Failed - Quota Exceeded

Unfortunately, the Google Gemini API quota has been exceeded and automatic recovery failed.

## What happened:
- The AI agents made too many requests to the Gemini API
- Multiple automatic retry attempts were made
- Quota restoration waiting periods were completed
- Maximum retry attempts were reached

## Solutions:
1. **Wait and retry**: Wait 1-2 hours and run the program again
2. **Check quotas**: Visit Google Cloud Console to check your API quotas
3. **Upgrade plan**: Consider upgrading your Google Cloud billing plan
4. **Use different API key**: If you have another API key, try using that
5. **Simplify request**: Try creating a simpler game to reduce API usage

## To retry:
Run the program again with a simpler game prompt or wait for quota restoration.
"""
        elif error_type == "max_retries_exceeded":
            return """
# Game Creation Failed - Maximum Retries Exceeded

The system attempted multiple times to complete your game creation but encountered persistent issues.

## What to try:
1. Check your internet connection
2. Verify your Google API key is valid
3. Ensure you have sufficient API quota and rate limits
4. Try again with a simpler game description
5. Check Google Cloud Console for any service issues
6. Wait 10-15 minutes for rate limits to reset

## To retry:
Wait a few minutes and try running the program again.
"""
        else:
            return f"Game creation failed due to: {error_type}"
    
    def run_with_monitoring(self, game_instructions):
        """
        Run the crew with enhanced monitoring and logging
        """
        start_time = time.time()
        logger.info("="*50)
        logger.info("STARTING GAME CREATION WITH RATE LIMIT PROTECTION")
        logger.info("="*50)
        
        try:
            result = self.run(game_instructions)
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info("="*50)
            logger.info(f"GAME CREATION COMPLETED in {duration:.1f} seconds")
            logger.info("="*50)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error("="*50)
            logger.error(f"GAME CREATION FAILED after {duration:.1f} seconds")
            logger.error(f"Error: {e}")
            logger.error("="*50)
            
            raise e