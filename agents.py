from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage
from textwrap import dedent
import os
import time
import asyncio
import logging
from dotenv import load_dotenv
from config import GeminiConfig

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilientChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    """
    A wrapper around ChatGoogleGenerativeAI that handles quota errors with retries
    """
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Override the _generate method to add quota handling"""
        max_attempts = GeminiConfig.MAX_QUOTA_RETRIES
        
        for attempt in range(max_attempts):
            try:
                # Add delay before each attempt
                if attempt > 0:
                    logger.info(f"Retrying LLM call (attempt {attempt + 1}/{max_attempts})")
                    GeminiConfig.add_request_delay()
                
                return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for various rate limit and quota error patterns
                if (GeminiConfig.is_quota_error(e) or 
                    'rate limit' in error_str or 
                    'quota' in error_str or
                    'too many requests' in error_str or
                    '429' in error_str or
                    'resource_exhausted' in error_str):
                    
                    logger.warning(f"Rate limit/quota error on attempt {attempt + 1}: {e}")
                    
                    if attempt < max_attempts - 1:  # Not the last attempt
                        # Wait 60 seconds for rate limit recovery
                        wait_time = 60 + (attempt * 30)  # Increasing wait time
                        logger.info(f"Rate limit detected - waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("LLM: Maximum rate limit retries exceeded")
                        raise Exception(f"Rate limit exceeded after {max_attempts} attempts. Please wait and try again.")
                else:
                    # Non-quota error, re-raise immediately
                    logger.error(f"LLM non-quota error: {e}")
                    raise e
        
        # If we get here, all attempts failed
        raise Exception("LLM: All rate limit retry attempts failed")
    
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        """Override the async _agenerate method to add quota handling"""
        max_attempts = GeminiConfig.MAX_QUOTA_RETRIES
        
        for attempt in range(max_attempts):
            try:
                # Add delay before each attempt
                if attempt > 0:
                    logger.info(f"Retrying async LLM call (attempt {attempt + 1}/{max_attempts})")
                    await asyncio.sleep(GeminiConfig.REQUEST_DELAY)
                
                return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for various rate limit and quota error patterns
                if (GeminiConfig.is_quota_error(e) or 
                    'rate limit' in error_str or 
                    'quota' in error_str or
                    'too many requests' in error_str or
                    '429' in error_str or
                    'resource_exhausted' in error_str):
                    
                    logger.warning(f"Async rate limit/quota error on attempt {attempt + 1}: {e}")
                    
                    if attempt < max_attempts - 1:  # Not the last attempt
                        # Wait 60 seconds for rate limit recovery
                        wait_time = 60 + (attempt * 30)  # Increasing wait time
                        logger.info(f"Async rate limit detected - waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("Async LLM: Maximum rate limit retries exceeded")
                        raise Exception(f"Rate limit exceeded after {max_attempts} attempts. Please wait and try again.")
                else:
                    # Non-quota error, re-raise immediately
                    logger.error(f"Async LLM non-quota error: {e}")
                    raise e
        
        # If we get here, all attempts failed
        raise Exception("Async LLM: All rate limit retry attempts failed")

def create_resilient_llm():
    """
    Create a Gemini LLM with quota handling wrapper
    """
    try:
        llm = ResilientChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Use most stable model
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_tokens=2048,
            request_timeout=90,  # Increased timeout
            max_retries=2,  # Reduced retries (we handle this at higher level)
            retry_delay=3,
        )
        
        logger.info("Successfully created resilient Gemini LLM")
        return llm
        
    except Exception as e:
        logger.error(f"Failed to create resilient LLM: {e}")
        raise e

class GameBuilderAgents:
    def __init__(self):
        # Initialize Resilient Gemini LLM with enhanced configuration
        try:
            self.llm = create_resilient_llm()
            logger.info("Successfully initialized Gemini LLM with quota handling")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise e
    
    def senior_engineer_agent(self):
        return Agent(
            role="Senior Software Engineer",
            goal="Create high-quality, functional game code efficiently",
            backstory=dedent("""
                You are a Senior Software Engineer at a leading tech company.
                Your expertise is in Python game development using Pygame.
                You write clean, efficient, and working code that runs without errors.
                You are mindful of API usage and write concise but complete solutions.
            """),
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            max_iter=5,  # Increased iterations to handle rate limits
            memory=True,
            max_execution_time=900,  # 15 minutes max per task
        )
    
    def qa_engineer_agent(self):
        return Agent(
            role="Software Quality Control Engineer",
            goal="Identify and fix critical errors in game code efficiently",
            backstory=dedent("""
                You are a software engineer specialized in code quality assurance.
                You have a keen eye for finding syntax errors, missing imports, 
                logic issues, and security vulnerabilities in Python game code.
                You focus on fixing only critical issues to maintain code efficiency.
                You ensure the code is functional and secure.
            """),
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            max_iter=5,  # Increased iterations to handle rate limits
            memory=True,
            max_execution_time=900,  # 15 minutes max per task
        )
    
    def chief_qa_engineer_agent(self):
        return Agent(
            role="Chief Software Quality Control Engineer",
            goal="Ensure final code meets all requirements and is production-ready",
            backstory=dedent("""
                You are the Chief QA Engineer responsible for final code approval.
                You ensure the game code is complete, functional, and meets all 
                specified requirements. You make only essential changes to maintain
                code quality while being efficient with resources.
                Your final review ensures the game is ready to run.
            """),
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
            max_iter=5,  # Increased iterations to handle rate limits
            memory=True,
            max_execution_time=900,  # 15 minutes max per task
        )
    
    def get_agent_with_fallback(self, agent_type):
        """
        Get an agent with fallback configuration if primary fails
        """
        try:
            if agent_type == "senior":
                return self.senior_engineer_agent()
            elif agent_type == "qa":
                return self.qa_engineer_agent()
            elif agent_type == "chief":
                return self.chief_qa_engineer_agent()
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
                
        except Exception as e:
            logger.warning(f"Failed to create {agent_type} agent: {e}")
            logger.info("Attempting to create agent with fallback configuration...")
            
            try:
                # Create fallback LLM with more conservative settings
                fallback_llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.5,  # Lower temperature
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    max_tokens=1024,  # Reduced tokens
                    request_timeout=60,
                    max_retries=1,
                    retry_delay=5,
                )
                
                # Create a basic agent with fallback settings
                return Agent(
                    role="Fallback Game Developer",
                    goal="Create working game code with minimal resource usage",
                    backstory="You are a reliable game developer focused on creating functional code efficiently.",
                    llm=fallback_llm,
                    allow_delegation=False,
                    verbose=False,  # Reduced verbosity
                    max_iter=1,  # Single iteration
                    memory=False,  # No memory to save resources
                    max_execution_time=180,  # Reduced time
                )
                
            except Exception as fallback_error:
                logger.error(f"Fallback agent creation also failed: {fallback_error}")
                raise Exception(f"Could not create {agent_type} agent: {e}, Fallback also failed: {fallback_error}")