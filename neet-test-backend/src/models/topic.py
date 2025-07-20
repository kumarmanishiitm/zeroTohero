from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from database.connection import db

class Topic(db.Model):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    def __init__(self, name, subject_id, description=None, is_active=True):
        self.name = name
        self.subject_id = subject_id
        self.description = description
        self.is_active = is_active

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject_id': self.subject_id,
            'is_active': self.is_active
        }

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', subject_id={self.subject_id})>"

# Pre-defined topics for each subject
NEET_TOPICS = {
    "Physics": [
        {"name": "Mechanics", "description": "Motion, force, work, energy, and momentum"},
        {"name": "Thermodynamics", "description": "Heat, temperature, and energy transfer"},
        {"name": "Optics", "description": "Light, reflection, refraction, and optical instruments"},
        {"name": "Electromagnetism", "description": "Electric and magnetic fields, circuits"},
        {"name": "Modern Physics", "description": "Atomic structure, quantum mechanics, radioactivity"},
        {"name": "Waves", "description": "Sound waves, electromagnetic waves"},
        {"name": "Oscillations", "description": "Simple harmonic motion, pendulum"}
    ],
    "Chemistry": [
        {"name": "Organic Chemistry", "description": "Carbon compounds, hydrocarbons, functional groups"},
        {"name": "Inorganic Chemistry", "description": "Metals, non-metals, periodic table, chemical bonding"},
        {"name": "Physical Chemistry", "description": "Chemical kinetics, thermochemistry, equilibrium"},
        {"name": "Coordination Chemistry", "description": "Complex compounds and coordination bonds"},
        {"name": "Environmental Chemistry", "description": "Pollution, green chemistry"},
        {"name": "Biomolecules", "description": "Carbohydrates, proteins, lipids, nucleic acids"},
        {"name": "Polymers", "description": "Natural and synthetic polymers"}
    ],
    "Biology": [
        {"name": "Cell Biology", "description": "Cell structure, organelles, cellular processes"},
        {"name": "Genetics", "description": "Heredity, DNA, RNA, genetic engineering"},
        {"name": "Human Physiology", "description": "Body systems, circulation, respiration, digestion"},
        {"name": "Plant Physiology", "description": "Photosynthesis, plant nutrition, growth"},
        {"name": "Ecology", "description": "Ecosystems, biodiversity, environmental biology"},
        {"name": "Evolution", "description": "Origin of life, natural selection, speciation"},
        {"name": "Reproduction", "description": "Sexual and asexual reproduction, development"},
        {"name": "Biotechnology", "description": "Genetic engineering, applications of biotechnology"}
    ]
}