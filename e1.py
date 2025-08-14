# Empathetic Code Reviewer using Groq API
# Fast, free, and powerful AI for hackathons!

import json
import requests
from typing import Dict, List
import re
import time


class EmpatheticCodeReviewer:
    def __init__(self):
        """Initialize the empathetic code reviewer with embedded Groq API key"""
        self.groq_api_key = "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"  # Embedded API key
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
        harsh_indicators = ['bad', 'wrong', 'terrible', 'awful', 'stupid', 'inefficient', 'horrible', 'trash']
        moderate_indicators = ['could be better', 'consider', 'might want', 'should', 'redundant']
        
        comment_lower = comment.lower()
        if any(i in comment_lower for i in harsh_indicators):
            return "harsh"
        elif any(i in comment_lower for i in moderate_indicators):
            return "moderate"
        else:
            return "neutral"
    
    def get_relevant_resources(self, comment: str, code_language: str = "python") -> List[str]:
        resources = []
        comment_lower = comment.lower()
        
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
        beginner_patterns = ['== True', '== False', 'results = []', 'append(', 'range(len(']
        intermediate_patterns = ['comprehension', 'lambda', 'yield', 'enumerate', 'zip']
        
        code_lower = code_snippet.lower()
        beginner_score = sum(1 for p in beginner_patterns if p in code_lower)
        intermediate_score = sum(1 for p in intermediate_patterns if p in code_lower)
        
        if beginner_score >= 2 and intermediate_score == 0:
            return "beginner"
        elif intermediate_score > 0:
            return "intermediate"
        else:
            return "beginner"
    
    def generate_empathetic_feedback(self, code_snippet: str, original_comment: str) -> Dict[str, str]:
        severity = self.analyze_comment_severity(original_comment)
        experience_level = self.detect_experience_level(code_snippet)
        
        tone_instructions = {
            "harsh": {
                "beginner": "Be extra gentle, encouraging, and patient.",
                "intermediate": "Be supportive and constructive."
            },
            "moderate": {
                "beginner": "Be encouraging and educational.",
                "intermediate": "Be professional and helpful."
            },
            "neutral": {
                "beginner": "Be friendly and educational.",
                "intermediate": "Be professional and direct."
            }
        }
        
        tone_instruction = tone_instructions[severity][experience_level]
        
        prompt = f"""You are an experienced, empathetic senior developer...
**Original harsh comment:** "{original_comment}"
**Code being reviewed:**
```python
{code_snippet}
```"""
        
        messages = [
            {"role": "system", "content": "You are an empathetic senior developer."},
            {"role": "user", "content": prompt}
        ]
        
        response_content = self.make_groq_request(messages, max_tokens=600, temperature=0.7)
        parsed_response = self.parse_groq_response(response_content)
        parsed_response["severity"] = severity
        parsed_response["experience_level"] = experience_level
        return parsed_response
    
    def parse_groq_response(self, content: str) -> Dict[str, str]:
        try:
            positive_match = re.search(r'POSITIVE_REPHRASING:\s*(.*?)(?=WHY_EXPLANATION:|$)', content, re.DOTALL)
            why_match = re.search(r'WHY_EXPLANATION:\s*(.*?)(?=CODE_IMPROVEMENT:|$)', content, re.DOTALL)
            code_match = re.search(r'CODE_IMPROVEMENT:\s*(.*?)$', content, re.DOTALL)
            
            return {
                "positive_rephrasing": positive_match.group(1).strip() if positive_match else "",
                "why_explanation": why_match.group(1).strip() if why_match else "",
                "code_improvement": code_match.group(1).strip() if code_match else ""
            }
        except Exception:
            return {
                "positive_rephrasing": "",
                "why_explanation": "",
                "code_improvement": ""
            }
    
    def generate_holistic_summary(self, feedback_items: List[Dict], code_snippet: str) -> str:
        experience_level = self.detect_experience_level(code_snippet)
        feedback_count = len(feedback_items)
        harsh_count = sum(1 for f in feedback_items if f.get("severity") == "harsh")
        
        prompt = f"""Write an encouraging summary..."""
        
        messages = [
            {"role": "system", "content": "You are a supportive coding mentor."},
            {"role": "user", "content": prompt}
        ]
        
        summary = self.make_groq_request(messages, max_tokens=200, temperature=0.8)
        return summary.strip()
    
    def process_review(self, input_data: Dict) -> str:
        code_snippet = input_data["code_snippet"]
        review_comments = input_data["review_comments"]
        
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
        print(f"Processing {len(review_comments)} comments with Groq AI...")
        
        for i, comment in enumerate(review_comments, 1):
            print(f"  ⚡ Processing comment {i}/{len(review_comments)}...")
            feedback = self.generate_empathetic_feedback(code_snippet, comment)
            feedback_items.append(feedback)
            
            resources = self.get_relevant_resources(comment)
            severity_emoji = {"harsh": "🤗", "moderate": "💪", "neutral": "✨"}
            emoji = severity_emoji.get(feedback.get("severity"), "✨")
            
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
                    section += f"- [{resource}]({resource})\n"
            
            markdown_sections.append(section)
        
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
            "*Remember: Every expert was once a beginner.*",
            "",
            f"*Generated with ❤️ by Empathetic Code Reviewer using Groq AI*"
        ])
        
        return '\n'.join(markdown_sections)


def run_demo_test():
    reviewer = EmpatheticCodeReviewer()
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
    with open("empathetic_review.md", "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\n💾 Report saved to 'empathetic_review.md'")
    return result


if __name__ == "__main__":
    run_demo_test()
