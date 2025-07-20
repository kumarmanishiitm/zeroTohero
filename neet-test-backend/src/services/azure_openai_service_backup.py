"""
Azure OpenAI service for generating NEET questions with enhanced LLM-first approach
"""
import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
import time
import random

# Load environment variables
load_dotenv()

class AzureOpenAIService:
    def __init__(self):
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.model_name = os.getenv('AZURE_OPENAI_MODEL_NAME')
        self.api_version = os.getenv('AZURE_OPENAI_VERSION')
        
        if not all([self.api_key, self.endpoint, self.model_name, self.api_version]):
            raise ValueError("Missing Azure OpenAI configuration. Check your .env file.")
    
    def generate_neet_questions(self, subject: str, topic: str = None, count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate NEET questions using Azure OpenAI"""
        
        # Create the prompt based on subject and parameters
        prompt = self._create_neet_prompt(subject, topic, count, difficulty)
        
        url = f"{self.endpoint}openai/deployments/{self.model_name}/chat/completions?api-version={self.api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert NEET (National Eligibility cum Entrance Test) question generator. Generate high-quality multiple choice questions for medical entrance preparation. Always respond with valid JSON format."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse the JSON response
            questions_data = json.loads(content)
            return questions_data.get('questions', [])
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return self._get_fallback_questions(subject, count, difficulty)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._get_fallback_questions(subject, count, difficulty)
        except Exception as e:
            print(f"Unexpected error: {e}")
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
                    "difficulty": difficulty
                },
                {
                    "question_text": "Two resistors of 4Ω and 6Ω are connected in parallel. The equivalent resistance is:",
                    "option_a": "2.4Ω",
                    "option_b": "5Ω",
                    "option_c": "10Ω",
                    "option_d": "24Ω",
                    "correct_answer": "A",
                    "explanation": "For parallel resistors: 1/R = 1/R₁ + 1/R₂ = 1/4 + 1/6 = (3+2)/12 = 5/12. Therefore R = 12/5 = 2.4Ω",
                    "difficulty": difficulty
                },
                {
                    "question_text": "A convex lens of focal length 20 cm forms an image at 60 cm from the lens. The object distance is:",
                    "option_a": "30 cm",
                    "option_b": "15 cm",
                    "option_c": "40 cm",
                    "option_d": "12 cm",
                    "correct_answer": "A",
                    "explanation": "Using lens formula: 1/f = 1/v - 1/u. Given f = 20 cm, v = 60 cm. So 1/20 = 1/60 - 1/u. Solving: 1/u = 1/60 - 1/20 = -1/30. Therefore u = 30 cm",
                    "difficulty": difficulty
                },
                {
                    "question_text": "The escape velocity from Earth's surface is approximately 11.2 km/s. The escape velocity from a planet with twice Earth's mass and half Earth's radius would be:",
                    "option_a": "22.4 km/s",
                    "option_b": "31.6 km/s",
                    "option_c": "15.8 km/s",
                    "option_d": "7.9 km/s",
                    "correct_answer": "B",
                    "explanation": "Escape velocity v = √(2GM/R). For the planet: v' = √(2G(2M)/(R/2)) = √(8GM/R) = 2√2 × √(2GM/R) = 2√2 × 11.2 ≈ 31.6 km/s",
                    "difficulty": difficulty
                }
            ],
            "Chemistry": [
                {
                    "question_text": "The IUPAC name of the compound CH₃-CH(CH₃)-CH₂-CH₂-OH is:",
                    "option_a": "3-methylbutanol",
                    "option_b": "3-methylbutan-1-ol",
                    "option_c": "2-methylbutan-4-ol",
                    "option_d": "isobutanol",
                    "correct_answer": "B",
                    "explanation": "The longest carbon chain has 4 carbons with -OH at position 1, making it butan-1-ol. The methyl branch is at position 3, so the name is 3-methylbutan-1-ol.",
                    "difficulty": difficulty
                },
                {
                    "question_text": "In the reaction 2SO₂ + O₂ ⇌ 2SO₃, if the equilibrium concentrations are [SO₂] = 0.2 M, [O₂] = 0.1 M, and [SO₃] = 0.4 M, the equilibrium constant Kc is:",
                    "option_a": "40",
                    "option_b": "400",
                    "option_c": "4",
                    "option_d": "0.025",
                    "correct_answer": "A",
                    "explanation": "Kc = [SO₃]²/([SO₂]² × [O₂]) = (0.4)²/((0.2)² × 0.1) = 0.16/(0.04 × 0.1) = 0.16/0.004 = 40",
                    "difficulty": difficulty
                },
                {
                    "question_text": "The electronic configuration of Fe³⁺ (Z = 26) is:",
                    "option_a": "[Ar] 3d⁵",
                    "option_b": "[Ar] 3d³",
                    "option_c": "[Ar] 4s² 3d³",
                    "option_d": "[Ar] 4s¹ 3d⁴",
                    "correct_answer": "A",
                    "explanation": "Fe has configuration [Ar] 4s² 3d⁶. Fe³⁺ loses 3 electrons (2 from 4s and 1 from 3d), giving [Ar] 3d⁵.",
                    "difficulty": difficulty
                },
                {
                    "question_text": "Which of the following exhibits maximum covalent character?",
                    "option_a": "NaCl",
                    "option_b": "AlCl₃",
                    "option_c": "MgCl₂",
                    "option_d": "CaCl₂",
                    "correct_answer": "B",
                    "explanation": "According to Fajan's rules, covalent character increases with smaller, highly charged cations. Al³⁺ is smallest and has highest charge density, making AlCl₃ most covalent.",
                    "difficulty": difficulty
                }
            ],
            "Biology": [
                {
                    "question_text": "In a population of 10,000 individuals, if the frequency of a recessive allele is 0.3, how many individuals are expected to be heterozygous (assuming Hardy-Weinberg equilibrium)?",
                    "option_a": "2100",
                    "option_b": "4200",
                    "option_c": "3000",
                    "option_d": "4900",
                    "correct_answer": "B",
                    "explanation": "If q = 0.3 (recessive allele frequency), then p = 0.7. Heterozygous frequency = 2pq = 2 × 0.7 × 0.3 = 0.42. In 10,000 individuals: 0.42 × 10,000 = 4,200",
                    "difficulty": difficulty
                },
                {
                    "question_text": "The Calvin cycle occurs in which part of the chloroplast?",
                    "option_a": "Thylakoid membrane",
                    "option_b": "Stroma",
                    "option_c": "Outer membrane",
                    "option_d": "Inner membrane",
                    "correct_answer": "B",
                    "explanation": "The Calvin cycle (light-independent reactions) occurs in the stroma of chloroplasts, where CO₂ is fixed into organic molecules using ATP and NADPH from light reactions.",
                    "difficulty": difficulty
                },
                {
                    "question_text": "During meiosis I, crossing over occurs during which phase?",
                    "option_a": "Prophase I",
                    "option_b": "Metaphase I",
                    "option_c": "Anaphase I",
                    "option_d": "Telophase I",
                    "correct_answer": "A",
                    "explanation": "Crossing over occurs during prophase I of meiosis, specifically during the pachytene stage when homologous chromosomes are paired and genetic material is exchanged.",
                    "difficulty": difficulty
                },
                {
                    "question_text": "The hormone responsible for the fight-or-flight response is:",
                    "option_a": "Insulin",
                    "option_b": "Adrenaline (Epinephrine)",
                    "option_c": "Thyroxine",
                    "option_d": "Cortisol",
                    "correct_answer": "B",
                    "explanation": "Adrenaline (epinephrine) is released by the adrenal medulla during stress, causing increased heart rate, blood pressure, and glucose levels - the classic fight-or-flight response.",
                    "difficulty": difficulty
                }
            ]
        }
        
        available_questions = fallback_questions.get(subject, fallback_questions["Biology"])
        
        # Return appropriate number of questions, cycling if needed
        result = []
        for i in range(count):
            question_index = i % len(available_questions)
            result.append(available_questions[question_index])
        
        return result
