import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTest } from '../context/TestContext';
import { testAPI } from '../services/api';
import Timer from '../components/Timer';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  ChevronLeft,
  ChevronRight,
  Flag,
  Clock,
  AlertTriangle,
  CheckCircle,
  Send
} from 'lucide-react';

const TestInterface = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const { currentTest, dispatch } = useTest();
  
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [testData, setTestData] = useState(null);
  const [timeUp, setTimeUp] = useState(false);
  const [testSubmitted, setTestSubmitted] = useState(false);
  const [warningCount, setWarningCount] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submissionStartedRef = useRef(false);

  useEffect(() => {
    if (currentTest && currentTest.test_id == testId) {
      setTestData(currentTest);
      setQuestions(currentTest.questions || []);
      setLoading(false);
    } else {
      // If no current test in state, could fetch test details here
      setLoading(false);
      toast.error('Test data not found');
      navigate('/test-selection');
    }
  }, [testId, currentTest, navigate]);

  // Navigation prevention after test submission
  useEffect(() => {
    if (testSubmitted) {
      // Push a dummy state to prevent going back
      window.history.pushState(null, '', window.location.href);
      
      const handlePopState = (event) => {
        window.history.pushState(null, '', window.location.href);
        toast.error('Navigation is restricted after test submission');
      };

      window.addEventListener('popstate', handlePopState);
      
      // Prevent page refresh
      const handleBeforeUnload = (event) => {
        event.preventDefault();
        event.returnValue = 'Test has been submitted. Are you sure you want to leave?';
        return 'Test has been submitted. Are you sure you want to leave?';
      };

      window.addEventListener('beforeunload', handleBeforeUnload);

      return () => {
        window.removeEventListener('popstate', handlePopState);
        window.removeEventListener('beforeunload', handleBeforeUnload);
      };
    }
  }, [testSubmitted]);

  // Window switching prevention with warning system
  useEffect(() => {
    if (testSubmitted || isSubmitting) return; // Don't track if test is already submitted or submitting

    const MAX_WARNINGS = 2; // Auto-submit after 2 warnings

    const handleVisibilityChange = () => {
      if (document.hidden && !isSubmitting && !testSubmitted) {
        const newWarningCount = warningCount + 1;
        setWarningCount(newWarningCount);
        
        if (newWarningCount === 1) {
          toast.error('⚠️ Warning: Don\'t switch windows during test! (1/2 warnings)');
        } else if (newWarningCount === 2) {
          toast.error('❌ Final warning: Switching windows again will auto-submit! (2/2 warnings)');
        } else if (newWarningCount > MAX_WARNINGS) {
          toast.error('🚨 Test auto-submitted due to repeated window switching!');
          handleSubmitTest(true); // Auto-submit the test
        }
      }
    };

    const handleBlur = () => {
      if (!document.hidden && !isSubmitting && !testSubmitted) {
        // Window lost focus but tab is still visible (e.g., clicked on another app)
        const newWarningCount = warningCount + 1;
        setWarningCount(newWarningCount);
        
        if (newWarningCount === 1) {
          toast.error('⚠️ Warning: Stay focused on the test! (1/2 warnings)');
        } else if (newWarningCount === 2) {
          toast.error('❌ Final warning: Losing focus again will auto-submit! (2/2 warnings)');
        } else if (newWarningCount > MAX_WARNINGS) {
          toast.error('🚨 Test auto-submitted due to repeated focus loss!');
          handleSubmitTest(true);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
    };
  }, [testSubmitted, warningCount, isSubmitting]);

  const currentQuestion = questions[currentQuestionIndex];

  const handleAnswerSelect = (optionKey) => {
    const questionId = currentQuestion.question_id || currentQuestion.id;
    setAnswers(prev => ({
      ...prev,
      [questionId]: {
        question_id: questionId,
        answer: optionKey,
        time_taken: Math.floor((Date.now() - testStartTime) / 1000) // Rough time tracking
      }
    }));
  };

  const handleClearAnswer = () => {
    const questionId = currentQuestion.question_id || currentQuestion.id;
    setAnswers(prev => {
      const newAnswers = { ...prev };
      delete newAnswers[questionId];
      return newAnswers;
    });
  };

  const testStartTime = testData ? new Date(testData.start_time).getTime() : Date.now();

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleQuestionJump = (index) => {
    setCurrentQuestionIndex(index);
  };

  const handleTimeUp = () => {
    // Prevent multiple time-up triggers
    if (timeUp || isSubmitting || testSubmitted || submissionStartedRef.current) {
      console.log('Time up already handled or test already submitting/submitted');
      return;
    }
    
    console.log('Time is up! Auto-submitting test...');
    setTimeUp(true);
    setIsSubmitting(true); // Set submitting flag immediately to prevent race conditions
    toast.error('Time is up! Auto-submitting test...');
    handleSubmitTest(true);
  };

  const handleSubmitTest = async (autoSubmit = false) => {
    // Prevent duplicate submissions using both state and ref
    if (isSubmitting || testSubmitted || submissionStartedRef.current) {
      console.log('Submission already in progress or test already submitted, ignoring duplicate request');
      return;
    }

    if (!autoSubmit && Object.keys(answers).length === 0) {
      toast.error('Please answer at least one question before submitting');
      return;
    }

    if (!autoSubmit) {
      const confirmed = window.confirm(
        `Are you sure you want to submit the test? You have answered ${Object.keys(answers).length} out of ${questions.length} questions.`
      );
      if (!confirmed) return;
    }

    // Set submission flags immediately to prevent race conditions
    submissionStartedRef.current = true;
    setIsSubmitting(true);
    console.log(`${autoSubmit ? 'Auto-' : 'Manual '}submitting test ${testId}...`);
    
    try {
      // Create answers array for ALL questions in the test, not just answered ones
      const answersArray = questions.map(question => {
        const questionId = question.question_id || question.id;
        const userAnswer = answers[questionId];
        
        if (userAnswer) {
          // User answered this question
          return userAnswer;
        } else {
          // User didn't answer this question
          return {
            question_id: questionId,
            answer: '',
            time_taken: 0
          };
        }
      });
      
      console.log('Submitting all questions:', answersArray);
      console.log('Total questions:', questions.length);
      console.log('Answered questions:', Object.keys(answers).length);
      
      // Pass both answers and test questions to backend
      const response = await testAPI.submitTest(testId, answersArray, questions);
      
      if (response.data.success) {
        setTestSubmitted(true);
        dispatch({ type: 'SET_TEST_RESULTS', payload: response.data });
        toast.success('Test submitted successfully!');
        navigate(`/results/${testId}`);
      } else {
        toast.error(response.data.message || 'Failed to submit test');
        console.error('Test submission failed:', response.data.message);
        setIsSubmitting(false);
        submissionStartedRef.current = false;
      }
    } catch (error) {
      console.error('Error submitting test:', error);
      
      // For auto-submit, still navigate to prevent user being stuck
      if (autoSubmit) {
        console.log('Auto-submit failed, but navigating to results anyway');
        toast.error('Auto-submit failed, but showing your results');
        setTestSubmitted(true); // Set as submitted to prevent further attempts
        navigate(`/results/${testId}`);
      } else {
        toast.error('Failed to submit test');
        setIsSubmitting(false);
        submissionStartedRef.current = false;
      }
    }
    // Don't reset submitting on success to prevent multiple attempts
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner text="Loading test..." />
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">No Questions Available</h2>
        <p className="text-gray-600">There was an issue loading the test questions.</p>
      </div>
    );
  }

  const getQuestionStatus = (questionId) => {
    if (answers[questionId]) return 'answered';
    return 'unanswered';
  };

  const answeredCount = Object.keys(answers).length;
  const unansweredCount = questions.length - answeredCount;

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 mb-6 rounded-lg shadow-sm">
        <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          <div className="text-center md:text-left">
            <h1 className="text-xl font-semibold text-gray-900">
              {testData?.subject || 'Test'} - Question {currentQuestionIndex + 1} of {questions.length}
            </h1>
            <p className="text-gray-600">
              Answered: {answeredCount} • Remaining: {unansweredCount}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {testData?.timer_seconds && !timeUp && (
              <Timer 
                duration={testData.timer_seconds} 
                onTimeUp={handleTimeUp}
                isActive={!isSubmitting}
              />
            )}
            
            {/* Warning Indicator */}
            {warningCount > 0 && !testSubmitted && (
              <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${
                warningCount === 1 ? 'bg-yellow-50 border-yellow-200 text-yellow-800' : 
                warningCount >= 2 ? 'bg-red-50 border-red-200 text-red-800' : ''
              }`}>
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {warningCount === 1 ? 'Warning 1/2' : 'Final Warning!'}
                </span>
              </div>
            )}
            
            <button
              onClick={() => handleSubmitTest(false)}
              disabled={isSubmitting}
              className="btn-success flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 animate-spin border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Test</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Question Panel */}
        <div className="lg:col-span-3 space-y-6">
          {/* Question Card */}
          <div className="card">
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  Question {currentQuestionIndex + 1}
                </h2>
                <div className="flex items-center space-x-2 text-sm">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">1 min per question</span>
                </div>
              </div>
              
              <div className="prose max-w-none">
                <p className="text-gray-900 text-lg leading-relaxed">
                  {currentQuestion.question_text}
                </p>
              </div>
              
              {/* Options */}
              <div className="space-y-3">
                {currentQuestion && ['A', 'B', 'C', 'D'].map((optionKey) => {
                  // Handle both data formats: nested options object or direct option_x fields
                  const optionText = currentQuestion.options 
                    ? currentQuestion.options[optionKey]
                    : currentQuestion[`option_${optionKey.toLowerCase()}`];
                  
                  const questionId = currentQuestion.question_id || currentQuestion.id;
                  const isSelected = answers[questionId]?.answer === optionKey;
                  
                  if (!optionText) return null;
                  
                  return (
                    <div
                      key={optionKey}
                      onClick={() => handleAnswerSelect(optionKey)}
                      className={`question-option ${isSelected ? 'selected' : ''}`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-sm font-medium ${
                          isSelected 
                            ? 'border-primary-500 bg-primary-500 text-white' 
                            : 'border-gray-300 text-gray-600'
                        }`}>
                          {optionKey}
                        </div>
                        <span className="text-gray-900">{optionText}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* Clear Answer Button */}
              {answers[currentQuestion.id] && (
                <div className="mt-4">
                  <button
                    onClick={handleClearAnswer}
                    className="px-4 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg border border-red-200 hover:border-red-300 transition-colors"
                  >
                    Clear Answer
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
              className="btn-secondary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>
            
            <div className="text-sm text-gray-600">
              {currentQuestionIndex + 1} of {questions.length}
            </div>
            
            <button
              onClick={handleNext}
              disabled={currentQuestionIndex === questions.length - 1}
              className="btn-secondary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Question Navigation Sidebar */}
        <div className="lg:col-span-1">
          <div className="card sticky top-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                <Flag className="w-4 h-4" />
                <span>Questions</span>
              </h3>
              
              <div className="grid grid-cols-5 gap-2">
                {questions.map((question, index) => {
                  const questionId = question.question_id || question.id;
                  const status = getQuestionStatus(questionId);
                  const isCurrentQuestion = index === currentQuestionIndex;
                  
                  return (
                    <button
                      key={`question-${index}`}
                      onClick={() => handleQuestionJump(index)}
                      className={`w-10 h-10 rounded-lg border-2 text-sm font-medium transition-all duration-200 ${
                        isCurrentQuestion
                          ? 'border-primary-600 bg-primary-600 text-white'
                          : status === 'answered'
                          ? 'border-success-500 bg-success-50 text-success-700 hover:bg-success-100'
                          : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                      }`}
                    >
                      {index + 1}
                    </button>
                  );
                })}
              </div>
              
              <div className="pt-4 border-t border-gray-200 space-y-2">
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-4 h-4 bg-success-500 rounded"></div>
                  <span className="text-gray-600">Answered ({answeredCount})</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-4 h-4 bg-gray-300 rounded"></div>
                  <span className="text-gray-600">Not Answered ({unansweredCount})</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-4 h-4 bg-primary-600 rounded"></div>
                  <span className="text-gray-600">Current Question</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestInterface;
