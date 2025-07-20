"""
Google Gemini service for generating NEET questions
"""
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Missing Gemini API key. Check your .env file.")
        
        # Configure Gemini with API Version
        genai.configure(
            api_key=self.api_key,
            client_options={"api_endpoint": "generativelanguage.googleapis.com"}
        )
        # Use the correct model
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_neet_questions(self, subject: str, topic: str = None, count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate NEET questions using Google Gemini"""
        
        # Create the prompt based on subject and parameters
        prompt = self._create_neet_prompt(subject, topic, count, difficulty)
        
        try:
            # Generate content using Gemini
            generation_config = {
                "temperature": 0.9,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            if not response.text:
                print("Empty response from Gemini")
                return self._get_fallback_questions(subject, count, difficulty)
            
            # Parse the response as JSON
            content = response.text.strip()
            print("Gemini Response:", content)  # Debug print
            
            try:
                questions_data = json.loads(content)
                questions = questions_data.get('questions', [])
                
                if not questions:
                    print("No questions in response")
                    return self._get_fallback_questions(subject, count, difficulty)
                
                return questions
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return self._get_fallback_questions(subject, count, difficulty)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_questions(subject, count, difficulty)
    
    def _create_neet_prompt(self, subject: str, topic: str, count: int, difficulty: str) -> str:
        """Create a detailed prompt for NEET question generation"""
        
        topic_filter = f" focusing specifically on {topic}" if topic else ""
        
        # Define NEET-specific guidelines for each subject
        subject_guidelines = {
            'Physics': {
                'focus_areas': 'mechanics, thermodynamics, electromagnetism, optics, modern physics, waves, oscillations',
                'question_types': 'numerical problems, conceptual questions, application-based scenarios',
                'key_concepts': 'laws of motion, energy conservation, electromagnetic induction, wave properties, atomic structure'
            },
            'Chemistry': {
                'focus_areas': 'organic chemistry, inorganic chemistry, physical chemistry, coordination compounds, biomolecules',
                'question_types': 'structure identification, reaction mechanisms, numerical calculations, periodic trends',
                'key_concepts': 'chemical bonding, thermodynamics, kinetics, equilibrium, organic reactions, periodic properties'
            },
            'Biology': {
                'focus_areas': 'cell biology, genetics, ecology, human physiology, plant physiology, biotechnology, evolution',
                'question_types': 'diagram-based questions, physiological processes, genetic problems, ecological concepts',
                'key_concepts': 'cell structure, inheritance patterns, ecosystem dynamics, organ systems, molecular biology'
            }
        }
        
        guidelines = subject_guidelines.get(subject, subject_guidelines['Biology'])
        
        prompt = f"""
Generate {count} high-quality NEET {subject} multiple choice questions{topic_filter}.

NEET Exam Standards:
- Each question must test deep conceptual understanding
- Include application-based scenarios from real life
- Questions should differentiate between students of different abilities
- Follow official NEET syllabus and pattern
- Avoid direct factual recall; focus on application and analysis

Subject-Specific Guidelines for {subject}:
- Focus Areas: {guidelines['focus_areas']}
- Question Types: {guidelines['question_types']}
- Key Concepts: {guidelines['key_concepts']}

Difficulty Level: {difficulty}
- Easy: Basic concept application, direct formula usage, simple calculations
- Medium: Multi-step reasoning, concept integration, moderate calculations
- Hard: Complex analysis, multiple concept integration, advanced problem-solving

Question Quality Requirements:
1. Clear, unambiguous question stem
2. Four distinct, plausible options
3. Only one clearly correct answer
4. Detailed explanations with reasoning
5. Use standard scientific terminology
6. Include units where applicable
7. Avoid trivial or overly complex calculations

Response format (STRICT JSON - no additional text):
{{
  "questions": [
    {{
      "question_text": "[Complete question with all necessary information]",
      "option_a": "[First option - clear and concise]",
      "option_b": "[Second option - plausible distractor]", 
      "option_c": "[Third option - plausible distractor]",
      "option_d": "[Fourth option - plausible distractor]",
      "correct_answer": "[A/B/C/D]",
      "explanation": "[Detailed explanation with scientific reasoning, formulas if applicable, and why other options are incorrect]",
      "difficulty": "{difficulty}",
      "topic": "{topic if topic else 'General'}"
    }}
  ]
}}

Generate exactly {count} questions for {subject}{topic_filter}.
Ensure variety in question types and concepts covered.
"""
        return prompt
    
    def _get_fallback_questions(self, subject: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """High-quality fallback questions if API fails"""
        # Using the same fallback questions as before for consistency
        fallback_questions = {
            "Physics": [
                {
                    "question_text": "A particle moves in a straight line with constant acceleration. If it covers 20 m in the first 2 seconds and 60 m in the next 4 seconds, what is its acceleration?",
                    "option_a": "5 m/s²",
                    "option_b": "10 m/s²",
                    "option_c": "15 m/s²",
                    "option_d": "20 m/s²",
                    "correct_answer": "A",
                    "explanation": "Using s = ut + ½at². For first 2s: 20 = u(2) + ½a(4), so 20 = 2u + 2a. For total 6s: 80 = u(6) + ½a(36), so 80 = 6u + 18a. Solving: a = 5 m/s²",
                    "difficulty": difficulty,
                    "topic": "Kinematics"
                }
            ],
            "Chemistry": [
                {
                    "question_text": "Which orbital has the highest energy according to aufbau principle?",
                    "option_a": "3d",
                    "option_b": "4s",
                    "option_c": "4p",
                    "option_d": "4f",
                    "correct_answer": "D",
                    "explanation": "According to the aufbau principle, orbitals are filled in order of increasing energy. The order is: 1s < 2s < 2p < 3s < 3p < 4s < 3d < 4p < 5s < 4d < 5p < 6s < 4f. Therefore, 4f has the highest energy among the given options.",
                    "difficulty": difficulty,
                    "topic": "Atomic Structure"
                }
            ],
            "Biology": [
                {
                    "question_text": "Which of the following is NOT a function of the rough endoplasmic reticulum?",
                    "option_a": "Protein synthesis",
                    "option_b": "Lipid synthesis",
                    "option_c": "Protein folding",
                    "option_d": "Glycoprotein formation",
                    "correct_answer": "B",
                    "explanation": "Lipid synthesis is primarily carried out by the smooth endoplasmic reticulum (SER). The rough endoplasmic reticulum (RER) is mainly involved in protein synthesis, protein folding, and glycoprotein formation due to the presence of ribosomes on its surface.",
                    "difficulty": difficulty,
                    "topic": "Cell Biology"
                }
            ]
        }
        
        available_questions = fallback_questions.get(subject, fallback_questions.get("Biology", []))
        return [available_questions[i % len(available_questions)] for i in range(count)]
