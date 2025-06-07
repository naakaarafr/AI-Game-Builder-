from crewai_tools import tool
import subprocess
import tempfile
import os

class GameBuilderTools:
    
    @tool("Python Code Validator")
    def validate_python_code(self, code: str) -> str:
        """
        Validates Python code for syntax errors and basic issues.
        """
        try:
            # Create a temporary file to test the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Try to compile the code
            with open(temp_file_path, 'r') as f:
                compile(f.read(), temp_file_path, 'exec')
            
            # Clean up
            os.unlink(temp_file_path)
            
            return "Code validation successful: No syntax errors found."
            
        except SyntaxError as e:
            # Clean up
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
            return f"Syntax Error found: {str(e)}"
        except Exception as e:
            # Clean up
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
            return f"Error during validation: {str(e)}"
    
    @tool("Code Security Scanner")
    def scan_security_issues(self, code: str) -> str:
        """
        Scans Python code for potential security vulnerabilities.
        """
        security_issues = []
        
        # Check for dangerous functions
        dangerous_functions = ['eval', 'exec', 'input', '__import__', 'open']
        for func in dangerous_functions:
            if func + '(' in code:
                security_issues.append(f"Potentially dangerous function '{func}' found")
        
        # Check for shell commands
        if 'subprocess' in code or 'os.system' in code:
            security_issues.append("Shell command execution detected")
        
        # Check for file operations
        if 'open(' in code and ('w' in code or 'a' in code):
            security_issues.append("File write operations detected")
        
        if security_issues:
            return "Security issues found: " + "; ".join(security_issues)
        else:
            return "No obvious security issues detected."