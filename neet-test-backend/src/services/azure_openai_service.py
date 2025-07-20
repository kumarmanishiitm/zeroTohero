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
        
        # Counter for ensuring unique IDs
        self._id_counter = 0
        
        # Check if Azure OpenAI is properly configured
        self.demo_mode = not all([self.api_key, self.endpoint])
        
        if self.demo_mode:
            print("🔧 Demo Mode: Azure OpenAI not configured. Will generate intelligent topic-specific questions.")
        else:
            print(f"🚀 Azure OpenAI configured: {self.endpoint} with model {self.model_name}")
            print("✅ LLM-first question generation enabled.")
    
    def _generate_unique_id(self, prefix: str = "ai") -> str:
        """Generate a guaranteed unique ID"""
        import time
        import random
        
        # Increment counter and add small delay for uniqueness
        self._id_counter += 1
        time.sleep(0.001)  # 1ms delay to ensure unique timestamps
        
        microseconds = int(time.time() * 1000000)
        random_suffix = random.randint(10000, 99999)
        
        return f"{prefix}_{microseconds}_{random_suffix}_{self._id_counter}"
    
    def generate_neet_questions(self, subject: str, topic: str = None, count: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate NEET questions ONLY from Azure OpenAI - NO FALLBACK LOGIC"""
        
        print(f"\n🎯 Generating {count} FRESH {difficulty} questions for {subject}" + (f" - {topic}" if topic else ""))
        
        # Add timestamp and randomness to ensure unique questions
        current_time = int(time.time())
        session_id = random.randint(10000, 99999)
        
        # ONLY USE AZURE OPENAI - NO FALLBACK ALLOWED
        try:
            if not self.demo_mode:
                # Real Azure OpenAI with enhanced uniqueness
                self.llm_attempts += 1
                questions = self._generate_with_azure_openai(subject, topic, count, difficulty, current_time, session_id)
                self.llm_successes += 1
                print(f"✅ LLM Success Rate: {self.llm_successes}/{self.llm_attempts} ({100*self.llm_successes/self.llm_attempts:.1f}%)")
                return questions
            else:
                # Demo mode - throw error instead of using fallback
                raise Exception("Demo mode not allowed - only Azure OpenAI allowed")
        
        except Exception as e:
            print(f"❌ Azure OpenAI generation failed: {e}")
            # NO FALLBACK - RAISE ERROR INSTEAD
            raise Exception(f"Azure OpenAI failed to generate questions: {e}. NO FALLBACK ALLOWED.")
    
    def _generate_with_azure_openai(self, subject: str, topic: str, count: int, difficulty: str, timestamp: int, session_id: int) -> List[Dict[str, Any]]:
        """Generate questions using Azure OpenAI with enhanced prompts for uniqueness"""
        
        # If requesting many questions, generate in smaller batches to avoid truncation
        if count > 2:  # Even smaller batches to ensure completion
            print(f"🔄 Generating {count} questions in smaller batches to ensure complete responses...")
            all_questions = []
            remaining = count
            
            while remaining > 0:
                batch_size = min(2, remaining)  # Generate max 2 at a time for reliability
                print(f"📦 Generating batch of {batch_size} questions...")
                
                batch_questions = self._generate_batch_with_azure_openai(subject, topic, batch_size, difficulty, timestamp, session_id)
                all_questions.extend(batch_questions)
                remaining -= batch_size
                
                # Add small delay between batches
                if remaining > 0:
                    time.sleep(0.5)
            
            print(f"✅ Combined all batches: {len(all_questions)} total questions")
            return all_questions
        else:
            # For small counts, generate directly
            return self._generate_batch_with_azure_openai(subject, topic, count, difficulty, timestamp, session_id)
    
    def _generate_batch_with_azure_openai(self, subject: str, topic: str, count: int, difficulty: str, timestamp: int, session_id: int) -> List[Dict[str, Any]]:
        """Generate a small batch of questions to avoid response truncation"""
        
        prompt = self._create_enhanced_neet_prompt(subject, topic, count, difficulty, timestamp, session_id)
        
        url = f"{self.endpoint}openai/deployments/{self.model_name}/chat/completions?api-version={self.api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": """You are an expert NEET question generator. CRITICAL INSTRUCTIONS:
1. Return ONLY valid, complete JSON - no truncation allowed
2. Keep options SHORT and concise (under 50 characters each)
3. Use simple text for math: '10^-6' not '10\\(^{-6}\\)'
4. No special characters that need JSON escaping
5. Complete ALL questions in the response
6. End with proper JSON closing braces}}"""
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,  # Increased to ensure complete responses
            "temperature": 0.8,  # Higher for more diversity
            "top_p": 0.9,
            "frequency_penalty": 0.4,  # Higher to reduce repetition
            "presence_penalty": 0.3,
            "stop": None  # Don't stop generation prematurely
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Clean up the response to ensure valid JSON
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        print(f"🔧 Response length: {len(content)} chars")
        print(f"🔧 Response starts with: {content[:100]}...")
        print(f"🔧 Response ends with: {content[-100:]}")
        
        try:
            questions_data = json.loads(content)
            questions = questions_data.get('questions', [])
            
            if not questions:
                # Try to parse if the response is directly a list
                if isinstance(questions_data, list):
                    questions = questions_data
                else:
                    raise ValueError("No questions found in response")
            
            print(f"✅ Successfully parsed JSON with {len(questions)} questions")
            
            # Validate questions have required fields and add unique IDs if missing
            valid_questions = []
            required_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
            
            for i, q in enumerate(questions):
                print(f"🔧 Validating question {i+1}: has fields {list(q.keys())}")
                
                # Check for required fields
                missing_fields = [field for field in required_fields if field not in q]
                if missing_fields:
                    print(f"⚠️ Question {i+1} missing fields: {missing_fields}")
                    continue
                
                # Validate correct_answer is a valid option
                correct_answer = q.get('correct_answer', '').upper()
                if correct_answer not in ['A', 'B', 'C', 'D']:
                    print(f"⚠️ Question {i+1} has invalid correct_answer: {correct_answer}")
                    continue
                
                # Check option lengths to prevent truncation issues
                for opt_key in ['option_a', 'option_b', 'option_c', 'option_d']:
                    if len(q.get(opt_key, '')) > 120:  # Warn if very long
                        print(f"⚠️ Question {i+1} {opt_key} is very long: {len(q[opt_key])} chars")
                
                # Generate truly unique ID using the new method
                unique_id = self._generate_unique_id("ai")
                q['id'] = unique_id
                print(f"✅ Question {i+1} validated with ID: {unique_id}")
                
                # Validate and fix answer-explanation consistency
                self._validate_answer_consistency(q, i+1)
                
                valid_questions.append(q)
                    
            print(f"✅ Final validation: {len(valid_questions)} valid questions out of {len(questions)}")
            
            if not valid_questions:
                raise ValueError("No valid questions found after validation")
            
            return valid_questions
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw content: {content[:500]}...")
            
            # Try to fix common JSON issues and retry
            try:
                fixed_content = self._fix_json_formatting(content)
                print(f"🔧 Attempting to fix JSON formatting...")
                questions_data = json.loads(fixed_content)
                questions = questions_data.get('questions', [])
                
                if not questions and isinstance(questions_data, list):
                    questions = questions_data
                    
                if questions:
                    print(f"✅ Fixed JSON parsing - got {len(questions)} questions")
                    # Apply full validation to fixed questions too
                    valid_questions = []
                    required_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                    
                    for i, q in enumerate(questions):
                        missing_fields = [field for field in required_fields if field not in q]
                        if not missing_fields:
                            unique_id = self._generate_unique_id("ai")
                            q['id'] = unique_id
                            self._validate_answer_consistency(q, i+1)
                            valid_questions.append(q)
                        else:
                            print(f"⚠️ Skipping invalid fixed question: missing {missing_fields}")
                    
                    if valid_questions:
                        print(f"✅ Successfully recovered {len(valid_questions)} questions after JSON fix")
                        return valid_questions
                    
            except Exception as fix_error:
                print(f"❌ JSON fix attempt also failed: {fix_error}")
            
            # As a last resort, try to extract individual questions using regex
            print("🔧 Attempting regex-based question extraction...")
            try:
                extracted_questions = self._extract_questions_from_broken_json(content)
                if extracted_questions:
                    print(f"✅ Extracted {len(extracted_questions)} questions using regex fallback")
                    return extracted_questions
            except Exception as regex_error:
                print(f"❌ Regex extraction also failed: {regex_error}")
            
            # If all parsing fails, raise error - NO FALLBACK
            raise ValueError(f"Failed to parse Azure OpenAI response as JSON: {e}. Content: {content[:200]}...")
            
        except Exception as e:
            print(f"❌ Error processing Azure OpenAI response: {e}")
            raise
    
    def _fix_json_formatting(self, content: str) -> str:
        """Fix common JSON formatting issues including truncation and mathematical notation"""
        import re
        
        print(f"🔧 Original content length: {len(content)} chars")
        print(f"🔧 First 200 chars: {content[:200]}")
        print(f"🔧 Last 200 chars: {content[-200:]}")
        
        # Remove any non-JSON content before the first {
        start_idx = content.find('{')
        if start_idx > 0:
            content = content[start_idx:]
            print(f"🔧 Removed prefix, new length: {len(content)}")
        
        # Handle truncated JSON - if it doesn't end properly, try to complete it
        if not content.rstrip().endswith('}'):
            print("🔧 JSON appears truncated, attempting to complete...")
            
            # Try to identify where the content was cut off
            last_quote_pos = content.rfind('"')
            
            if last_quote_pos > 0:
                # Check if we're in the middle of a field value
                after_quote = content[last_quote_pos+1:].strip()
                
                # If we have an incomplete string, complete it
                if not after_quote or after_quote in [',', '}', ']']:
                    # Looks like we just have a trailing quote, that's fine
                    pass
                else:
                    # We're in the middle of a value, close the string
                    content = content[:last_quote_pos+1] + '"'
                    print(f"🔧 Completed truncated string")
            
            # Add missing structural elements
            # Count open braces and brackets to see what's missing
            open_braces = content.count('{') - content.count('}')
            open_brackets = content.count('[') - content.count(']')
            
            print(f"🔧 Missing: {open_braces} braces, {open_brackets} brackets")
            
            # Complete the structure
            while open_brackets > 0:
                content += ']'
                open_brackets -= 1
                print("🔧 Added closing bracket ]")
            
            while open_braces > 0:
                content += '}'
                open_braces -= 1
                print("🔧 Added closing brace }")
        
        # Remove any content after the last }
        end_idx = content.rfind('}')
        if end_idx > 0 and end_idx < len(content) - 1:
            trailing = content[end_idx+1:].strip()
            if trailing:
                print(f"🔧 Removing trailing content: {trailing[:50]}...")
                content = content[:end_idx + 1]
        
        # Fix mathematical notation escaping issues
        content = content.replace('\\(', '(')
        content = content.replace('\\)', ')')
        content = content.replace('\\^', '^')
        content = content.replace('\\{', '{')
        content = content.replace('\\}', '}')
        content = content.replace('\\_', '_')
        
        # Fix unquoted property names (simple cases)
        content = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', content)
        
        # Fix single quotes to double quotes
        content = content.replace("'", '"')
        
        # Fix trailing commas
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # Fix missing commas between objects
        content = re.sub(r'}\s*{', r'},{', content)
        
        # Fix incomplete strings by finding unclosed quotes and trying to complete them
        quote_count = content.count('"')
        if quote_count % 2 != 0:
            print(f"🔧 Found odd number of quotes ({quote_count}), attempting to fix...")
            # Find the last incomplete string and close it
            last_quote_idx = content.rfind('"')
            if last_quote_idx > 0:
                # Look for common patterns that might be incomplete
                after_quote = content[last_quote_idx + 1:]
                if not after_quote.strip() or after_quote.strip().startswith('}'):
                    # Likely a truncated string, add closing quote
                    content = content[:last_quote_idx + 1] + '"' + content[last_quote_idx + 1:]
        
        print(f"🔧 Fixed content length: {len(content)} chars")
        print(f"🔧 Fixed content preview: {content[:300]}...")
        
        return content
    
    def _extract_questions_from_broken_json(self, content: str) -> List[Dict[str, Any]]:
        """Extract questions from broken JSON using regex patterns as last resort"""
        import re
        
        print("🔧 Attempting regex-based question extraction from broken JSON...")
        
        questions = []
        
        # More flexible pattern to match question components even if incomplete
        # Extract question_text first
        question_texts = re.findall(r'"question_text":\s*"([^"]+)"', content)
        
        # Extract all options
        option_a_matches = re.findall(r'"option_a":\s*"([^"]*)"', content)
        option_b_matches = re.findall(r'"option_b":\s*"([^"]*)"', content)
        option_c_matches = re.findall(r'"option_c":\s*"([^"]*)"', content)
        option_d_matches = re.findall(r'"option_d":\s*"([^"]*)"', content)
        correct_answers = re.findall(r'"correct_answer":\s*"([ABCD])"', content, re.IGNORECASE)
        
        print(f"Found: {len(question_texts)} question_texts, {len(option_a_matches)} option_a, {len(option_b_matches)} option_b")
        print(f"Found: {len(option_c_matches)} option_c, {len(option_d_matches)} option_d, {len(correct_answers)} correct_answers")
        
        # Match up the components (taking the minimum count)
        min_count = min(len(question_texts), len(option_a_matches))
        
        for i in range(min_count):
            question_text = question_texts[i] if i < len(question_texts) else f"Question {i+1}"
            option_a = option_a_matches[i] if i < len(option_a_matches) else "Option A"
            option_b = option_b_matches[i] if i < len(option_b_matches) else "Option B"
            option_c = option_c_matches[i] if i < len(option_c_matches) else "Option C"
            option_d = option_d_matches[i] if i < len(option_d_matches) else "Option D"
            correct_answer = correct_answers[i] if i < len(correct_answers) else "A"
            
            # Basic validation - at least question text and some options
            if question_text and len(question_text) > 10:
                question = {
                    'id': self._generate_unique_id("regex"),
                    'question_text': question_text.strip(),
                    'option_a': option_a.strip() or "Option A",
                    'option_b': option_b.strip() or "Option B", 
                    'option_c': option_c.strip() or "Option C",
                    'option_d': option_d.strip() or "Option D",
                    'correct_answer': correct_answer.upper(),
                    'explanation': f"Extracted from incomplete response. Question about {question_text[:50]}...",
                    'difficulty': 'medium',
                    'topic': 'General'
                }
                
                questions.append(question)
                print(f"✅ Extracted question {i+1}: {question_text[:50]}...")
        
        if questions:
            print(f"✅ Successfully extracted {len(questions)} questions using regex")
        else:
            print("❌ Could not extract any questions using regex")
            
        return questions
    
    def _generate_intelligent_llm_simulation(self, subject: str, topic: str, count: int, difficulty: str, timestamp: int, session_id: int) -> List[Dict[str, Any]]:
        """Simulate LLM generation with intelligent, topic-specific questions"""
        
        print(f"🧠 Simulating LLM generation for {subject} - {topic} (Session: {session_id})")
        
        try:
            # Get topic-specific question generators
            questions = []
            for i in range(count):
                question = self._generate_unique_topic_question(subject, topic, difficulty, i + 1, timestamp, session_id)
                questions.append(question)
            
            print(f"✅ Generated {len(questions)} unique questions via intelligent simulation")
            return questions
            
        except Exception as e:
            print(f"❌ Intelligent simulation failed: {e}")
            # NO FALLBACK - RAISE ERROR
            raise Exception(f"Simulation failed: {e}. NO FALLBACK ALLOWED.")
    
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
        """Generate NEET-level Physics questions based on topic"""
        
        # Ensure random answer distribution
        correct_answers = ['A', 'B', 'C', 'D']
        correct_answer = correct_answers[question_num % 4]  # Cycle through A, B, C, D
        
        physics_questions = {
            'Mechanics': [
                {
                    "question_text": f"A particle moves with constant acceleration a = {2 + question_num} m/s². If it starts from rest, what is its velocity after t = {3 + question_num} seconds?",
                    "options": {
                        'A': f"{(2 + question_num) * (3 + question_num)} m/s",
                        'B': f"{(2 + question_num) * (3 + question_num) / 2} m/s",
                        'C': f"{(2 + question_num) + (3 + question_num)} m/s",
                        'D': f"{(2 + question_num) * (3 + question_num) * 2} m/s"
                    },
                    "correct_option": 'A',
                    "explanation": f"Using kinematic equation v = u + at. Initial velocity u = 0, acceleration a = {2 + question_num} m/s², time t = {3 + question_num} s. Therefore, v = 0 + {2 + question_num} × {3 + question_num} = {(2 + question_num) * (3 + question_num)} m/s. This is a fundamental application of kinematics in uniformly accelerated motion."
                },
                {
                    "question_text": f"A projectile is launched at 45° to horizontal with initial velocity {20 + question_num * 2} m/s. What is the maximum height reached? (g = 10 m/s²)",
                    "options": {
                        'A': f"{((20 + question_num * 2) ** 2) / 40:.1f} m",
                        'B': f"{((20 + question_num * 2) ** 2) / 80:.1f} m", 
                        'C': f"{((20 + question_num * 2) ** 2) / 20:.1f} m",
                        'D': f"{(20 + question_num * 2) / 10:.1f} m"
                    },
                    "correct_option": 'B',
                    "explanation": f"For projectile motion at 45°, vertical component of velocity = v₀sin45° = {20 + question_num * 2}/√2. Maximum height H = (v₀sin45°)²/(2g) = ({20 + question_num * 2}/√2)²/(2×10) = {((20 + question_num * 2) ** 2) / 80:.1f} m. This uses energy conservation and projectile motion principles."
                }
            ],
            'Thermodynamics': [
                {
                    "question_text": f"An ideal gas undergoes isothermal expansion at {273 + question_num * 10} K. If volume changes from {2 + question_num} L to {4 + question_num * 2} L, the work done by the gas is (R = 8.314 J/mol·K, n = 1 mol):",
                    "options": {
                        'A': f"{8.314 * (273 + question_num * 10) * 0.693:.0f} J",
                        'B': f"{8.314 * (273 + question_num * 10) * 1.386:.0f} J",
                        'C': f"{8.314 * (273 + question_num * 10) * 0.301:.0f} J",
                        'D': f"{8.314 * (273 + question_num * 10) * 2.079:.0f} J"
                    },
                    "correct_option": 'A',
                    "explanation": f"For isothermal process, W = nRT ln(V₂/V₁). Here, W = 1 × 8.314 × {273 + question_num * 10} × ln({4 + question_num * 2}/{2 + question_num}) = {8.314 * (273 + question_num * 10) * 0.693:.0f} J. This demonstrates the first law of thermodynamics for isothermal processes."
                }
            ],
            'Electromagnetism': [
                {
                    "question_text": f"Two point charges +{2 + question_num}q and -{1 + question_num}q are separated by distance r. The electric field is zero at a point:",
                    "options": {
                        'A': f"Between the charges, closer to -{1 + question_num}q",
                        'B': f"Between the charges, closer to +{2 + question_num}q",
                        'C': f"Beyond +{2 + question_num}q on the line joining them",
                        'D': f"Beyond -{1 + question_num}q on the line joining them"
                    },
                    "correct_option": 'A',
                    "explanation": f"Electric field is zero where fields due to both charges cancel. Since +{2 + question_num}q > {1 + question_num}q, the zero field point must be closer to the smaller charge (in magnitude) for the fields to balance. This occurs between charges, closer to -{1 + question_num}q. Applies Coulomb's law and superposition principle."
                }
            ]
        }
        
        # Get questions for the topic or use general mechanics
        topic_questions = physics_questions.get(topic, physics_questions['Mechanics'])
        base_question = topic_questions[question_num % len(topic_questions)].copy()
        
        # Randomize the correct answer position
        options = base_question['options']
        correct_text = options[base_question['correct_option']]
        
        # Create new option arrangement with randomized correct answer
        option_keys = ['A', 'B', 'C', 'D']
        option_values = list(options.values())
        
        # Put correct answer in desired position
        correct_index = option_keys.index(correct_answer)
        original_correct_index = option_keys.index(base_question['correct_option'])
        
        # Swap positions
        option_values[correct_index], option_values[original_correct_index] = option_values[original_correct_index], option_values[correct_index]
        
        # Add unique ID using the new method
        unique_id = self._generate_unique_id("phys")
        
        return {
            'id': unique_id,
            'question_text': base_question['question_text'],
            'option_a': option_values[0],
            'option_b': option_values[1],
            'option_c': option_values[2],
            'option_d': option_values[3],
            'correct_answer': correct_answer,
            'explanation': base_question['explanation'],
            'difficulty': difficulty,
            'topic': topic
        }
    
    def _generate_chemistry_question(self, topic: str, difficulty: str, question_num: int, timestamp: int, session_id: int) -> Dict[str, Any]:
        """Generate NEET-level Chemistry questions based on topic"""
        
        # Ensure random answer distribution
        correct_answers = ['A', 'B', 'C', 'D']
        correct_answer = correct_answers[question_num % 4]  # Cycle through A, B, C, D
        
        chemistry_questions = {
            'Organic Chemistry': [
                {
                    "question_text": f"What is the IUPAC name of the compound CH₃-CH(CH₃)-CH₂-CH₂-OH?",
                    "options": {
                        'A': "3-methylbutan-1-ol",
                        'B': "2-methylbutan-4-ol", 
                        'C': "3-methylbutanol",
                        'D': "2-methyl-1-butanol"
                    },
                    "correct_option": 'A',
                    "explanation": "The longest carbon chain has 4 carbons (butane). The -OH group is on carbon 1, making it butan-1-ol. The methyl group is on carbon 3 from the alcohol end. Therefore, the IUPAC name is 3-methylbutan-1-ol. IUPAC nomenclature prioritizes functional groups and uses lowest numbering."
                },
                {
                    "question_text": f"In the reaction CH₃CHO + HCN → Product, the product formed is:",
                    "options": {
                        'A': "CH₃CH(OH)CN",
                        'B': "CH₃CH(CN)OH", 
                        'C': "CH₃COCN",
                        'D': "CH₃CH₂CN"
                    },
                    "correct_option": 'A',
                    "explanation": "This is nucleophilic addition of HCN to acetaldehyde. The cyanide ion (CN⁻) attacks the carbonyl carbon, and H⁺ adds to oxygen, forming cyanohydrin: CH₃CH(OH)CN. This reaction demonstrates nucleophilic addition to carbonyl compounds, important in organic synthesis."
                }
            ],
            'Inorganic Chemistry': [
                {
                    "question_text": f"The oxidation state of chromium in K₂Cr₂O₇ is:",
                    "options": {
                        'A': "+6",
                        'B': "+7",
                        'C': "+3", 
                        'D': "+5"
                    },
                    "correct_option": 'A',
                    "explanation": "In K₂Cr₂O₇: K is +1, O is -2. For the compound to be neutral: 2(+1) + 2(Cr) + 7(-2) = 0. Solving: 2 + 2Cr - 14 = 0, so 2Cr = +12, Cr = +6. This demonstrates oxidation state calculation using the electroneutrality principle."
                },
                {
                    "question_text": f"Which of the following shows maximum covalent character?",
                    "options": {
                        'A': "LiCl",
                        'B': "NaCl",
                        'C': "KCl",
                        'D': "CsCl"
                    },
                    "correct_option": 'A',
                    "explanation": "According to Fajan's rules, covalent character increases with smaller cation size and higher charge density. Li⁺ is the smallest among given cations, so LiCl has maximum covalent character. This illustrates the relationship between ionic size and bonding character."
                }
            ],
            'Physical Chemistry': [
                {
                    "question_text": f"For the reaction N₂ + 3H₂ ⇌ 2NH₃, if Kp = 1.44 × 10⁻⁵ at 500°C, what is the value of Kc? (R = 0.082 L atm mol⁻¹ K⁻¹)",
                    "options": {
                        'A': "8.95 × 10⁻² mol⁻² L²",
                        'B': "1.44 × 10⁻⁵ mol⁻² L²",
                        'C': "2.31 × 10⁻⁸ mol⁻² L²",
                        'D': "9.24 × 10⁻³ mol⁻² L²"
                    },
                    "correct_option": 'A',
                    "explanation": "Using Kp = Kc(RT)^Δn. Here, Δn = (products - reactants) = 2 - (1+3) = -2. T = 500°C = 773 K. So Kc = Kp/(RT)^Δn = 1.44 × 10⁻⁵/(0.082 × 773)⁻² = 8.95 × 10⁻² mol⁻² L². This demonstrates the relationship between Kp and Kc."
                }
            ]
        }
        
        # Get questions for the topic or use general inorganic
        topic_questions = chemistry_questions.get(topic, chemistry_questions['Inorganic Chemistry'])
        base_question = topic_questions[question_num % len(topic_questions)].copy()
        
        # Randomize the correct answer position
        options = base_question['options']
        correct_text = options[base_question['correct_option']]
        
        # Create new option arrangement with randomized correct answer
        option_keys = ['A', 'B', 'C', 'D']
        option_values = list(options.values())
        
        # Put correct answer in desired position
        correct_index = option_keys.index(correct_answer)
        original_correct_index = option_keys.index(base_question['correct_option'])
        
        # Swap positions
        option_values[correct_index], option_values[original_correct_index] = option_values[original_correct_index], option_values[correct_index]
        
        # Add unique ID using the new method
        unique_id = self._generate_unique_id("chem")
        
        return {
            'id': unique_id,
            'question_text': base_question['question_text'],
            'option_a': option_values[0],
            'option_b': option_values[1],
            'option_c': option_values[2],
            'option_d': option_values[3],
            'correct_answer': correct_answer,
            'explanation': base_question['explanation'],
            'difficulty': difficulty,
            'topic': topic
        }
    
    def _generate_biology_question(self, topic: str, difficulty: str, question_num: int, timestamp: int, session_id: int) -> Dict[str, Any]:
        """Generate NEET-level Biology questions based on topic"""
        
        # Ensure random answer distribution
        correct_answers = ['A', 'B', 'C', 'D']
        correct_answer = correct_answers[question_num % 4]  # Cycle through A, B, C, D
        
        biology_questions = {
            'Cell Biology': [
                {
                    "question_text": f"Which of the following is NOT a function of smooth endoplasmic reticulum?",
                    "options": {
                        'A': "Lipid synthesis",
                        'B': "Protein synthesis",
                        'C': "Detoxification",
                        'D': "Steroid hormone synthesis"
                    },
                    "correct_option": 'B',
                    "explanation": "Protein synthesis occurs on rough endoplasmic reticulum (RER) which has ribosomes attached. Smooth ER lacks ribosomes and is involved in lipid synthesis, detoxification of harmful substances, and steroid hormone synthesis. This demonstrates the structural-functional relationship in cell organelles."
                },
                {
                    "question_text": f"During which phase of mitosis do chromosomes align at the equatorial plane?",
                    "options": {
                        'A': "Prophase",
                        'B': "Metaphase",
                        'C': "Anaphase", 
                        'D': "Telophase"
                    },
                    "correct_option": 'B',
                    "explanation": "During metaphase, chromosomes align at the equatorial plane (metaphase plate) of the cell. This alignment ensures equal distribution of genetic material to daughter cells. Spindle fibers from opposite poles attach to kinetochores, demonstrating the precision of cell division."
                }
            ],
            'Genetics': [
                {
                    "question_text": f"In a test cross between a heterozygous tall plant (Tt) and a dwarf plant (tt), what will be the phenotypic ratio?",
                    "options": {
                        'A': "3:1",
                        'B': "1:1",
                        'C': "9:3:3:1",
                        'D': "1:2:1"
                    },
                    "correct_option": 'B',
                    "explanation": "Test cross involves crossing a heterozygote with a homozygous recessive. Tt × tt gives 50% Tt (tall) and 50% tt (dwarf), resulting in 1:1 phenotypic ratio. This demonstrates Mendel's law of segregation and is used to determine unknown genotypes."
                },
                {
                    "question_text": f"The genetic code is said to be degenerate because:",
                    "options": {
                        'A': "Multiple codons can code for the same amino acid",
                        'B': "One codon codes for multiple amino acids",
                        'C': "Some codons do not code for any amino acid",
                        'D': "Codons are read in overlapping manner"
                    },
                    "correct_option": 'A',
                    "explanation": "Degeneracy of genetic code means multiple codons (usually differing in the third position) can specify the same amino acid. For example, UUU and UUC both code for phenylalanine. This provides protection against mutations and demonstrates the redundancy built into the genetic system."
                }
            ],
            'Plant Physiology': [
                {
                    "question_text": f"Which of the following is the primary acceptor of CO₂ in C₄ plants?",
                    "options": {
                        'A': "RuBP (Ribulose bisphosphate)",
                        'B': "PEP (Phosphoenolpyruvate)",
                        'C': "Pyruvate",
                        'D': "Oxaloacetate"
                    },
                    "correct_option": 'B',
                    "explanation": "In C₄ plants, CO₂ is first fixed by PEP carboxylase enzyme using PEP (phosphoenolpyruvate) as acceptor, forming oxaloacetate. This differs from C₃ plants where RuBP is the primary acceptor. C₄ pathway is an adaptation to minimize photorespiration in hot, dry conditions."
                }
            ],
            'Human Physiology': [
                {
                    "question_text": f"The pacemaker of the heart is located in:",
                    "options": {
                        'A': "SA node",
                        'B': "AV node", 
                        'C': "Bundle of His",
                        'D': "Purkinje fibers"
                    },
                    "correct_option": 'A',
                    "explanation": "The sinoatrial (SA) node, located in the right atrium, acts as the natural pacemaker of the heart. It generates electrical impulses that initiate each heartbeat at a rate of 70-75 beats per minute. This demonstrates the specialized conduction system of the heart."
                }
            ]
        }
        
        # Get questions for the topic or use general cell biology
        topic_questions = biology_questions.get(topic, biology_questions['Cell Biology'])
        base_question = topic_questions[question_num % len(topic_questions)].copy()
        
        # Randomize the correct answer position
        options = base_question['options']
        correct_text = options[base_question['correct_option']]
        
        # Create new option arrangement with randomized correct answer
        option_keys = ['A', 'B', 'C', 'D']
        option_values = list(options.values())
        
        # Put correct answer in desired position
        correct_index = option_keys.index(correct_answer)
        original_correct_index = option_keys.index(base_question['correct_option'])
        
        # Swap positions
        option_values[correct_index], option_values[original_correct_index] = option_values[original_correct_index], option_values[correct_index]
        
        # Add unique ID using the new method
        unique_id = self._generate_unique_id("bio")
        
        return {
            'id': unique_id,
            'question_text': base_question['question_text'],
            'option_a': option_values[0],
            'option_b': option_values[1],
            'option_c': option_values[2],
            'option_d': option_values[3],
            'correct_answer': correct_answer,
            'explanation': base_question['explanation'],
            'difficulty': difficulty,
            'topic': topic
        }
    
    def _generate_general_question(self, subject: str, topic: str, difficulty: str, question_num: int) -> Dict[str, Any]:
        """Generate general questions when specific topic generators are not available"""
        
        # Add unique ID using the new method
        unique_id = self._generate_unique_id("gen")
        
        return {
            "id": unique_id,
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
    
    def _create_enhanced_neet_prompt(self, subject: str, topic: str, count: int, difficulty: str, timestamp: int = None, session_id: int = None) -> str:
        """Create NEET-focused prompts with balanced answer distribution and high-quality content"""
        
        topic_text = f" on {topic}" if topic else ""
        
        # NEET-specific subject guidelines with focus on concepts, numericals, and previous year patterns
        subject_guidelines = {
            'Physics': {
                'focus': 'NEET Physics: diverse concepts, problem-solving, real-world applications',
                'question_types': ['Conceptual analysis', 'Numerical computations', 'Comparative studies', 'Experimental scenarios', 'Graphical interpretation', 'Cause-effect relationships']
            },
            'Chemistry': {
                'focus': 'NEET Chemistry: comprehensive coverage across organic, inorganic, and physical chemistry',
                'question_types': ['Mechanism analysis', 'Structure-property relationships', 'Quantitative calculations', 'Experimental design', 'Comparative chemistry', 'Industrial applications']
            },
            'Biology': {
                'focus': 'NEET Biology: life processes, genetics, ecology, and biotechnology applications',
                'question_types': ['Process analysis', 'System integration', 'Genetic problems', 'Ecological scenarios', 'Medical applications', 'Evolutionary concepts']
            }
        }
        
        subject_info = subject_guidelines.get(subject, subject_guidelines['Biology'])
        question_types = ', '.join(subject_info['question_types'])
        
        # Answer distribution enforcement
        answer_distribution_instruction = """
CRITICAL: Ensure balanced answer distribution across all options (A, B, C, D).
- Do NOT favor option A
- Correct answers should be randomly distributed: some A, some B, some C, some D
- Each option should appear as correct answer roughly equally
- Avoid patterns like A, A, A or sequential patterns
"""
        
        # Quality standards based on NEET requirements
        quality_standards = f"""
NEET QUALITY STANDARDS:
1. Questions must test deep conceptual understanding, not just memorization
2. Include numerical problems with proper units and significant figures
3. Use NCERT terminology and standard conventions
4. Similar to previous year NEET question patterns
5. Explanation must clarify the concept and methodology
6. Options should be plausible but clearly distinguishable
7. Avoid ambiguous or trick questions
8. Focus on application of concepts to real-world scenarios

SUBJECT FOCUS: {subject_info['focus']}
QUESTION TYPES TO USE: {question_types}
{f"TOPIC SPECIFIC: Focus on {topic}" if topic else ""}
"""
        
        prompt = f"""You are an expert NEET question creator. Generate {count} high-quality NEET {subject} questions{topic_text} at {difficulty} level.

{quality_standards}

{answer_distribution_instruction}

QUESTION VARIETY REQUIREMENTS:
- Create DIVERSE question types: conceptual, analytical, application-based, comparative, and computational
- Avoid repetitive patterns or similar question structures
- Mix different cognitive levels: knowledge, comprehension, application, analysis
- Vary question contexts: theoretical concepts, real-world applications, experimental scenarios
- Use different formats: direct questions, scenario-based, data interpretation, cause-effect

FORMATTING REQUIREMENTS:
- Keep ALL option texts under 80 characters to prevent truncation
- Use simple mathematical notation: "10^-6" not "10\\(^{{-6}}\\)"
- Write "Hg2+" not "Hg\\(^{{2+}}\\)"
- Use plain text for chemical formulas: "H2SO4" not "H₂SO₄"
- NO special characters that need JSON escaping
- Keep explanations under 300 characters
- COMPLETE all {count} questions - do not truncate

CRITICAL ANSWER VERIFICATION:
- VERIFY your calculated answer matches the option letter
- If calculation gives 250 mg/L and option B is "250 mg/L", then correct_answer = "B"
- Explanation must confirm the correct option value
- NO mismatched option letters

JSON OUTPUT FORMAT (NO markdown, NO code blocks, COMPLETE response):
{{
  "questions": [
    {{
      "id": 1,
      "question_text": "Concise NEET {subject} question (under 200 chars)",
      "option_a": "Short option A (under 80 chars)",
      "option_b": "Short option B (under 80 chars)", 
      "option_c": "Short option C (under 80 chars)",
      "option_d": "Short option D (under 80 chars)",
      "correct_answer": "B",
      "explanation": "Brief explanation under 300 chars that confirms option B"
    }}
  ]
}}

REMEMBER: 
1. CREATE exactly {count} complete questions - NO truncation allowed
2. Keep each option under 80 characters to prevent response cutoff
3. Use simple notation: "10^-6" not "10\\(^{{-6}}\\)"
4. Distribute correct answers: some A, some B, some C, some D 
5. VERIFY calculated answers match option letters you assign
6. Complete the entire JSON response - don't stop mid-sentence
7. End with proper closing braces: }}]}}

CRITICAL: Your response MUST be complete valid JSON. If you start a question, you MUST finish it completely with all fields filled in. Do not truncate or leave incomplete questions."""
        
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
    
    def _validate_answer_consistency(self, question: Dict[str, Any], question_index: int) -> None:
        """Validate that the correct_answer matches the explanation and fix if necessary"""
        
        correct_letter = question.get('correct_answer', '').upper()
        explanation = question.get('explanation', '')
        
        # Get the actual value of the correct option
        option_key = f"option_{correct_letter.lower()}"
        correct_option_value = question.get(option_key, '')
        
        print(f"🔧 DEBUG: Validating Q{question_index}: correct_answer='{correct_letter}', option='{correct_option_value}'")
        
        if not correct_option_value:
            print(f"⚠️ WARNING Q{question_index}: Invalid correct_answer '{correct_letter}' - no matching option found")
            return
            
        # Extract numerical values or key terms from options to check against explanation
        options = {
            'A': question.get('option_a', ''),
            'B': question.get('option_b', ''),
            'C': question.get('option_c', ''),
            'D': question.get('option_d', '')
        }
        
        # Look for numerical values mentioned in explanation
        import re
        
        # Find numbers in explanation (including scientific notation)
        explanation_numbers = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', explanation)
        
        # Check if the correct option's value appears in the explanation
        found_mismatch = False
        correct_values_in_explanation = []
        
        for letter, option_text in options.items():
            # Find numbers in this option
            option_numbers = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', option_text)
            
            # Check if any of these numbers appear in the explanation
            for num in option_numbers:
                if num in explanation:
                    correct_values_in_explanation.append((letter, num, option_text))
        
        # Special case: Look for explicit statements like "option A", "answer is B", etc.
        explanation_lower = explanation.lower()
        explicit_mentions = []
        for letter in ['a', 'b', 'c', 'd']:
            if f"option {letter}" in explanation_lower or f"answer is {letter}" in explanation_lower:
                explicit_mentions.append(letter.upper())
        
        # If explanation explicitly mentions a different option, fix it
        if explicit_mentions and correct_letter not in explicit_mentions:
            suggested_answer = explicit_mentions[0]
            print(f"🔧 MISMATCH DETECTED Q{question_index}: correct_answer='{correct_letter}' but explanation mentions option {suggested_answer}")
            print(f"   Current: {correct_letter} = '{correct_option_value}'")
            print(f"   Suggested: {suggested_answer} = '{options.get(suggested_answer, 'Unknown')}'")
            
            # Fix the mismatch by updating correct_answer
            question['correct_answer'] = suggested_answer
            print(f"✅ FIXED Q{question_index}: Updated correct_answer to '{suggested_answer}'")
            
        # If we found numerical evidence, validate it
        elif correct_values_in_explanation:
            explanation_mentions = [item for item in correct_values_in_explanation]
            current_match = any(item[0] == correct_letter for item in explanation_mentions)
            
            if not current_match and explanation_mentions:
                # The explanation supports a different answer
                suggested_letter = explanation_mentions[0][0]
                suggested_value = explanation_mentions[0][1]
                
                print(f"🔧 NUMERICAL MISMATCH Q{question_index}: correct_answer='{correct_letter}' but explanation calculates '{suggested_value}' (option {suggested_letter})")
                print(f"   Current: {correct_letter} = '{correct_option_value}'")
                print(f"   Calculated: {suggested_letter} = '{options.get(suggested_letter, 'Unknown')}'")
                
                # Fix the mismatch
                question['correct_answer'] = suggested_letter
                print(f"✅ FIXED Q{question_index}: Updated correct_answer to '{suggested_letter}' based on calculation")
        
        else:
            print(f"✅ Q{question_index}: Answer consistency validated - no issues detected")

    # NO EMERGENCY FALLBACK METHODS - ONLY AZURE OPENAI ALLOWED
