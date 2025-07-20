import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTest } from '../context/TestContext';
import { testAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  Atom,
  FlaskConical,
  Dna,
  BookOpen,
  Target,
  Clock,
  Play,
  Settings,
  ChevronRight
} from 'lucide-react';

const TestSelection = () => {
  const navigate = useNavigate();
  const context = useTest();
  const { selectedSubject, selectedTopic, subjects, topics, questionCount, testType, dispatch } = context;
  const [loading, setLoading] = useState(false);
  const [startingTest, setStartingTest] = useState(false);

  const subjectIcons = {
    'Physics': <Atom className="w-12 h-12" />,
    'Chemistry': <FlaskConical className="w-12 h-12" />,
    'Biology': <Dna className="w-12 h-12" />
  };

  const subjectColors = {
    'Physics': 'border-blue-500 bg-blue-50 text-blue-700',
    'Chemistry': 'border-green-500 bg-green-50 text-green-700',
    'Biology': 'border-purple-500 bg-purple-50 text-purple-700'
  };

  useEffect(() => {
    fetchSubjects();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      fetchTopics(selectedSubject.id);
    }
  }, [selectedSubject]);

  const fetchSubjects = async () => {
    setLoading(true);
    try {
      const response = await testAPI.getSubjects();
      if (response.data.success) {
        dispatch({ type: 'SET_SUBJECTS', payload: response.data.subjects });
      } else {
        toast.error('Failed to load subjects');
      }
    } catch (error) {
      console.error('Error fetching subjects:', error);
      toast.error('Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  const fetchTopics = async (subjectId) => {
    try {
      const response = await testAPI.getTopicsBySubject(subjectId);
      if (response.data.success) {
        dispatch({ type: 'SET_TOPICS', payload: response.data.topics });
      } else {
        toast.error('Failed to load topics');
      }
    } catch (error) {
      console.error('Error fetching topics:', error);
      toast.error('Failed to load topics');
    }
  };

  const handleSubjectSelect = (subject) => {
    dispatch({ type: 'SET_SELECTED_SUBJECT', payload: subject });
    dispatch({ type: 'SET_TEST_TYPE', payload: 'topic' });
  };

  const handleTopicSelect = (topic) => {
    dispatch({ type: 'SET_SELECTED_TOPIC', payload: topic });
  };

  const handleTestTypeChange = (testType) => {
    dispatch({ type: 'SET_TEST_TYPE', payload: testType });
    if (testType !== 'topic') {
      dispatch({ type: 'SET_SELECTED_TOPIC', payload: null });
    }
  };

  const handleQuestionCountChange = (count) => {
    dispatch({ type: 'SET_QUESTION_COUNT', payload: count });
  };

  const startTest = async () => {
    if (!selectedSubject) {
      toast.error('Please select a subject');
      return;
    }

    if (testType === 'topic' && !selectedTopic) {
      toast.error('Please select a topic');
      return;
    }

    setStartingTest(true);
    try {
      const testData = {
        subject_id: selectedSubject.id,
        question_count: questionCount
      };

      if (testType === 'topic' && selectedTopic) {
        testData.topic_id = selectedTopic.id;
      }

      const response = await testAPI.startTest(testData);
      
      if (response.data.success) {
        dispatch({ type: 'SET_CURRENT_TEST', payload: response.data });
        toast.success('Test started successfully!');
        navigate(`/test/${response.data.test_id}`);
      } else {
        toast.error(response.data.message || 'Failed to start test');
      }
    } catch (error) {
      console.error('Error starting test:', error);
      toast.error('Failed to start test');
    } finally {
      setStartingTest(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner text="Loading subjects..." />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Configure Your Test</h1>
        <p className="text-gray-600">
          Select subject, topic, and question count to customize your practice session
        </p>
      </div>

      {/* Subject Selection */}
      <div className="card space-y-6">
        <div className="flex items-center space-x-3">
          <BookOpen className="w-6 h-6 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Step 1: Choose Subject</h2>
        </div>
        
        <div className="grid md:grid-cols-3 gap-4">
          {subjects.map((subject) => (
            <div
              key={subject.id}
              onClick={() => handleSubjectSelect(subject)}
              className={`subject-card text-center space-y-4 ${
                selectedSubject?.id === subject.id ? 'selected' : ''
              }`}
            >
              <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center ${
                subjectColors[subject.name] || 'border-gray-500 bg-gray-50 text-gray-700'
              }`}>
                {subjectIcons[subject.name] || <BookOpen className="w-12 h-12" />}
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{subject.name}</h3>
                <p className="text-sm text-gray-600">
                  {subject.name === 'Physics' && 'Mechanics, Thermodynamics, Optics...'}
                  {subject.name === 'Chemistry' && 'Organic, Inorganic, Physical...'}
                  {subject.name === 'Biology' && 'Botany, Zoology, Genetics...'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Type Selection */}
      {selectedSubject && (
        <div className="card space-y-6">
          <div className="flex items-center space-x-3">
            <Target className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Step 2: Choose Test Type</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div
              onClick={() => handleTestTypeChange('topic')}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                testType === 'topic'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
              }`}
            >
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-900">Topic-wise Test</h3>
                <p className="text-sm text-gray-600">
                  Focus on specific topics to target your weak areas
                </p>
              </div>
            </div>
            
            <div
              onClick={() => handleTestTypeChange('subject')}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                testType === 'subject'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
              }`}
            >
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-900">Full Subject Test</h3>
                <p className="text-sm text-gray-600">
                  Mixed questions from all topics in {selectedSubject.name}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Topic Selection */}
      {selectedSubject && testType === 'topic' && (
        <div className="card space-y-6">
          <div className="flex items-center space-x-3">
            <Target className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Step 3: Select Topic</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-3">
            {topics.map((topic) => (
              <div
                key={topic.id}
                onClick={() => handleTopicSelect(topic)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                  selectedTopic?.id === topic.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                }`}
              >
                <div className="space-y-1">
                  <h3 className="font-medium text-gray-900">{topic.name}</h3>
                  {topic.description && (
                    <p className="text-sm text-gray-600">{topic.description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Question Count Selection */}
      {selectedSubject && (testType === 'subject' || selectedTopic) && (
        <div className="card space-y-6">
          <div className="flex items-center space-x-3">
            <Settings className="w-6 h-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Step {testType === 'topic' ? '4' : '3'}: Number of Questions</h2>
          </div>
          
          <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
            {[5, 10, 15, 20, 25, 30].map((count) => (
              <button
                key={count}
                onClick={() => handleQuestionCountChange(count)}
                className={`p-3 border-2 rounded-lg transition-all duration-200 ${
                  questionCount === count
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                }`}
              >
                <div className="text-center">
                  <div className="font-semibold">{count}</div>
                  <div className="text-xs text-gray-600">{count} mins</div>
                </div>
              </button>
            ))}
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium">Timer Information</p>
                <p>You'll have 1 minute per question. Test will auto-submit when time expires.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Start Test Button */}
      {selectedSubject && (testType === 'subject' || selectedTopic) && (
        <div className="card">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="text-center md:text-left">
              <h3 className="text-lg font-semibold text-gray-900">Ready to Start?</h3>
              <p className="text-gray-600">
                {testType === 'topic' 
                  ? `${selectedTopic?.name} • ${questionCount} questions • ${questionCount} minutes`
                  : `${selectedSubject?.name} Full Test • ${questionCount} questions • ${questionCount} minutes`
                }
              </p>
            </div>
            
            <button
              onClick={startTest}
              disabled={startingTest}
              className="btn-primary flex items-center space-x-2 text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {startingTest ? (
                <>
                  <div className="w-5 h-5 animate-spin border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Starting...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Start Test</span>
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestSelection;
