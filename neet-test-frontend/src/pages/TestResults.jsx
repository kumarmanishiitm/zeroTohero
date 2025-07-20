import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTest } from '../context/TestContext';
import { testAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  Trophy,
  Clock,
  Target,
  TrendingUp,
  CheckCircle,
  XCircle,
  BookOpen,
  RotateCcw,
  Home,
  ChevronRight,
  Award,
  AlertCircle
} from 'lucide-react';

const TestResults = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const { testResults: contextTestResults, dispatch } = useTest();
  
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAnswers, setShowAnswers] = useState(false);

  useEffect(() => {
    if (contextTestResults && contextTestResults.test_id == testId) {
      setResults(contextTestResults);
      setLoading(false);
    } else {
      fetchResults();
    }
  }, [testId, contextTestResults]);

  const fetchResults = async () => {
    try {
      const response = await testAPI.getTestResults(testId);
      if (response.data.success) {
        setResults(response.data);
        dispatch({ type: 'SET_TEST_RESULTS', payload: response.data });
      } else {
        toast.error('Failed to load test results');
        navigate('/test-selection');
      }
    } catch (error) {
      console.error('Error fetching results:', error);
      toast.error('Failed to load test results');
      navigate('/test-selection');
    } finally {
      setLoading(false);
    }
  };

  const handleRetakeTest = () => {
    dispatch({ type: 'RESET_TEST' });
    navigate('/test-selection');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner text="Loading results..." />
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Results Not Found</h2>
        <p className="text-gray-600 mb-4">Unable to load test results.</p>
        <Link to="/test-selection" className="btn-primary">
          Take Another Test
        </Link>
      </div>
    );
  }

  const { results: testResults, performance_analysis, answer_details } = results;
  const scorePercentage = testResults.score_percentage;
  
  const getGradeColor = (grade) => {
    switch (grade) {
      case 'Excellent': return 'text-green-600 bg-green-50 border-green-200';
      case 'Good': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'Average': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Below Average': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'Poor': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 75) return 'text-blue-600';
    if (percentage >= 60) return 'text-yellow-600';
    if (percentage >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className={`w-20 h-20 rounded-full flex items-center justify-center ${
            scorePercentage >= 75 ? 'bg-green-100' : scorePercentage >= 60 ? 'bg-yellow-100' : 'bg-red-100'
          }`}>
            {scorePercentage >= 75 ? (
              <Trophy className={`w-10 h-10 ${getScoreColor(scorePercentage)}`} />
            ) : (
              <Target className={`w-10 h-10 ${getScoreColor(scorePercentage)}`} />
            )}
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Test Results</h1>
        <p className="text-gray-600">
          {results.subject} {results.topic && `• ${results.topic}`}
        </p>
      </div>

      {/* Score Overview */}
      <div className="card">
        <div className="text-center space-y-6">
          <div className="space-y-2">
            <div className={`text-6xl font-bold ${getScoreColor(scorePercentage)}`}>
              {Math.round(scorePercentage)}%
            </div>
            <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full border ${getGradeColor(testResults.grade)}`}>
              <Award className="w-4 h-4" />
              <span className="font-medium">{testResults.grade}</span>
            </div>
          </div>
          
          <div className="grid md:grid-cols-5 gap-4">
            <div className="space-y-1">
              <div className="text-2xl font-bold text-green-600">{testResults.correct_answers}</div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-red-600">{testResults.wrong_answers || (testResults.total_questions - testResults.correct_answers - (testResults.not_attempted || 0))}</div>
              <div className="text-sm text-gray-600">Wrong</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-500">{testResults.not_attempted || 0}</div>
              <div className="text-sm text-gray-600">Not Attempted</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-gray-600">{testResults.total_questions}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-blue-600">{testResults.time_taken_minutes}m</div>
              <div className="text-sm text-gray-600">Time Taken</div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Scoring Breakdown */}
      <div className="card space-y-4">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
          <Award className="w-5 h-5 text-primary-600" />
          <span>Detailed Scoring Breakdown</span>
        </h2>
        
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">NEET Scoring System</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Correct Answer:</span>
                  <span className="font-medium text-green-600">+4 marks</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Wrong Answer:</span>
                  <span className="font-medium text-red-600">-1 mark</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Not Attempted:</span>
                  <span className="font-medium text-gray-600">0 marks</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Your Score Calculation</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Correct ({testResults.correct_answers} × 4):</span>
                  <span className="font-medium text-green-600">+{testResults.correct_answers * 4} marks</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Wrong ({testResults.wrong_answers || (testResults.total_questions - testResults.correct_answers - (testResults.not_attempted || 0))} × 1):</span>
                  <span className="font-medium text-red-600">-{(testResults.wrong_answers || (testResults.total_questions - testResults.correct_answers - (testResults.not_attempted || 0))) * 1} marks</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Not Attempted ({testResults.not_attempted || 0}):</span>
                  <span className="font-medium text-gray-600">0 marks</span>
                </div>
                <hr className="border-gray-300" />
                <div className="flex justify-between font-semibold">
                  <span className="text-gray-900">Total Score:</span>
                  <span className={`${(testResults.neet_score || (testResults.correct_answers * 4 - (testResults.wrong_answers || (testResults.total_questions - testResults.correct_answers - (testResults.not_attempted || 0))))) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {testResults.neet_score || (testResults.correct_answers * 4 - (testResults.wrong_answers || (testResults.total_questions - testResults.correct_answers - (testResults.not_attempted || 0))))} / {testResults.max_score || (testResults.total_questions * 4)} marks
                  </span>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Percentage:</span>
                  <span>{testResults.score_percentage?.toFixed(1) || '0.0'}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Analysis */}
      {performance_analysis && (
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <span>Performance Analysis</span>
          </h2>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800">{performance_analysis.grade_message}</p>
          </div>
          
          {performance_analysis.time_message && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <Clock className="w-5 h-5 text-yellow-600 mt-0.5" />
                <p className="text-yellow-800">{performance_analysis.time_message}</p>
              </div>
            </div>
          )}
          
          {performance_analysis.recommendations && performance_analysis.recommendations.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-medium text-gray-900">Recommendations:</h3>
              <ul className="space-y-2">
                {performance_analysis.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <ChevronRight className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Detailed Answers */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-primary-600" />
            <span>Detailed Solutions</span>
          </h2>
          <button
            onClick={() => setShowAnswers(!showAnswers)}
            className="btn-secondary"
          >
            {showAnswers ? 'Hide' : 'Show'} Answers
          </button>
        </div>
        
        {showAnswers && (
          <div className="space-y-6">
            {answer_details.map((answer, index) => (
              <div key={answer.question_id} className="border border-gray-200 rounded-lg p-4 space-y-4">
                <div className="flex items-start justify-between">
                  <h3 className="font-medium text-gray-900">
                    Question {index + 1}
                  </h3>
                  <div className="flex items-center space-x-2">
                    {answer.is_correct ? (
                      <div className="flex items-center space-x-1 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Correct</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-1 text-red-600">
                        <XCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Incorrect</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <p className="text-gray-900">{answer.question_text}</p>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-700">Your Answer:</h4>
                    <div className={`p-2 rounded-lg ${
                      answer.is_correct 
                        ? 'bg-green-50 border border-green-200 text-green-800' 
                        : 'bg-red-50 border border-red-200 text-red-800'
                    }`}>
                      {answer.user_answer}: {answer.options && answer.user_answer ? answer.options[answer.user_answer.toUpperCase()] || 'N/A' : 'N/A'}
                    </div>
                  </div>
                  
                  {!answer.is_correct && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-700">Correct Answer:</h4>
                      <div className="p-2 rounded-lg bg-green-50 border border-green-200 text-green-800">
                        {answer.correct_answer}: {answer.options && answer.correct_answer ? answer.options[answer.correct_answer.toUpperCase()] || 'N/A' : 'N/A'}
                      </div>
                    </div>
                  )}
                </div>
                
                {answer.explanation && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">Explanation:</h4>
                    <p className="text-blue-800 text-sm">{answer.explanation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <button
          onClick={handleRetakeTest}
          className="btn-primary flex items-center space-x-2"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Take Another Test</span>
        </button>
        
        <Link
          to="/"
          className="btn-secondary flex items-center space-x-2"
        >
          <Home className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>
      </div>
    </div>
  );
};

export default TestResults;
