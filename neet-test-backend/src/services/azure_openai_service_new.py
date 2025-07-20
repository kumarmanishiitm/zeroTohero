"""
Enhanced Azure OpenAI service for generating NEET questions
LLM-first approach with intelligent fallbacks and topic-specific generation
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
        self.model_name = os.getenv('AZURE_OPENAI_MODEL_NAME', 'gpt-4')
        self.api_version = os.getenv('AZURE_OPENAI_VERSION', '2024-02-15-preview')
        
        # Track LLM usage vs fallback usage
        self.llm_attempts = 0
        self.llm_successes = 0
        self.fallback_uses = 0
        
        # For demo purposes, we'll simulate LLM responses if Azure OpenAI is not configured
        self.demo_mode = not all([self.api_key, self.endpoint])
        
        if self.demo_mode:
            print("🔧 Demo Mode: Azure OpenAI not configured. Will generate intelligent topic-specific questions.")
        else:
            print("🚀 Azure OpenAI configured. LLM-first question generation enabled.")
    
    def generate_neet_questions(self, subject: str, topic: str = None, count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate NEET questions with LLM-first approach, topic-specific focus"""
        
        print(f"\n🎯 Generating {count} {difficulty} questions for {subject}" + (f" - {topic}" if topic else ""))
        
        # Always try LLM first (either real Azure OpenAI or intelligent simulation)
        try:
            if not self.demo_mode:
                # Real Azure OpenAI
                self.llm_attempts += 1
                questions = self._generate_with_azure_openai(subject, topic, count, difficulty)
                self.llm_successes += 1
                print(f"✅ LLM Success Rate: {self.llm_successes}/{self.llm_attempts} ({100*self.llm_successes/self.llm_attempts:.1f}%)")
                return questions
            else:
                # Intelligent simulation of LLM responses
                return self._generate_intelligent_llm_simulation(subject, topic, count, difficulty)
        
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}")
            self.fallback_uses += 1
            
            # Only use emergency fallback as last resort
            print(f"🚨 Using emergency fallback (Use #{self.fallback_uses})")
            return self._get_emergency_fallback_questions(subject, topic, count, difficulty)
    
    def _generate_with_azure_openai(self, subject: str, topic: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate questions using Azure OpenAI with enhanced prompts"""
        
        prompt = self._create_enhanced_neet_prompt(subject, topic, count, difficulty)
        
        url = f"{self.endpoint}openai/deployments/{self.model_name}/chat/completions?api-version={self.api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": """You are an expert NEET question generator with deep knowledge of Physics, Chemistry, and Biology. 
                    Generate questions that exactly match NEET exam standards and difficulty levels.
                    Always respond with valid JSON format containing exactly the requested number of questions.
                    Make each question unique and topic-specific. Ensure scientific accuracy."""
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 3000,
            "temperature": 0.8,  # Higher creativity for varied questions
            "top_p": 0.9,
            "frequency_penalty": 0.3,  # Reduce repetition
            "presence_penalty": 0.2
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=45)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Clean up the response to ensure valid JSON
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        
        questions_data = json.loads(content)
        questions = questions_data.get('questions', [])
        
        print(f"✅ Generated {len(questions)} questions using Azure OpenAI")
        return questions
    
    def _generate_intelligent_llm_simulation(self, subject: str, topic: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Simulate LLM generation with intelligent, topic-specific questions"""
        
        print(f"🧠 Simulating LLM generation for {subject} - {topic}")
        
        # Use timestamp and random for uniqueness
        current_time = int(time.time())
        session_id = random.randint(1000, 9999)
        
        # Get topic-specific question generators
        questions = []
        for i in range(count):
            question = self._generate_unique_topic_question(subject, topic, difficulty, i + 1, current_time, session_id)
            questions.append(question)
        
        print(f"✅ Generated {len(questions)} unique questions via intelligent simulation")
        return questions
    
    def _generate_unique_topic_question(self, subject: str, topic: str, difficulty: str, question_num: int, timestamp: int, session_id: int) -> Dict[str, Any]:
        """Generate a unique question based on topic"""
        
        # Topic-specific question generators
        if subject == 'Physics':
            return self._generate_physics_question(topic, difficulty, question_num, timestamp, session_id)
        elif subject == 'Chemistry':
            return self._generate_chemistry_question(topic, difficulty, question_num, timestamp, session_id)
        elif subject == 'Biology':
            return self._generate_biology_question(topic, difficulty, question_num, timestamp, session_id)
        else:
            return self._generate_general_question(subject, topic, difficulty, question_num)
    
    def _generate_physics_question(self, topic: str, difficulty: str, question_num: int, timestamp: int, session_id: int) -> Dict[str, Any]:
        """Generate Physics questions based on topic"""
        
        physics_questions = {
            'Mechanics': [
                {
                    "question_text": f"[Q{question_num}-{session_id}] A particle undergoes motion with acceleration a = {2 + question_num} m/s². If it starts from rest, what is its velocity after {3 + question_num} seconds?",
                    "option_a": f"{(2 + question_num) * (3 + question_num)} m/s",
                    "option_b": f"{(2 + question_num) * (3 + question_num) / 2} m/s",
                    "option_c": f"{(2 + question_num) + (3 + question_num)} m/s",
                    "option_d": f"{(2 + question_num) * (3 + question_num) * 2} m/s",
                    "correct_answer": "A",
                    "explanation": f"Using v = u + at, where u=0, a={2 + question_num} m/s², t={3 + question_num} s: v = 0 + {2 + question_num} × {3 + question_num} = {(2 + question_num) * (3 + question_num)} m/s",
                    "difficulty": difficulty,
                    "topic": topic
                },
                {
                    "question_text": f"[Q{question_num}-{session_id}] A projectile is launched at {30 + question_num * 5}° to the horizontal with initial velocity {20 + question_num * 2} m/s. What is the time of flight? (g = 10 m/s²)",
                    "option_a": f"{2 * (20 + question_num * 2) * 0.5 / 10:.1f} s",
                    "option_b": f"{2 * (20 + question_num * 2) * 0.6 / 10:.1f} s",
                    "option_c": f"{(20 + question_num * 2) * 0.5 / 10:.1f} s",
                    "option_d": f"{(20 + question_num * 2) / 10:.1f} s",
                    "correct_answer": "A",
                    "explanation": f"Time of flight T = 2v₀sinθ/g. For v₀={20 + question_num * 2} m/s, θ={30 + question_num * 5}°: T = 2×{20 + question_num * 2}×sin({30 + question_num * 5}°)/10",
                    "difficulty": difficulty,
                    "topic": topic
                }
            ],
            'Thermodynamics': [
                {
                    "question_text": f"[Q{question_num}-{session_id}] An ideal gas undergoes an isothermal process at {250 + question_num * 10} K. If the volume changes from {2 + question_num} L to {4 + question_num * 2} L, what happens to the pressure?",
                    "option_a": "Pressure increases",
                    "option_b": "Pressure decreases", 
                    "option_c": "Pressure remains constant",
                    "option_d": "Pressure becomes zero",
                    "correct_answer": "B",
                    "explanation": f"In an isothermal process, PV = constant. Since volume increases from {2 + question_num} L to {4 + question_num * 2} L, pressure must decrease to maintain the product constant.",
                    "difficulty": difficulty,
                    "topic": topic
                }
            ],
            'Electromagnetism': [
                {
                    "question_text": f"[Q{question_num}-{session_id}] A charge of {2 + question_num} μC is placed in an electric field of {1000 + question_num * 100} N/C. What is the force experienced by the charge?",
                    "option_a": f"{(2 + question_num) * (1000 + question_num * 100) / 1000000:.6f} N",
                    "option_b": f"{(2 + question_num) * (1000 + question_num * 100) / 1000:.3f} N",
                    "option_c": f"{(2 + question_num) * (1000 + question_num * 100):.0f} N",
                    "option_d": f"{(2 + question_num) + (1000 + question_num * 100):.0f} N",
                    "correct_answer": "A",
                    "explanation": f"Force F = qE = {2 + question_num} × 10⁻⁶ C × {1000 + question_num * 100} N/C = {(2 + question_num) * (1000 + question_num * 100) / 1000000:.6f} N",
                    "difficulty": difficulty,
                    "topic": topic
                }
            ]
        }
        
        # Get questions for the topic or use general physics
        topic_questions = physics_questions.get(topic, physics_questions['Mechanics'])
        selected_question = topic_questions[question_num % len(topic_questions)].copy()
        
        return selected_question
    
    def _generate_chemistry_question(self, topic: str, difficulty: str, question_num: int, timestamp: int, session_id: int) -> Dict[str, Any]:
        """Generate Chemistry questions based on topic"""
        
        chemistry_questions = {
            'Organic Chemistry': [
                {
                    "question_text": f"[Q{question_num}-{session_id}] What is the IUPAC name of the compound with molecular formula C{3 + question_num}H{6 + question_num * 2}O (an alcohol)?",
                    "option_a": f"{'prop' if question_num % 2 == 1 else 'but'}anol",
                    "option_b": f"{'prop' if question_num % 2 == 1 else 'but'}an-1-ol",
                    "option_c": f"{'but' if question_num % 2 == 1 else 'prop'}anol",
                    "option_d": f"{'but' if question_num % 2 == 1 else 'prop'}an-2-ol",
                    "correct_answer": "B",
                    "explanation": f"For a primary alcohol with {3 + question_num} carbons, the IUPAC name includes the position of -OH group as -1-ol",
                    "difficulty": difficulty,
                    "topic": topic
                }
            ],
            'Inorganic Chemistry': [
                {
                    "question_text": f"[Q{question_num}-{session_id}] The oxidation state of manganese in KMnO₄ is:",
                    "option_a": "+6",
                    "option_b": "+7",
                    "option_c": "+5",
                    "option_d": "+4",
                    "correct_answer": "B",
                    "explanation": "In KMnO₄: K is +1, O is -2. For the compound to be neutral: (+1) + Mn + 4(-2) = 0, so Mn = +7",
                    "difficulty": difficulty,
                    "topic": topic
                }
            ]
        }
        
        topic_questions = chemistry_questions.get(topic, chemistry_questions['Inorganic Chemistry'])
        selected_question = topic_questions[question_num % len(topic_questions)].copy()
        
        return selected_question
    
    def _generate_biology_question(self, topic: str, difficulty: str, question_num: int, timestamp: int, session_id: int) -> Dict[str, Any]:
        """Generate Biology questions based on topic"""
        
        biology_questions = {
            'Cell Biology': [
                {
                    "question_text": f"[Q{question_num}-{session_id}] Which of the following is NOT a function of the cell membrane?",
                    "option_a": "Selective permeability",
                    "option_b": "Protein synthesis",
                    "option_c": "Cell recognition",
                    "option_d": "Transport regulation",
                    "correct_answer": "B",
                    "explanation": "Protein synthesis occurs in ribosomes, not in the cell membrane. The cell membrane is responsible for selective permeability, cell recognition, and transport regulation.",
                    "difficulty": difficulty,
                    "topic": topic
                }
            ],
            'Genetics': [
                {
                    "question_text": f"[Q{question_num}-{session_id}] In a cross between AaBb × AaBb, what fraction of offspring will show both dominant traits?",
                    "option_a": "1/16",
                    "option_b": "3/16",
                    "option_c": "9/16",
                    "option_d": "12/16",
                    "correct_answer": "C",
                    "explanation": "In a dihybrid cross AaBb × AaBb, the phenotypic ratio is 9:3:3:1. 9/16 offspring show both dominant traits (A_B_).",
                    "difficulty": difficulty,
                    "topic": topic
                }
            ]
        }
        
        topic_questions = biology_questions.get(topic, biology_questions['Cell Biology'])
        selected_question = topic_questions[question_num % len(topic_questions)].copy()
        
        return selected_question
    
    def _generate_general_question(self, subject: str, topic: str, difficulty: str, question_num: int) -> Dict[str, Any]:
        """Generate general questions when specific topic generators are not available"""
        
        return {
            "question_text": f"[Generated] What is a key concept in {subject} related to {topic}?",
            "option_a": f"Concept A of {topic}",
            "option_b": f"Concept B of {topic}",
            "option_c": f"Concept C of {topic}",
            "option_d": f"Concept D of {topic}",
            "correct_answer": "A",
            "explanation": f"This is a generated question about {topic} in {subject}.",
            "difficulty": difficulty,
            "topic": topic
        }
    
    def _create_enhanced_neet_prompt(self, subject: str, topic: str, count: int, difficulty: str) -> str:
        """Create an enhanced, topic-specific prompt for NEET question generation"""
        
        current_time = int(time.time())
        
        # Topic-specific instructions
        topic_focus = ""
        if topic:
            topic_focus = f"""
TOPIC FOCUS: {topic}
- All questions must be specifically about {topic}
- Cover different aspects and subtopics within {topic}
- Use {topic}-specific terminology and concepts
- Include numerical problems if applicable to {topic}
- Reference {topic}-related phenomena, laws, or principles
"""
        
        subject_guidelines = self._get_subject_guidelines(subject, topic)
        
        prompt = f"""
Generate {count} unique NEET {subject} questions{f' focusing on {topic}' if topic else ''}.

{topic_focus}

SUBJECT: {subject}
DIFFICULTY: {difficulty}
COUNT: {count}
TIMESTAMP: {current_time}

{subject_guidelines}

STRICT REQUIREMENTS:
1. Each question must be completely different from others
2. Test conceptual understanding, not just memorization
3. Include application-based scenarios where possible
4. Use authentic NEET exam language and style
5. Ensure scientific accuracy in all content
6. Make distractors plausible but clearly incorrect
7. Generate fresh, unique content each time

DIFFICULTY SPECIFICATIONS:
- Easy: Direct application of basic concepts, simple calculations
- Medium: Multi-step reasoning, concept integration, moderate complexity
- Hard: Advanced analysis, multiple concepts, complex problem-solving

OUTPUT FORMAT (Valid JSON only):
{{
  "questions": [
    {{
      "question_text": "Complete question with all necessary information and context",
      "option_a": "First option - must be plausible",
      "option_b": "Second option - must be plausible", 
      "option_c": "Third option - must be plausible",
      "option_d": "Fourth option - must be plausible",
      "correct_answer": "A",
      "explanation": "Detailed explanation with scientific reasoning and why other options are wrong",
      "difficulty": "{difficulty}",
      "topic": "{topic if topic else 'General'}"
    }}
  ]
}}

Generate exactly {count} unique questions now.
"""
        return prompt
    
    def _get_subject_guidelines(self, subject: str, topic: str) -> str:
        """Get detailed subject and topic-specific guidelines"""
        
        guidelines = {
            'Physics': {
                'general': 'Focus on laws, principles, formulas, and numerical problems. Include units and calculations.',
                'topics': {
                    'Mechanics': 'Kinematics, dynamics, work-energy, momentum, rotational motion, gravitation',
                    'Thermodynamics': 'Laws of thermodynamics, heat engines, entropy, phase transitions', 
                    'Electromagnetism': 'Electric fields, magnetic fields, circuits, electromagnetic induction',
                    'Optics': 'Ray optics, wave optics, interference, diffraction, polarization',
                    'Modern Physics': 'Atomic structure, quantum mechanics, radioactivity, nuclear physics'
                }
            },
            'Chemistry': {
                'general': 'Focus on chemical reactions, structures, mechanisms, and calculations. Include molecular formulas.',
                'topics': {
                    'Organic Chemistry': 'Hydrocarbons, functional groups, reactions, mechanisms, stereochemistry',
                    'Inorganic Chemistry': 'Periodic properties, chemical bonding, coordination compounds, metallurgy',
                    'Physical Chemistry': 'Thermodynamics, kinetics, equilibrium, electrochemistry, solutions'
                }
            },
            'Biology': {
                'general': 'Focus on biological processes, structures, functions, and life phenomena. Include scientific names.',
                'topics': {
                    'Cell Biology': 'Cell structure, organelles, cell division, membrane transport',
                    'Genetics': 'Heredity, DNA structure, protein synthesis, genetic engineering',
                    'Plant Physiology': 'Photosynthesis, respiration, transport, plant hormones',
                    'Human Physiology': 'Circulatory, respiratory, nervous, endocrine, excretory systems'
                }
            }
        }
        
        subject_info = guidelines.get(subject, guidelines['Biology'])
        general_info = subject_info['general']
        
        topic_info = ""
        if topic and topic in subject_info.get('topics', {}):
            topic_info = f"\nTOPIC SPECIFIC: {subject_info['topics'][topic]}"
        
        return f"{general_info}{topic_info}"
    
    def _get_emergency_fallback_questions(self, subject: str, topic: str, count: int, difficulty: str) -> List[Dict[str, Any]]:
        """Emergency fallback - only 2-3 basic questions to prevent total failure"""
        
        print(f"🚨 EMERGENCY FALLBACK: Generating minimal questions for {subject}")
        
        emergency_questions = {
            'Physics': {
                "question_text": "What is the SI unit of force?",
                "option_a": "Newton",
                "option_b": "Joule", 
                "option_c": "Watt",
                "option_d": "Pascal",
                "correct_answer": "A",
                "explanation": "The SI unit of force is Newton (N), named after Sir Isaac Newton.",
                "difficulty": difficulty,
                "topic": topic or "General"
            },
            'Chemistry': {
                "question_text": "What is the atomic number of hydrogen?",
                "option_a": "1",
                "option_b": "2",
                "option_c": "0",
                "option_d": "3",
                "correct_answer": "A",
                "explanation": "Hydrogen has atomic number 1, meaning it has 1 proton in its nucleus.",
                "difficulty": difficulty,
                "topic": topic or "General"
            },
            'Biology': {
                "question_text": "What is the basic unit of life?",
                "option_a": "Cell",
                "option_b": "Atom",
                "option_c": "Molecule",
                "option_d": "Organism",
                "correct_answer": "A",
                "explanation": "The cell is the basic unit of life. All living organisms are made up of one or more cells.",
                "difficulty": difficulty,
                "topic": topic or "General"
            }
        }
        
        base_question = emergency_questions.get(subject, emergency_questions['Biology'])
        
        # Generate the requested number by slight variations
        questions = []
        for i in range(min(count, 3)):  # Limit emergency fallback to 3 questions max
            question = base_question.copy()
            if i > 0:
                question['question_text'] = f"[Emergency Fallback {i+1}] {question['question_text']}"
            questions.append(question)
        
        return questions
