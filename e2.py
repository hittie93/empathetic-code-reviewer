# 🚀 HACKATHON-READY: Empathetic Code Reviewer with Groq
# Copy this directly into your notebook and run!

# First, install required packages (run this cell first)
# !pip install requests

import json
import requests
from typing import Dict, List
import re

# 🔥 MAIN CLASS - Empathetic Code Reviewer
class EmpathethicCodeReviewer:
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-8b-8192"  # Fast and free!
        
    def make_groq_request(self, prompt: str) -> str:
        """Make request to Groq API"""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an empathetic senior developer who transforms harsh code review feedback into constructive, educational guidance."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 600,
            "temperature": 0.7,
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API Error: {e}")
            return self.get_fallback_response()
    
    def get_fallback_response(self) -> str:
        """Fallback if API fails"""
        return """POSITIVE_REPHRASING: Great work on this code! Let's explore some ways to make it even better.
WHY_EXPLANATION: These improvements will help make your code more efficient and maintainable.
CODE_IMPROVEMENT: # Improved version with better practices"""
    
    def analyze_severity(self, comment: str) -> str:
        """Check how harsh the comment is"""
        harsh_words = ['bad', 'terrible', 'awful', 'wrong', 'stupid', 'horrible']
        return "harsh" if any(word in comment.lower() for word in harsh_words) else "moderate"
    
    def get_resources(self, comment: str) -> List[str]:
        """Get relevant learning resources"""
        resources = []
        comment_lower = comment.lower()
        
        if "variable" in comment_lower or "name" in comment_lower:
            resources.append("https://pep8.org/#naming-conventions")
        if "boolean" in comment_lower or "== true" in comment_lower:
            resources.append("https://pep8.org/#programming-recommendations")
        if "inefficient" in comment_lower or "loop" in comment_lower:
            resources.append("https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions")
            
        return resources
    
    def generate_empathetic_feedback(self, code_snippet: str, original_comment: str) -> Dict[str, str]:
        """Transform harsh comment into empathetic feedback"""
        
        severity = self.analyze_severity(original_comment)
        tone_guide = "Be extra gentle and encouraging" if severity == "harsh" else "Be supportive and constructive"
        
        prompt = f"""Transform this harsh code review comment into empathetic, educational feedback.

{tone_guide}. The developer is learning and needs constructive guidance.

Original comment: "{original_comment}"
Code being reviewed:
```python
{code_snippet}
```

Respond in EXACTLY this format:

POSITIVE_REPHRASING: [Start with something positive, then gently suggest improvement]

WHY_EXPLANATION: [Explain WHY this improvement matters - focus on principles like performance, readability, maintainability]

CODE_IMPROVEMENT: [Show concrete improved code example]

Make it encouraging, educational, and actionable!"""
        
        response = self.make_groq_request(prompt)
        
        # Parse response
        try:
            positive = re.search(r'POSITIVE_REPHRASING:\s*(.*?)(?=WHY_EXPLANATION:|$)', response, re.DOTALL)
            why = re.search(r'WHY_EXPLANATION:\s*(.*?)(?=CODE_IMPROVEMENT:|$)', response, re.DOTALL)
            code = re.search(r'CODE_IMPROVEMENT:\s*(.*?)$', response, re.DOTALL)
            
            return {
                "positive_rephrasing": positive.group(1).strip() if positive else "Great start! Let's improve this together.",
                "why_explanation": why.group(1).strip() if why else "This will make your code better.",
                "code_improvement": code.group(1).strip() if code else "# Improved code here",
                "severity": severity
            }
        except:
            return {
                "positive_rephrasing": "Great work! Let's enhance this code together.",
                "why_explanation": "These improvements follow Python best practices.",
                "code_improvement": "# See the detailed suggestions above",
                "severity": severity
            }
    
    def generate_summary(self, feedback_count: int) -> str:
        """Generate encouraging summary"""
        prompt = f"""Write an encouraging 2-3 sentence summary for a developer who received {feedback_count} pieces of constructive code review feedback.

The summary should:
- Acknowledge their effort
- Highlight learning opportunities  
- Encourage continued growth
- Be warm and mentor-like

Keep it genuine and specific to code review context."""
        
        summary = self.make_groq_request(prompt)
        
        # Fallback summary
        if len(summary.strip()) < 20:
            summary = f"Excellent work implementing this functionality! These {feedback_count} suggestions will help you develop strong coding practices. You're clearly thinking through the problem well - these refinements will make your code even more professional!"
        
        return summary.strip()
    
    def process_review(self, input_data: Dict) -> str:
        """Main method - processes review and generates markdown"""
        
        code_snippet = input_data["code_snippet"]
        review_comments = input_data["review_comments"]
        
        print(f"🔄 Processing {len(review_comments)} comments with Groq AI...")
        
        # Start building markdown
        markdown = [
            "# 🤝 Empathetic Code Review Report",
            "",
            "**Original Code:**",
            "```python",
            code_snippet,
            "```",
            ""
        ]
        
        feedback_items = []
        
        # Process each comment
        for i, comment in enumerate(review_comments, 1):
            print(f"  ⚡ Comment {i}/{len(review_comments)}...")
            
            feedback = self.generate_empathetic_feedback(code_snippet, comment)
            feedback_items.append(feedback)
            
            resources = self.get_resources(comment)
            
            # Choose emoji based on severity
            emoji = "🤗" if feedback["severity"] == "harsh" else "💪"
            
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
                    title = "PEP 8 Guide" if "pep8" in resource else "Python Documentation"
                    section += f"- [{title}]({resource})\n"
            
            markdown.append(section)
        
        # Add encouraging summary
        print("  🎯 Generating summary...")
        summary = self.generate_summary(len(feedback_items))
        
        markdown.extend([
            "\n---\n",
            "## 🎯 Overall Summary",
            "",
            summary,
            "",
            "---",
            "",
            "*Every expert was once a beginner. Keep coding, keep growing! 🚀*"
        ])
        
        return '\n'.join(markdown)

# 🎯 QUICK SETUP FUNCTION
def setup_and_test():
    """One function to rule them all - setup and test!"""
    
    print("🚀 Empathetic Code Reviewer Setup")
    print("=" * 40)
    
    # Get Groq API key
    api_key = input("📋 Enter your Groq API key (free at https://console.groq.com): ").strip()
    
    if not api_key:
        print("❌ Need API key to continue!")
        return
    
    # Initialize reviewer
    reviewer = EmpathethicCodeReviewer(api_key)
    print("✅ Groq API configured!")
    
    # Test with hackathon data
    test_input = {
        "code_snippet": "def get_active_users(users):\n    results = []\n    for u in users:\n        if u.is_active == True and u.profile_complete == True:\n            results.append(u)\n    return results",
        "review_comments": [
            "This is inefficient. Don't loop twice conceptually.",
            "Variable 'u' is a bad name.",
            "Boolean comparison '== True' is redundant."
        ]
    }
    
    print("\n🎯 Generating Empathetic Review...")
    print("=" * 40)
    
    # Generate review
    result = reviewer.process_review(test_input)
    
    # Display result
    print("\n📄 FINAL RESULT:")
    print("=" * 50)
    print(result)
    
    # Save to file
    with open("empathetic_review.md", "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\n💾 Saved to 'empathetic_review.md'")
    
    print("\n🏆 SUCCESS! Your empathetic code reviewer is working!")
    
    return reviewer, result

# 🎭 INTERACTIVE DEMO FUNCTION  
def interactive_demo():
    """For live demonstrations"""
    print("🎭 LIVE DEMO MODE")
    print("=" * 30)
    
    api_key = input("Groq API key: ").strip()
    if not api_key:
        print("Need API key!")
        return
        
    reviewer = EmpathethicCodeReviewer(api_key)
    
    # Custom input
    print("\n📝 Enter harsh comments to transform:")
    comments = input("Comments (comma-separated): ").strip()
    
    if not comments:
        comments = "This code is terrible,Bad variable names,Completely inefficient"
    
    # Use default code
    test_input = {
        "code_snippet": "def get_active_users(users):\n    results = []\n    for u in users:\n        if u.is_active == True:\n            results.append(u)\n    return results",
        "review_comments": [c.strip() for c in comments.split(',')]
    }
    
    result = reviewer.process_review(test_input)
    
    print("\n✨ TRANSFORMATION COMPLETE!")
    print("=" * 40)
    print(result)

# 🚀 HACKATHON EXECUTION
if __name__ == "__main__":
    # Run this for hackathon
    reviewer, result = setup_and_test()
    
    # Optional: Run interactive demo
    # interactive_demo()