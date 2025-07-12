import os
import logging
import uuid
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
CORS(app)

# In-memory storage for interview sessions
interview_sessions = {}

# Expanded question pools for different job roles
INTERVIEW_QUESTIONS = {
    "software_engineer": [
        "Tell me about yourself and your experience in software development.",
        "What programming languages are you most comfortable with and why?",
        "Describe a challenging technical problem you solved recently.",
        "How do you approach debugging a complex issue?",
        "What's your experience with version control systems like Git?",
        "Explain the difference between SQL and NoSQL databases and when you'd use each.",
        "How do you ensure code quality in your projects?",
        "Describe your experience with agile development methodologies.",
        "What's your approach to testing and test-driven development?",
        "How do you stay updated with new technologies and programming trends?",
        "Explain a time when you had to optimize code for better performance.",
        "What's your experience with cloud platforms like AWS or Azure?",
        "How do you handle code reviews and collaboration with other developers?",
        "Describe a project where you had to learn a new technology quickly.",
        "What's your experience with API design and development?"
    ],
    "data_scientist": [
        "Tell me about your background in data science and analytics.",
        "What machine learning algorithms are you most familiar with?",
        "Describe a data analysis project you've worked on.",
        "How do you handle missing or dirty data in your analysis?",
        "What tools and programming languages do you use for data science?",
        "Explain the difference between supervised and unsupervised learning.",
        "How do you validate the accuracy of your machine learning models?",
        "Describe your experience with data visualization tools.",
        "What's your approach to feature engineering and selection?",
        "How do you communicate complex data insights to non-technical stakeholders?",
        "Explain a time when your model didn't perform as expected and how you fixed it.",
        "What's your experience with big data technologies like Hadoop or Spark?",
        "How do you ensure data privacy and ethical considerations in your work?",
        "Describe a project where you used deep learning techniques.",
        "What's your approach to A/B testing and experimental design?"
    ],
    "product_manager": [
        "Tell me about your experience in product management.",
        "How do you prioritize features in a product roadmap?",
        "Describe a time when you had to make a difficult product decision.",
        "How do you gather and analyze user feedback?",
        "What metrics do you use to measure product success?",
        "Explain how you would launch a new product feature.",
        "How do you work with engineering teams to deliver products?",
        "Describe your experience with user research and testing.",
        "What's your approach to competitive analysis?",
        "How do you handle stakeholder disagreements about product direction?",
        "Explain a time when you had to pivot a product strategy.",
        "What's your experience with product analytics and data-driven decisions?",
        "How do you balance user needs with business requirements?",
        "Describe a product failure you learned from.",
        "What's your approach to market research and validation?"
    ],
    "marketing_manager": [
        "Tell me about your marketing experience and background.",
        "How do you develop and execute marketing campaigns?",
        "Describe a successful marketing campaign you've managed.",
        "How do you measure the effectiveness of marketing efforts?",
        "What digital marketing channels have you worked with?",
        "Explain your approach to content marketing and SEO.",
        "How do you determine the right marketing budget allocation?",
        "Describe your experience with social media marketing.",
        "What's your approach to email marketing and automation?",
        "How do you identify and target your ideal customer personas?",
        "Explain a time when a marketing campaign didn't meet expectations.",
        "What's your experience with marketing analytics and attribution?",
        "How do you collaborate with sales teams to generate leads?",
        "Describe your approach to brand management and positioning.",
        "What's your experience with paid advertising platforms like Google Ads or Facebook?"
    ],
    "sales_representative": [
        "Tell me about your sales experience and approach.",
        "How do you handle objections from potential customers?",
        "Describe your most successful sales achievement.",
        "How do you build and maintain client relationships?",
        "What CRM tools and sales methodologies are you familiar with?",
        "Explain your approach to prospecting and lead generation.",
        "How do you qualify leads and identify decision-makers?",
        "Describe a time when you lost a big deal and what you learned.",
        "What's your process for following up with potential clients?",
        "How do you handle price objections and negotiations?",
        "Explain your approach to consultative selling.",
        "What's your experience with sales forecasting and pipeline management?",
        "How do you stay motivated during challenging sales periods?",
        "Describe how you research prospects before making contact.",
        "What's your approach to closing deals and asking for the sale?"
    ]
}

# Number of questions to select for each interview
QUESTIONS_PER_INTERVIEW = 5

def get_random_questions(role):
    """Get random questions for the specified role"""
    if role not in INTERVIEW_QUESTIONS:
        role = "software_engineer"  # Default fallback
    
    available_questions = INTERVIEW_QUESTIONS[role]
    
    # If we have fewer questions than needed, return all
    if len(available_questions) <= QUESTIONS_PER_INTERVIEW:
        return available_questions.copy()
    
    # Randomly select questions
    return random.sample(available_questions, QUESTIONS_PER_INTERVIEW)

# Enhanced evaluation system with detailed feedback
def evaluate_answer(question, answer, role):
    """Enhanced evaluation that provides specific feedback and identifies issues"""
    if not answer.strip():
        return {
            "score": 1,
            "feedback": "No answer provided. Please provide a complete response to the question.",
            "is_satisfactory": False,
            "specific_issues": ["No response given"],
            "improvement_suggestions": ["Please answer the question with specific examples and details"]
        }
    
    # Role-specific evaluation criteria
    role_criteria = {
        "software_engineer": {
            "keywords": ["code", "programming", "development", "algorithm", "bug", "debug", "git", "version", "software", "technical", "framework", "database", "api"],
            "required_concepts": ["technical experience", "problem-solving", "tools/technologies"],
            "min_words": 20
        },
        "data_scientist": {
            "keywords": ["data", "analysis", "machine learning", "statistics", "python", "model", "dataset", "visualization", "analytics", "regression", "classification"],
            "required_concepts": ["data analysis", "statistical methods", "tools/languages"],
            "min_words": 20
        },
        "product_manager": {
            "keywords": ["product", "roadmap", "feature", "user", "customer", "metrics", "stakeholder", "requirement", "priority", "market"],
            "required_concepts": ["product strategy", "user focus", "decision-making"],
            "min_words": 20
        },
        "marketing_manager": {
            "keywords": ["marketing", "campaign", "brand", "customer", "digital", "social media", "analytics", "roi", "target", "strategy"],
            "required_concepts": ["marketing strategy", "campaign experience", "measurement"],
            "min_words": 20
        },
        "sales_representative": {
            "keywords": ["sales", "customer", "client", "relationship", "revenue", "target", "crm", "negotiation", "closing", "pipeline"],
            "required_concepts": ["sales experience", "customer relationships", "results/achievements"],
            "min_words": 20
        }
    }
    
    criteria = role_criteria.get(role, role_criteria["software_engineer"])
    answer_lower = answer.lower()
    word_count = len(answer.split())
    
    # Check for keyword relevance
    keyword_matches = sum(1 for keyword in criteria["keywords"] if keyword in answer_lower)
    keyword_score = min(4, keyword_matches)
    
    # Check answer length
    length_score = min(3, word_count / 10)
    
    # Check for specific examples
    example_indicators = ["example", "project", "experience", "worked on", "implemented", "developed", "managed", "led"]
    has_examples = any(indicator in answer_lower for indicator in example_indicators)
    example_score = 2 if has_examples else 0
    
    # Calculate total score
    total_score = keyword_score + length_score + example_score + 1  # Base score of 1
    final_score = min(10, max(1, total_score))
    
    # Determine if answer is satisfactory
    is_satisfactory = final_score >= 5 and word_count >= criteria["min_words"]
    
    # Generate specific feedback
    issues = []
    suggestions = []
    
    if word_count < criteria["min_words"]:
        issues.append("Answer is too brief")
        suggestions.append("Provide more detailed explanations and examples")
    
    if keyword_matches < 2:
        issues.append(f"Missing relevant {role.replace('_', ' ')} terminology")
        suggestions.append(f"Include specific {role.replace('_', ' ')} concepts and technologies")
    
    if not has_examples:
        issues.append("No specific examples provided")
        suggestions.append("Share concrete examples from your experience")
    
    # Generate contextual feedback
    if final_score >= 8:
        feedback = "Excellent answer! You provided relevant details and demonstrated strong experience."
    elif final_score >= 6:
        feedback = "Good answer with relevant information. " + " ".join(suggestions[:1]) if suggestions else "Consider adding more specific examples."
    elif final_score >= 4:
        feedback = "Your answer addresses the question but needs improvement. " + " ".join(suggestions[:2])
    else:
        feedback = "This answer needs significant improvement. " + " ".join(suggestions)
    
    return {
        "score": round(final_score, 1),
        "feedback": feedback,
        "is_satisfactory": is_satisfactory,
        "specific_issues": issues,
        "improvement_suggestions": suggestions
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    try:
        data = request.get_json()
        role = data.get('role')
        
        if not role or role not in INTERVIEW_QUESTIONS:
            return jsonify({"error": "Invalid role selected"}), 400
        
        session_id = str(uuid.uuid4())
        random_questions = get_random_questions(role)
        
        interview_sessions[session_id] = {
            "role": role,
            "questions": random_questions,
            "current_question": 0,
            "answers": [],
            "scores": [],
            "started_at": datetime.now().isoformat(),
            "completed": False
        }
        
        return jsonify({
            "session_id": session_id,
            "role": role,
            "first_question": random_questions[0],
            "total_questions": len(random_questions)
        })
    
    except Exception as e:
        logging.error(f"Error starting interview: {str(e)}")
        return jsonify({"error": "Failed to start interview"}), 500

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer and get the next question"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answer = data.get('answer', '').strip()
        
        if not session_id or session_id not in interview_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = interview_sessions[session_id]
        
        if session["completed"]:
            return jsonify({"error": "Interview already completed"}), 400
        
        current_q_index = session["current_question"]
        current_question = session["questions"][current_q_index]
        
        # Evaluate the answer
        evaluation = evaluate_answer(current_question, answer, session["role"])
        
        response = {
            "question_completed": False,
            "feedback": evaluation["feedback"],
            "score": evaluation["score"],
            "is_satisfactory": evaluation["is_satisfactory"],
            "specific_issues": evaluation["specific_issues"],
            "improvement_suggestions": evaluation["improvement_suggestions"]
        }
        
        # If answer is satisfactory, proceed to next question
        if evaluation["is_satisfactory"]:
            # Store answer and score
            session["answers"].append({
                "question": current_question,
                "answer": answer,
                "score": evaluation["score"],
                "feedback": evaluation["feedback"]
            })
            session["scores"].append(evaluation["score"])
            
            # Move to next question
            session["current_question"] += 1
            response["question_completed"] = True
            
            # Check if interview is complete
            if session["current_question"] >= len(session["questions"]):
                session["completed"] = True
                session["completed_at"] = datetime.now().isoformat()
                
                # Calculate final score
                avg_score = sum(session["scores"]) / len(session["scores"])
                
                response.update({
                    "interview_complete": True,
                    "final_score": round(avg_score, 1),
                    "total_questions": len(session["questions"])
                })
            else:
                # Get next question
                next_question = session["questions"][session["current_question"]]
                response.update({
                    "interview_complete": False,
                    "next_question": next_question,
                    "question_number": session["current_question"] + 1,
                    "total_questions": len(session["questions"])
                })
        else:
            # Answer is not satisfactory, ask same question again
            response.update({
                "interview_complete": False,
                "repeat_question": True,
                "current_question": current_question,
                "question_number": session["current_question"] + 1,
                "total_questions": len(session["questions"]),
                "retry_message": "Let me ask the same question again. Please provide a more detailed answer."
            })
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error submitting answer: {str(e)}")
        return jsonify({"error": "Failed to submit answer"}), 500

@app.route('/api/cancel-interview', methods=['POST'])
def cancel_interview():
    """Cancel an ongoing interview session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in interview_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        # Mark session as cancelled
        session = interview_sessions[session_id]
        session["cancelled"] = True
        session["cancelled_at"] = datetime.now().isoformat()
        
        # Remove from active sessions
        del interview_sessions[session_id]
        
        return jsonify({"message": "Interview cancelled successfully"})
    
    except Exception as e:
        logging.error(f"Error cancelling interview: {str(e)}")
        return jsonify({"error": "Failed to cancel interview"}), 500

@app.route('/api/get-summary', methods=['POST'])
def get_summary():
    """Get interview summary and detailed feedback"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in interview_sessions:
            return jsonify({"error": "Invalid session"}), 400
        
        session = interview_sessions[session_id]
        
        if not session["completed"]:
            return jsonify({"error": "Interview not completed"}), 400
        
        avg_score = sum(session["scores"]) / len(session["scores"])
        
        # Generate overall feedback
        if avg_score >= 8:
            overall_feedback = "Outstanding performance! You demonstrated excellent knowledge and communication skills throughout the interview."
        elif avg_score >= 6:
            overall_feedback = "Good performance overall. You showed relevant experience and knowledge with room for improvement in some areas."
        elif avg_score >= 4:
            overall_feedback = "Adequate performance. Focus on providing more detailed examples and demonstrating deeper knowledge in future interviews."
        else:
            overall_feedback = "There's significant room for improvement. Consider practicing more specific examples and developing stronger responses."
        
        return jsonify({
            "role": session["role"],
            "final_score": round(avg_score, 1),
            "total_questions": len(session["questions"]),
            "overall_feedback": overall_feedback,
            "detailed_results": session["answers"],
            "duration": session.get("completed_at", ""),
            "started_at": session["started_at"]
        })
    
    except Exception as e:
        logging.error(f"Error getting summary: {str(e)}")
        return jsonify({"error": "Failed to get summary"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
