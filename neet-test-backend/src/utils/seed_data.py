"""
Sample data seeder for NEET Test Backend
This file contains sample questions for testing purposes.
"""

from models.question import Question, DifficultyLevel
from models.subject import Subject
from models.topic import Topic
from database.connection import db

def seed_sample_questions():
    """Seed the database with sample questions for all subjects"""
    
    try:
        # Physics Questions
        physics_questions = [
            {
                'question_text': 'What is the SI unit of electric current?',
                'option_a': 'Volt',
                'option_b': 'Ampere', 
                'option_c': 'Ohm',
                'option_d': 'Watt',
                'correct_answer': 'B',
                'explanation': 'The SI unit of electric current is Ampere (A), named after André-Marie Ampère.',
                'difficulty': DifficultyLevel.EASY,
                'subject': 'Physics',
                'topic': 'Electromagnetism'
            },
            {
                'question_text': 'The escape velocity of Earth is approximately:',
                'option_a': '11.2 km/s',
                'option_b': '9.8 km/s',
                'option_c': '15.0 km/s',
                'option_d': '7.9 km/s',
                'correct_answer': 'A',
                'explanation': 'The escape velocity of Earth is approximately 11.2 km/s, which is the minimum speed needed for an object to escape Earth\'s gravitational pull.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Physics',
                'topic': 'Mechanics'
            },
            {
                'question_text': 'Which phenomenon explains the bending of light around corners?',
                'option_a': 'Reflection',
                'option_b': 'Refraction',
                'option_c': 'Diffraction',
                'option_d': 'Dispersion',
                'correct_answer': 'C',
                'explanation': 'Diffraction is the phenomenon where light bends around corners or obstacles, demonstrating its wave nature.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Physics',
                'topic': 'Optics'
            },
            {
                'question_text': 'At what temperature do Celsius and Fahrenheit scales meet?',
                'option_a': '-40°',
                'option_b': '-32°',
                'option_c': '0°',
                'option_d': '100°',
                'correct_answer': 'A',
                'explanation': 'Celsius and Fahrenheit scales meet at -40°, where -40°C = -40°F.',
                'difficulty': DifficultyLevel.HARD,
                'subject': 'Physics',
                'topic': 'Thermodynamics'
            },
            {
                'question_text': 'What is the frequency of a pendulum with a period of 2 seconds?',
                'option_a': '0.5 Hz',
                'option_b': '1 Hz',
                'option_c': '2 Hz',
                'option_d': '4 Hz',
                'correct_answer': 'A',
                'explanation': 'Frequency = 1/Period. If T = 2 seconds, then f = 1/2 = 0.5 Hz.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Physics',
                'topic': 'Oscillations'
            }
        ]
        
        # Chemistry Questions
        chemistry_questions = [
            {
                'question_text': 'What is the valency of carbon in methane (CH₄)?',
                'option_a': '2',
                'option_b': '3',
                'option_c': '4',
                'option_d': '1',
                'correct_answer': 'C',
                'explanation': 'Carbon has a valency of 4 in methane, as it forms four bonds with hydrogen atoms.',
                'difficulty': DifficultyLevel.EASY,
                'subject': 'Chemistry',
                'topic': 'Organic Chemistry'
            },
            {
                'question_text': 'Which noble gas has the electronic configuration [Ar] 3d¹⁰ 4s² 4p⁶?',
                'option_a': 'Argon',
                'option_b': 'Krypton',
                'option_c': 'Xenon',
                'option_d': 'Radon',
                'correct_answer': 'B',
                'explanation': 'Krypton (Kr) has the electronic configuration [Ar] 3d¹⁰ 4s² 4p⁶, with atomic number 36.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Chemistry',
                'topic': 'Inorganic Chemistry'
            },
            {
                'question_text': 'The rate of reaction doubles when temperature increases by 10°C. This is explained by:',
                'option_a': 'Le Chatelier\'s principle',
                'option_b': 'Arrhenius equation',
                'option_c': 'Hess\'s law',
                'option_d': 'Charles\' law',
                'correct_answer': 'B',
                'explanation': 'The Arrhenius equation explains how reaction rate depends on temperature. The rule of thumb is that reaction rate doubles with every 10°C increase.',
                'difficulty': DifficultyLevel.HARD,
                'subject': 'Chemistry',
                'topic': 'Physical Chemistry'
            },
            {
                'question_text': 'Which of the following is a biodegradable polymer?',
                'option_a': 'Polythene',
                'option_b': 'PVC',
                'option_c': 'PHBV',
                'option_d': 'Teflon',
                'correct_answer': 'C',
                'explanation': 'PHBV (Polyhydroxybutyrate-co-valerate) is a biodegradable polymer, unlike synthetic polymers like polythene, PVC, and Teflon.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Chemistry',
                'topic': 'Polymers'
            },
            {
                'question_text': 'The primary pollutant in photochemical smog is:',
                'option_a': 'CO₂',
                'option_b': 'SO₂',
                'option_c': 'NO₂',
                'option_d': 'CH₄',
                'correct_answer': 'C',
                'explanation': 'NO₂ (nitrogen dioxide) is the primary pollutant in photochemical smog, which forms ozone in the presence of sunlight.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Chemistry',
                'topic': 'Environmental Chemistry'
            }
        ]
        
        # Biology Questions  
        biology_questions = [
            {
                'question_text': 'Which organelle is responsible for protein synthesis?',
                'option_a': 'Mitochondria',
                'option_b': 'Ribosome',
                'option_c': 'Golgi apparatus',
                'option_d': 'Lysosome',
                'correct_answer': 'B',
                'explanation': 'Ribosomes are responsible for protein synthesis by translating mRNA into polypeptide chains.',
                'difficulty': DifficultyLevel.EASY,
                'subject': 'Biology',
                'topic': 'Cell Biology'
            },
            {
                'question_text': 'The genetic code is said to be degenerate because:',
                'option_a': 'Multiple codons code for the same amino acid',
                'option_b': 'One codon codes for multiple amino acids',
                'option_c': 'Codons are read in overlapping manner',
                'option_d': 'Stop codons are present',
                'correct_answer': 'A',
                'explanation': 'The genetic code is degenerate because multiple codons can code for the same amino acid, providing redundancy.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Biology',
                'topic': 'Genetics'
            },
            {
                'question_text': 'Which hormone regulates blood glucose levels?',
                'option_a': 'Thyroxine',
                'option_b': 'Insulin',
                'option_c': 'Adrenaline',
                'option_d': 'Growth hormone',
                'correct_answer': 'B',
                'explanation': 'Insulin, produced by beta cells of the pancreas, regulates blood glucose levels by promoting glucose uptake by cells.',
                'difficulty': DifficultyLevel.EASY,
                'subject': 'Biology',
                'topic': 'Human Physiology'
            },
            {
                'question_text': 'In C4 plants, the primary CO₂ acceptor is:',
                'option_a': 'RuBP',
                'option_b': 'PEP',
                'option_c': 'OAA',
                'option_d': 'Malate',
                'correct_answer': 'B',
                'explanation': 'In C4 plants, phosphoenolpyruvate (PEP) is the primary CO₂ acceptor in the mesophyll cells.',
                'difficulty': DifficultyLevel.HARD,
                'subject': 'Biology',
                'topic': 'Plant Physiology'
            },
            {
                'question_text': 'Which of the following is an example of ex-situ conservation?',
                'option_a': 'National parks',
                'option_b': 'Wildlife sanctuaries',
                'option_c': 'Seed banks',
                'option_d': 'Biosphere reserves',
                'correct_answer': 'C',
                'explanation': 'Seed banks are an example of ex-situ conservation where organisms are conserved outside their natural habitat.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Biology',
                'topic': 'Ecology'
            },
            {
                'question_text': 'The theory of evolution by natural selection was proposed by:',
                'option_a': 'Gregor Mendel',
                'option_b': 'Charles Darwin',
                'option_c': 'Lamarck',
                'option_d': 'Hugo de Vries',
                'correct_answer': 'B',
                'explanation': 'Charles Darwin proposed the theory of evolution by natural selection in his book "On the Origin of Species" (1859).',
                'difficulty': DifficultyLevel.EASY,
                'subject': 'Biology',
                'topic': 'Evolution'
            },
            {
                'question_text': 'Parthenogenesis is a type of:',
                'option_a': 'Sexual reproduction',
                'option_b': 'Asexual reproduction',
                'option_c': 'Binary fission',
                'option_d': 'Budding',
                'correct_answer': 'B',
                'explanation': 'Parthenogenesis is a type of asexual reproduction where offspring develop from unfertilized eggs.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Biology',
                'topic': 'Reproduction'
            },
            {
                'question_text': 'PCR technique is used for:',
                'option_a': 'DNA sequencing',
                'option_b': 'DNA amplification',
                'option_c': 'Protein synthesis',
                'option_d': 'Gene cloning',
                'correct_answer': 'B',
                'explanation': 'PCR (Polymerase Chain Reaction) is used for DNA amplification, making millions of copies of a specific DNA sequence.',
                'difficulty': DifficultyLevel.MEDIUM,
                'subject': 'Biology',
                'topic': 'Biotechnology'
            }
        ]
        
        # Combine all questions
        all_questions = physics_questions + chemistry_questions + biology_questions
        
        # Add questions to database
        for q_data in all_questions:
            # Get subject and topic IDs
            subject = Subject.query.filter_by(name=q_data['subject']).first()
            topic = Topic.query.filter_by(name=q_data['topic'], subject_id=subject.id).first()
            
            if subject and topic:
                # Check if question already exists
                existing = Question.query.filter_by(
                    question_text=q_data['question_text'],
                    subject_id=subject.id
                ).first()
                
                if not existing:
                    question = Question(
                        question_text=q_data['question_text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data['explanation'],
                        difficulty=q_data['difficulty'],
                        subject_id=subject.id,
                        topic_id=topic.id
                    )
                    db.session.add(question)
        
        db.session.commit()
        print(f"✓ Successfully seeded {len(all_questions)} sample questions")
        
    except Exception as e:
        print(f"Error seeding questions: {e}")
        db.session.rollback()

def create_sample_user():
    """Create a sample user for testing"""
    try:
        from src.models.user import User
        
        # Check if sample user exists
        existing_user = User.query.filter_by(username='student').first()
        if not existing_user:
            sample_user = User(
                username='student',
                email='student@example.com',
                password='password123'
            )
            db.session.add(sample_user)
            db.session.commit()
            print("✓ Created sample user: username='student', password='password123'")
        
    except Exception as e:
        print(f"Error creating sample user: {e}")
        db.session.rollback()

if __name__ == '__main__':
    from src.main import create_app
    
    app = create_app()
    with app.app_context():
        seed_sample_questions()
        create_sample_user()
        print("Database seeding completed!")
