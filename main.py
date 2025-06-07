import sys
import os
import time
import logging
from dotenv import load_dotenv
from crew import GameBuilderCrew
from config import GeminiConfig

# Load environment variables
load_dotenv()

# Set up enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('game_builder.log')
    ]
)
logger = logging.getLogger(__name__)

# Check if Google API key is set
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ Warning: GOOGLE_API_KEY not found in environment variables.")
    print("Please set your Google API key in a .env file or as an environment variable.")

# Game examples for reference
GAME_EXAMPLES = {
    'example1_pacman': """
        Create a simple Pacman game using Python and Pygame.
        The game should have:
        - A Pacman character that moves around
        - Dots to collect
        - Simple maze layout
        - Score tracking
        - Basic game loop with proper event handling
        Keep the code concise and under 200 lines.
    """,
    'example2_pong': """
        Create a classic Pong game using Python and Pygame.
        The game should have:
        - Two paddles (player vs computer)
        - A ball that bounces around
        - Score tracking for both players
        - Simple AI for computer opponent
        - Proper collision detection
        Keep the code concise and under 150 lines.
    """,
    'example3_snake': """
        Create a Snake game using Python and Pygame.
        The game should have:
        - A snake that grows when eating food
        - Food items that appear randomly
        - Game over when snake hits walls or itself
        - Score tracking
        - Smooth movement and controls
        Keep the code concise and under 150 lines.
    """
}

def check_api_status():
    """Check if API is accessible and not rate limited"""
    try:
        # Validate configuration
        GeminiConfig.validate_config()
        logger.info("✓ API key found and configuration validated")
        
        # Show current configuration
        print("\n📊 Current Configuration:")
        print(f"  • Model: {GeminiConfig.DEFAULT_MODEL}")
        print(f"  • Request delay: {GeminiConfig.REQUEST_DELAY}s")
        print(f"  • Quota wait time: {GeminiConfig.QUOTA_WAIT_TIME}s")
        print(f"  • Max retries: {GeminiConfig.MAX_QUOTA_RETRIES}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Configuration error: {e}")
        return False

def display_examples():
    """Display available game examples"""
    print("\n=== EXAMPLE GAMES FOR REFERENCE ===")
    print("1. Pacman - Classic arcade game with maze navigation")
    print("2. Pong - Simple paddle and ball game")
    print("3. Snake - Growing snake collection game (Recommended)")
    print("=====================================\n")

def get_user_game_prompt():
    """Get game development prompt from user"""
    print("🎮 Welcome to the Enhanced Game Builder! 🎮")
    print("=" * 50)
    print("✨ Now with automatic quota handling and recovery!")
    
    display_examples()
    
    print("Choose an option:")
    print("1. Create a custom game (write your own prompt)")
    print("2. Use a pre-made example")
    print("3. View example prompts for inspiration")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            return get_custom_game_prompt()
        elif choice == "2":
            return get_example_game()
        elif choice == "3":
            show_example_prompts()
            continue
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def get_custom_game_prompt():
    """Get custom game prompt from user"""
    print("\n" + "=" * 50)
    print("CREATE YOUR CUSTOM GAME")
    print("=" * 50)
    print("📝 Describe the game you want to create. Be specific about:")
    print("  • Game type/genre (e.g., puzzle, arcade, strategy)")
    print("  • Key features and mechanics")
    print("  • Visual elements")
    print("  • Controls")
    print("  • Win/lose conditions")
    print("  • Any special requirements")
    print("\n💡 Example: 'Create a space shooter game where the player...'")
    print("⚡ Tip: Keep it concise to reduce API usage and improve results.")
    print("-" * 50)
    
    game_prompt = []
    print("Enter your game description (press Enter twice when finished):")
    
    while True:
        line = input()
        if line == "" and game_prompt and game_prompt[-1] == "":
            break
        game_prompt.append(line)
    
    # Remove the last empty line if it exists
    if game_prompt and game_prompt[-1] == "":
        game_prompt.pop()
    
    final_prompt = "\n".join(game_prompt).strip()
    
    if not final_prompt:
        print("No prompt entered. Using Snake game example instead.")
        return GAME_EXAMPLES['example3_snake']
    
    # Add technical requirements to user prompt
    enhanced_prompt = f"""
Create a game using Python and Pygame based on this description:

{final_prompt}

Technical Requirements:
- Use Python and Pygame library
- Include proper game loop with event handling
- Add basic collision detection if needed
- Include score tracking if applicable
- Keep the code concise and well-structured
- Ensure the game is playable and complete
- Add comments for major sections only (to reduce code length)

Make sure the game is functional and can be run directly.
"""
    
    return enhanced_prompt

def get_example_game():
    """Let user choose from example games"""
    print("\n" + "=" * 30)
    print("CHOOSE AN EXAMPLE GAME")
    print("=" * 30)
    print("1. Pacman Game")
    print("2. Pong Game") 
    print("3. Snake Game (Recommended - shorter code)")
    
    while True:
        choice = input("\nSelect example (1-3): ").strip()
        
        if choice == "1":
            return GAME_EXAMPLES['example1_pacman']
        elif choice == "2":
            return GAME_EXAMPLES['example2_pong']
        elif choice == "3":
            return GAME_EXAMPLES['example3_snake']
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def show_example_prompts():
    """Show example prompts for inspiration"""
    print("\n" + "=" * 50)
    print("EXAMPLE PROMPTS FOR INSPIRATION")
    print("=" * 50)
    
    examples = [
        "Create a Tetris-like puzzle game with falling blocks",
        "Make a platformer game with jumping and obstacle avoidance",
        "Build a space invaders shooter with enemies and power-ups",
        "Design a maze game where the player collects items",
        "Create a memory matching card game",
        "Make a simple racing game with a top-down view",
        "Build a tower defense game with waves of enemies",
        "Create a breakout/brick breaker game with paddle and ball"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print("\nFeel free to use these as starting points or create something completely new!")
    print("=" * 50)

def run():
    """
    Run the Game Builder Crew with enhanced quota handling
    """
    print("## Welcome to the Enhanced Game Crew")
    print('=' * 40)
    print("🚀 Features:")
    print("  • Automatic quota detection and recovery")
    print("  • Intelligent retry mechanisms")
    print("  • Progress monitoring")
    print("  • Enhanced error handling")
    print('=' * 40)
    
    # Check API status first
    if not check_api_status():
        return
    
    # Get game instructions from user
    try:
        game_instructions = get_user_game_prompt()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        return
    
    print("\n" + "=" * 60)
    print("🎯 STARTING ENHANCED GAME DEVELOPMENT")
    print("=" * 60)
    print("Your prompt:")
    print("-" * 20)
    print(game_instructions[:200] + "..." if len(game_instructions) > 200 else game_instructions)
    print("-" * 20)
    
    confirm = input("\n✅ Proceed with game creation? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ Game creation cancelled.")
        return
    
    print("\n🚀 Starting enhanced game creation process...")
    print("📊 Features enabled:")
    print("  • Automatic quota monitoring")
    print("  • Smart retry with exponential backoff")
    print("  • Progress tracking with visual indicators")
    print("  • Automatic recovery from rate limits")
    print("\n⏱️  This may take 2-10 minutes depending on API quota")
    print("🔄 Please be patient while the system handles any quota limitations...")
    print()
    
    try:
        # Create and run the crew with enhanced monitoring
        crew = GameBuilderCrew()
        result = crew.run_with_monitoring(game_instructions)
        
        # Check if result is an error message
        if isinstance(result, str) and "# Game Creation Failed" in result:
            print("\n" + "=" * 60)
            print("❌ GAME CREATION ENCOUNTERED ISSUES")
            print("=" * 60)
            print(result)
            print("=" * 60)
            return
        
        print("\n\n" + "=" * 60)
        print("🎉 GAME CREATION COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 60)
        print("\n🎮 Your game code is ready:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        print("\n📋 To run your game:")
        print("1. Save the code to a .py file (e.g., my_game.py)")
        print("2. Install pygame: pip install pygame")
        print("3. Run: python my_game.py")
        print("\n💡 Tips:")
        print("  • Make sure you have Python 3.7+ installed")
        print("  • If you get import errors, install missing packages")
        print("  • The game window should open when you run the code")
        
        # Save to file option
        save_option = input("\n💾 Would you like to save the code to a file? (y/n): ").lower().strip()
        if save_option == 'y':
            filename = input("Enter filename (without extension): ").strip() or "my_game"
            filename = f"{filename}.py"
            try:
                with open(filename, 'w') as f:
                    f.write(str(result))
                print(f"✅ Code saved to {filename}")
            except Exception as e:
                print(f"❌ Error saving file: {e}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Game creation interrupted by user.")
        logger.info("Game creation interrupted by user")
        
    except Exception as e:
        error_str = str(e).lower()
        
        if GeminiConfig.is_quota_error(e):
            print("\n" + "=" * 60)
            print("⚠️  QUOTA LIMITATION DETECTED")
            print("=" * 60)
            print("The system detected API quota limitations that couldn't be automatically resolved.")
            print("\n🔧 Recommended solutions:")
            print("1. ⏰ Wait 1-2 hours and try again")
            print("2. 🔍 Check your Google Cloud Console for quota limits")
            print("3. 💳 Consider upgrading your Google Cloud billing plan")
            print("4. 🔑 Try using a different API key if available")
            print("5. 📝 Create a simpler game to reduce API usage")
            print("\n💡 The system made multiple automatic attempts to recover.")
            
        elif "connection" in error_str or "network" in error_str:
            print("\n❌ Network connectivity issue detected!")
            print("Solutions:")
            print("1. Check your internet connection")
            print("2. Try again in a few minutes")
            print("3. Check if Google AI services are accessible")
            
        else:
            print(f"\n❌ Unexpected error occurred: {e}")
            print("💡 Please check the logs for more details.")
            logger.error(f"Unexpected error in main: {e}", exc_info=True)

def train():
    """
    Train the crew for a given number of iterations with quota awareness
    """
    if len(sys.argv) < 3:
        print("Usage: python main.py train <n_iterations> <filename>")
        return
    
    try:
        n_iterations = int(sys.argv[1])
        filename = sys.argv[2]
        
        print("⚠️  Warning: Training will use significant API quota!")
        estimated_calls = n_iterations * 6  # 3 agents * 2 iterations average
        print(f"📊 Estimated API calls: {estimated_calls}")
        print(f"⏱️  Estimated time with quota handling: {estimated_calls * 4} seconds")
        
        # Ask for confirmation
        confirm = input("Continue with training? (y/N): ").lower().strip()
        if confirm != 'y':
            print("❌ Training cancelled.")
            return
            
        if not check_api_status():
            print("❌ API status check failed. Cannot proceed with training.")
            return
        
        # Use Snake game for training (shortest example)
        game_instructions = GAME_EXAMPLES['example3_snake']
        
        print(f"\n🚀 Starting training for {n_iterations} iterations...")
        print(f"💾 Training data will be saved to {filename}")
        print("🔄 Using Snake game example for consistent training data")
        
        # Create crew and attempt training
        crew = GameBuilderCrew()
        
        training_results = []
        successful_runs = 0
        
        for i in range(n_iterations):
            print(f"\n📈 Training iteration {i+1}/{n_iterations}")
            try:
                result = crew.run_with_monitoring(game_instructions)
                if not isinstance(result, str) or "# Game Creation Failed" not in result:
                    training_results.append({
                        'iteration': i+1,
                        'status': 'success',
                        'result': str(result)[:500] + "..." if len(str(result)) > 500 else str(result)
                    })
                    successful_runs += 1
                    print(f"✅ Iteration {i+1} completed successfully")
                else:
                    training_results.append({
                        'iteration': i+1,
                        'status': 'failed',
                        'error': 'Quota or system error'
                    })
                    print(f"❌ Iteration {i+1} failed due to quota/system issues")
                
                # Add delay between training iterations
                if i < n_iterations - 1:
                    print("⏳ Adding delay between training iterations...")
                    time.sleep(30)  # 30 second delay between iterations
                    
            except Exception as e:
                training_results.append({
                    'iteration': i+1,
                    'status': 'error',
                    'error': str(e)
                })
                print(f"❌ Iteration {i+1} encountered error: {e}")
                
                # If quota error, wait longer
                if GeminiConfig.is_quota_error(e):
                    print("⏰ Quota error detected, waiting 2 minutes before continuing...")
                    time.sleep(120)
        
        # Save training results
        try:
            import json
            with open(filename, 'w') as f:
                json.dump({
                    'total_iterations': n_iterations,
                    'successful_runs': successful_runs,
                    'success_rate': successful_runs / n_iterations * 100,
                    'results': training_results
                }, f, indent=2)
            
            print(f"\n📊 Training completed!")
            print(f"✅ Successful runs: {successful_runs}/{n_iterations} ({successful_runs/n_iterations*100:.1f}%)")
            print(f"💾 Results saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving training results: {e}")
        
    except ValueError:
        print("❌ Invalid number of iterations. Please provide a valid integer.")
    except Exception as e:
        logger.error(f"Training error: {e}", exc_info=True)
        print(f"❌ Training failed: {e}")

def monitor_quota():
    """Monitor API quota usage (utility function)"""
    print("📊 Quota Monitoring Utility")
    print("=" * 30)
    print("Current configuration:")
    print(f"  • Request delay: {GeminiConfig.REQUEST_DELAY}s")
    print(f"  • Quota wait time: {GeminiConfig.QUOTA_WAIT_TIME}s")
    print(f"  • Max retries: {GeminiConfig.MAX_QUOTA_RETRIES}")
    print(f"  • Max backoff time: {GeminiConfig.MAX_BACKOFF_TIME}s")
    print("\n💡 This tool helps you understand the current quota settings.")
    print("For actual quota usage, check your Google Cloud Console.")

if __name__ == "__main__":
    # Enhanced command line interface
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "train":
            train()
        elif command == "monitor":
            monitor_quota()
        elif command == "help":
            print("🎮 Game Builder Commands:")
            print("  python main.py          - Run interactive game builder")
            print("  python main.py train <n> <file> - Train the crew")
            print("  python main.py monitor  - Show quota monitoring info")
            print("  python main.py help     - Show this help message")
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python main.py help' for available commands")
    else:
        run()