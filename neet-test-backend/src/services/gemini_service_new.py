"""
Google Gemini service for generating NEET questions
"""
import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Missing Gemini API key. Check your .env file.")
        
        # Set up Gemini API endpoint
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def generate_neet_questions(self, subject: str, topic: str = None, count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate NEET questions using Google Gemini"""
        
        # Create the prompt based on subject and parameters
        prompt = self._create_neet_prompt(subject, topic, count, difficulty)
        
        try:
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048,
                    "topP": 1,
                    "topK": 40
                }
            }

            response = requests.post(self.url, headers=self.headers, json=data)
            result = response.json()
            print("Raw Gemini API Response:", result)

            try:
                # Extract text from response
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Extract JSON from markdown code block
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                else:
                    json_str = content.strip()
                
                print("Extracted JSON string:", json_str)
                
                # Parse JSON
                questions_data = json.loads(json_str)
                questions = questions_data.get('questions', [])
                
                if not questions:
                    print("No questions in response")
                    return self._get_fallback_questions(subject, count, difficulty)
                    
                return questions
            except Exception as e:
                print(f"Error parsing response: {e}")
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
