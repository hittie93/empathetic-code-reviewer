# Empathetic Code Reviewer using Groq API
# Fast, free, and powerful AI for hackathons!

import json
import requests
from typing import Dict, List
import re
import time

 

class EmpathethicCodeReviewer:
    def __init__(self, groq_api_key: str):
        """Initialize the empathetic code reviewer with Groq API key"""
        self.groq_api_key = "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"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-8b-8192"  # Fast and free model
        
    def make_groq_request(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Make a request to Groq API"""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Groq API: {e}")
            return self.get_fallback_response()
        except Exception as e:
            print(f"Unexpected error: {e}")
            return self.get_fallback_response()
    
    def get_fallback_response(self) -> str:
        """Fallback response if API fails"""
        return """POSITIVE_REPHRASING: Great work on implementing this functionality! Let's explore some ways to make this code even better.
WHY_EXPLANATION: These improvements will help make your code more efficient, readable, and maintainable.
CODE_IMPROVEMENT: # Improved version would go here"""

    def analyze_comment_severity(self, comment: str) -> str:
        """Determine the severity/tone of the original comment"""
        harsh_indicators = ['bad', 'wrong', 'terrible', 'awful', 'stupid', 'inefficient', 'horrible', 'trash']
        moderate_indicators = ['could be better', 'consider', 'might want', 'should', 'redundant']
        
        comment_lower = comment.lower()
        
        if any(indicator in comment_lower for indicator in harsh_indicators):
            return "harsh"
        elif any(indicator in comment_lower for indicator in moderate_indicators):
            return "moderate"
        else:
            return "neutral"
    
    def get_relevant_resources(self, comment: str, code_language: str = "python") -> List[str]:
        """Generate relevant documentation links based on the comment content"""
        resources = []
        comment_lower = comment.lower()
        
        # Python-specific resources
        if code_language.lower() == "python":
            if "variable" in comment_lower or "name" in comment_lower:
                resources.extend([
                    "https://pep8.org/#naming-conventions",
                    "https://realpython.com/python-pep8/#naming-conventions"
                ])
            if "boolean" in comment_lower or "== true" in comment_lower or "redundant" in comment_lower:
                resources.extend([
                    "https://pep8.org/#programming-recommendations",
                    "https://docs.python.org/3/tutorial/datastructures.html#more-on-conditions"
                ])
            if "inefficient" in comment_lower or "performance" in comment_lower or "loop" in comment_lower:
                resources.extend([
                    "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions",
                    "https://realpython.com/list-comprehension-python/"
                ])
        
        return resources
    
    def detect_experience_level(self, code_snippet: str) -> str:
        """Detect developer experience level from code patterns"""
        beginner_patterns = ['== True', '== False', 'results = []', 'append(', 'range(len(']
        intermediate_patterns = ['comprehension', 'lambda', 'yield', 'enumerate', 'zip']
        
        code_lower = code_snippet.lower()
        
        beginner_score = sum(1 for pattern in beginner_patterns if pattern in code_lower)
        intermediate_score = sum(1 for pattern in intermediate_patterns if pattern in code_lower)
        
        if beginner_score >= 2 and intermediate_score == 0:
            return "beginner"
        elif intermediate_score > 0:
            return "intermediate"
        else:
            return "beginner"  # Default to beginner for safer tone
    
    def generate_empathetic_feedback(self, code_snippet: str, original_comment: str) -> Dict[str, str]:
        """Generate empathetic feedback for a single comment using Groq"""
        
        severity = self.analyze_comment_severity(original_comment)
        experience_level = self.detect_experience_level(code_snippet)
        
        # Adjust tone based on severity and experience
        tone_instructions = {
            "harsh": {
                "beginner": "Be extra gentle, encouraging, and patient. This person is learning, and harsh feedback can be discouraging.",
                "intermediate": "Be supportive and constructive. Acknowledge their skills while suggesting improvements."
            },
            "moderate": {
                "beginner": "Be encouraging and educational. Focus on learning opportunities.",
                "intermediate": "Be professional and helpful with clear explanations."
            },
            "neutral": {
                "beginner": "Be friendly and educational.",
                "intermediate": "Be professional and direct."
            }
        }
        
        tone_instruction = tone_instructions[severity][experience_level]
        
        # Create context-aware prompt
        prompt = f"""You are an experienced, empathetic senior developer conducting a code review. Your goal is to transform harsh or blunt feedback into constructive, educational guidance that helps developers grow.

**Context:**
- Developer appears to be at {experience_level} level
- Original comment severity: {severity}
- Tone guidance: {tone_instruction}

**Original harsh comment:** "{original_comment}"

**Code being reviewed:**
```python
{code_snippet}
```

Please provide a response in EXACTLY this format:

POSITIVE_REPHRASING: [Write a gentle, encouraging version of the feedback that acknowledges what's working well and suggests improvement. Start with something positive.]

WHY_EXPLANATION: [Explain clearly WHY this improvement matters - focus on principles like performance, readability, maintainability, or Python best practices. Make it educational.]

CODE_IMPROVEMENT: [Provide a concrete, working code example that demonstrates the recommended improvement. Show the actual improved code.]

Remember:
- Start with encouragement or acknowledgment
- Explain the underlying principle, not just what to change
- Provide concrete, implementable solutions
- Keep the tone {severity} → supportive transformation"""
        
        messages = [
            {
                "role": "system", 
                "content": "You are an empathetic senior developer who transforms harsh code review feedback into constructive, educational guidance. Always be encouraging while maintaining technical accuracy."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        response_content = self.make_groq_request(messages, max_tokens=600, temperature=0.7)
        
        # Parse the structured response
        parsed_response = self.parse_groq_response(response_content)
        parsed_response["severity"] = severity
        parsed_response["experience_level"] = experience_level
        
        return parsed_response
    
    def parse_groq_response(self, content: str) -> Dict[str, str]:
        """Parse the structured response from Groq"""
        try:
            # Extract sections using regex
            positive_match = re.search(r'POSITIVE_REPHRASING:\s*(.*?)(?=WHY_EXPLANATION:|$)', content, re.DOTALL)
            why_match = re.search(r'WHY_EXPLANATION:\s*(.*?)(?=CODE_IMPROVEMENT:|$)', content, re.DOTALL)
            code_match = re.search(r'CODE_IMPROVEMENT:\s*(.*?)$', content, re.DOTALL)
            
            return {
                "positive_rephrasing": positive_match.group(1).strip() if positive_match else "Great work! Let's explore some improvements.",
                "why_explanation": why_match.group(1).strip() if why_match else "This will help improve code quality.",
                "code_improvement": code_match.group(1).strip() if code_match else "# Improved code here"
            }
        except Exception as e:
            print(f"Error parsing response: {e}")
            return {
                "positive_rephrasing": "Great start on this code! Let's look at some ways to enhance it.",
                "why_explanation": "These improvements will make your code more efficient and maintainable.",
                "code_improvement": "# See specific improvements in the detailed feedback"
            }
    
    def generate_holistic_summary(self, feedback_items: List[Dict], code_snippet: str) -> str:
        """Generate an encouraging summary using Groq"""
        
        experience_level = self.detect_experience_level(code_snippet)
        feedback_count = len(feedback_items)
        severity_levels = [item.get("severity", "neutral") for item in feedback_items]
        
        harsh_count = sum(1 for s in severity_levels if s == "harsh")
        
        prompt = f"""Write an encouraging 2-3 sentence summary for a code review with these details:

- Developer level: {experience_level}
- Number of feedback items: {feedback_count}
- Harsh comments transformed: {harsh_count}
- Code reviewed: Python function

The summary should:
1. Acknowledge the developer's effort and current skill
2. Highlight the positive aspects of their learning journey
3. Encourage continued growth with enthusiasm
4. Be warm, genuine, and mentor-like

Write a summary that feels personal and encouraging, not generic."""
        
        messages = [
            {
                "role": "system", 
                "content": "You are a supportive coding mentor writing an encouraging summary. Be warm, specific, and genuinely encouraging."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        summary = self.make_groq_request(messages, max_tokens=200, temperature=0.8)
        
        # Fallback if API fails
        if "Error" in summary or len(summary.strip()) < 20:
            fallback_summaries = {
                "beginner": f"Excellent work tackling this problem! These {feedback_count} suggestions will help you develop strong coding habits early in your journey. You're asking the right questions and thinking through the logic well - that's exactly how great developers grow!",
                "intermediate": f"Solid implementation! These {feedback_count} refinements focus on Python best practices that will make your code more professional. You clearly understand the fundamentals - now we're polishing the details that separate good code from great code."
            }
            summary = fallback_summaries.get(experience_level, fallback_summaries["beginner"])
        
        return summary.strip()
    
    def process_review(self, input_data: Dict) -> str:
        """Main method to process the code review and generate markdown report"""
        
        code_snippet = input_data["code_snippet"]
        review_comments = input_data["review_comments"]
        
        # Header with code context
        markdown_sections = [
            "# 🤝 Empathetic Code Review Report",
            "",
            "**Original Code:**",
            "```python",
            code_snippet,
            "```",
            ""
        ]
        
        feedback_items = []
        
        # Process each comment with progress indication
        print(f"Processing {len(review_comments)} comments with Groq AI...")
        
        for i, comment in enumerate(review_comments, 1):
            print(f"  ⚡ Processing comment {i}/{len(review_comments)}...")
            
            feedback = self.generate_empathetic_feedback(code_snippet, comment)
            feedback_items.append(feedback)
            
            # Generate resources
            resources = self.get_relevant_resources(comment)
            
            # Create section with enhanced formatting
            severity_emoji = {"harsh": "🤗", "moderate": "💪", "neutral": "✨"}
            emoji = severity_emoji.get(feedback.get("severity", "neutral"), "✨")
            
            section = f"""---

### {emoji} Analysis of Comment {i}: "{comment}"

**🌟 Positive Rephrasing:** {feedback['positive_rephrasing']}

**🧠 The 'Why':** {feedback['why_explanation']}

**💡 Suggested Improvement:**
```python
{feedback['code_improvement']}
```"""
            
            if resources:
                section += "\n\n**📚 Helpful Resources:**\n"
                for resource in resources:
                    # Create nice titles from URLs
                    title = resource.split('/')[-1].replace('-', ' ').replace('.html', '').title()
                    if 'pep8' in resource:
                        title = "PEP 8 Style Guide"
                    elif 'realpython' in resource:
                        title = "Real Python Tutorial"
                    elif 'docs.python.org' in resource:
                        title = "Official Python Documentation"
                    
                    section += f"- [{title}]({resource})\n"
            
            markdown_sections.append(section)
        
        # Generate and add holistic summary
        print("  🎯 Generating encouraging summary...")
        summary = self.generate_holistic_summary(feedback_items, code_snippet)
        
        markdown_sections.extend([
            "\n---\n",
            "## 🎯 Overall Summary",
            "",
            summary,
            "",
            "---",
            "",
            "*Remember: Every expert was once a beginner. These suggestions are stepping stones to writing even more amazing code! 🚀*",
            "",
            f"*Generated with ❤️ by Empathetic Code Reviewer using Groq AI*"
        ])
        
        return '\n'.join(markdown_sections)

# Quick setup and test functions
def setup_groq_reviewer():
    """Quick setup function for the notebook"""
    print("🚀 Setting up Empathetic Code Reviewer with Groq")
    print("=" * 50)
    
    # Get API key
    api_key = input("Enter your Groq API key (get one free at https://console.groq.com): ")
    
    if not api_key:
        print("❌ No API key provided. You can still use the fallback version.")
        return None
    
    reviewer = EmpathethicCodeReviewer(api_key)
    print("✅ Groq API configured successfully!")
    return reviewer

def run_demo_test(reviewer=None):
    """Run the demo with test data"""
    if not reviewer:
        print("⚠️ No reviewer provided, creating with demo key...")
        reviewer = EmpathethicCodeReviewer("demo-key")
    
    # Test data from problem statement
    test_input = {
        "code_snippet": "def get_active_users(users):\n    results = []\n    for u in users:\n        if u.is_active == True and u.profile_complete == True:\n            results.append(u)\n    return results",
        "review_comments": [
            "This is inefficient. Don't loop twice conceptually.",
            "Variable 'u' is a bad name.",
            "Boolean comparison '== True' is redundant."
        ]
    }
    
    print("\n🎯 Running Empathetic Code Review...")
    print("=" * 50)
    
    result = reviewer.process_review(test_input)
    
    print("\n📄 Generated Review:")
    print("=" * 50)
    print(result)
    
    # Save to file
    with open("empathetic_review.md", "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\n💾 Report saved to 'empathetic_review.md'")
    
    return result

# Interactive demo function
def interactive_demo():
    """Interactive demo for live presentation"""
    print("🎭 Interactive Empathetic Code Reviewer Demo")
    print("=" * 50)
    
    reviewer = setup_groq_reviewer()
    if not reviewer:
        return
    
    # Get custom input
    print("\n📝 Enter your code and harsh comments:")
    code = input("Code snippet (or press Enter for default): ").strip()
    if not code:
        code = "def get_active_users(users):\n    results = []\n    for u in users:\n        if u.is_active == True and u.profile_complete == True:\n            results.append(u)\n    return results"
    
    comments_str = input("Harsh comments (comma-separated): ").strip()
    if not comments_str:
        comments_str = "This is terrible code,Variable names are awful,This is completely wrong"
    
    comments = [c.strip() for c in comments_str.split(',')]
    
    input_data = {
        "code_snippet": code,
        "review_comments": comments
    }
    
    result = reviewer.process_review(input_data)
    print("\n" + "="*60)
    print("✨ EMPATHETIC TRANSFORMATION COMPLETE!")
    print("="*60)
    print(result)

# Main execution
if __name__ == "__main__":
    # For quick testing
    reviewer = setup_groq_reviewer()
    if reviewer:
        run_demo_test(reviewer)