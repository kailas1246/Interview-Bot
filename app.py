import os
import logging
import uuid
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

# Predefined questions for different job roles
INTERVIEW_QUESTIONS = {
    "software_engineer": [
        "Tell me about yourself and your experience in software development.",
        "What programming languages are you most comfortable with and why?",
        "Describe a challenging technical problem you solved recently.",
        "How do you approach debugging a complex issue?",
        "What's your experience with version control systems like Git?"
    ],
    "data_scientist": [
        "Tell me about your background in data science and analytics.",
        "What machine learning algorithms are you most familiar with?",
        "Describe a data analysis project you've worked on.",
        "How do you handle missing or dirty data in your analysis?",
        "What tools and programming languages do you use for data science?"
    ],
    "product_manager": [
        "Tell me about your experience in product management.",
        "How do you prioritize features in a product roadmap?",
        "Describe a time when you had to make a difficult product decision.",
        "How do you gather and analyze user feedback?",
        "What metrics do you use to measure product success?"
    ],
    "marketing_manager": [
        "Tell me about your marketing experience and background.",
        "How do you develop and execute marketing campaigns?",
        "Describe a successful marketing campaign you've managed.",
        "How do you measure the effectiveness of marketing efforts?",
        "What digital marketing channels have you worked with?"
    ],
    "sales_representative": [
        "Tell me about your sales experience and approach.",
        "How do you handle objections from potential customers?",
        "Describe your most successful sales achievement.",
        "How do you build and maintain client relationships?",
        "What CRM tools and sales methodologies are you familiar with?"
    ]
}

# Mock LLM responses for evaluation
def evaluate_answer(question, answer, role):
    """Mock LLM evaluation that provides intelligent responses"""
    if not answer.strip():
        return {
            "score": 2,
            "feedback": "Your answer was too brief. Try to provide more detailed responses that demonstrate your experience and knowledge."
        }
    
    # Simple keyword-based evaluation for different roles
    role_keywords = {
        "software_engineer": ["code", "programming", "development", "algorithm", "bug", "debug", "git", "version", "software", "technical"],
        "data_scientist": ["data", "analysis", "machine learning", "statistics", "python", "model", "dataset", "visualization", "analytics"],
        "product_manager": ["product", "roadmap", "feature", "user", "customer", "metrics", "stakeholder", "requirement"],
        "marketing_manager": ["marketing", "campaign", "brand", "customer", "digital", "social media", "analytics", "roi"],
        "sales_representative": ["sales", "customer", "client", "relationship", "revenue", "target", "crm", "negotiation"]
    }
    
    keywords = role_keywords.get(role, [])
    answer_lower = answer.lower()
    keyword_matches = sum(1 for keyword in keywords if keyword in answer_lower)
    
    # Score based on answer length and keyword relevance
    word_count = len(answer.split())
    base_score = min(10, max(3, (word_count / 10) + (keyword_matches * 2)))
    
    if base_score >= 8:
        feedback = "Excellent answer! You demonstrated strong knowledge and experience relevant to the role."
    elif base_score >= 6:
        feedback = "Good answer. You showed relevant experience, but could provide more specific examples."
    elif base_score >= 4:
        feedback = "Adequate answer. Consider providing more detailed examples and demonstrating deeper knowledge."
    else:
        feedback = "Your answer could be improved. Try to be more specific and provide concrete examples from your experience."
    
    return {
        "score": round(base_score, 1),
        "feedback": feedback
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
        interview_sessions[session_id] = {
            "role": role,
            "questions": INTERVIEW_QUESTIONS[role].copy(),
            "current_question": 0,
            "answers": [],
            "scores": [],
            "started_at": datetime.now().isoformat(),
            "completed": False
        }
        
        return jsonify({
            "session_id": session_id,
            "role": role,
            "first_question": INTERVIEW_QUESTIONS[role][0],
            "total_questions": len(INTERVIEW_QUESTIONS[role])
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
        
        response = {
            "question_completed": True,
            "feedback": evaluation["feedback"],
            "score": evaluation["score"]
        }
        
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
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error submitting answer: {str(e)}")
        return jsonify({"error": "Failed to submit answer"}), 500

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
