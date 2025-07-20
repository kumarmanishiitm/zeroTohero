import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTest } from '../context/TestContext';
import { testAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  Calendar,
  Clock,
  Trophy,
  TrendingUp,
  Eye,
  BarChart3,
  PieChart,
  Target,
  Award,
  BookOpen,
  ChevronRight,
  Filter,
  Search
} from 'lucide-react';

const TestHistory = () => {
  const navigate = useNavigate();
  const { user } = useTest();
  
  const [testHistory, setTestHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, physics, chemistry, biology
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchTestHistory();
    fetchAnalytics();
  }, [user, navigate]);

  const fetchTestHistory = async () => {
    try {
      console.log('Fetching test history...');
      const response = await testAPI.getUserTestHistory();
      console.log('Test history response:', response);
      
      if (response.data.success) {
        setTestHistory(response.data.tests || []);
      } else {
        console.error('Test history failed:', response.data.message);
        toast.error(response.data.message || 'Failed to load test history');
      }
    } catch (error) {
      console.error('Error fetching test history:', error);
      console.error('Error details:', error.response?.data);
      
      if (error.response?.status === 500) {
        toast.error('Server error - database may need migration. Check console for details.');
      } else if (error.response?.status === 401) {
        toast.error('Authentication failed. Please login again.');
        navigate('/login');
      } else {
        toast.error('Failed to load test history - check if backend is running');
      }
    }
  };

  const fetchAnalytics = async () => {
    try {
      console.log('Fetching analytics...');
      const response = await testAPI.getUserAnalytics();
      console.log('Analytics response:', response);
      
      if (response.data.success) {
        setAnalytics(response.data.analytics);
      } else {
        console.log('Analytics failed:', response.data.message);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      console.error('Analytics error details:', error.response?.data);
      // Don't show error toast for analytics as it's not critical
    } finally {
      setLoading(false);
    }
  };

  const filteredTests = testHistory.filter(test => {
    const matchesFilter = filter === 'all' || test.subject?.toLowerCase() === filter.toLowerCase();
    const matchesSearch = test.test_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         test.subject?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getGradeColor = (percentage) => {
    if (percentage >= 90) return 'text-green-600 bg-green-50';
    if (percentage >= 80) return 'text-blue-600 bg-blue-50';
    if (percentage >= 70) return 'text-yellow-600 bg-yellow-50';
    if (percentage >= 60) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const getPerformanceTrend = () => {
    if (!analytics || !analytics.recent_scores || analytics.recent_scores.length < 2) return null;
    
    const recent = analytics.recent_scores;
    const lastScore = recent[recent.length - 1];
    const prevScore = recent[recent.length - 2];
    const trend = lastScore - prevScore;
    
    return {
      value: Math.abs(trend).toFixed(1),
      direction: trend > 0 ? 'up' : trend < 0 ? 'down' : 'stable',
      color: trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600'
    };
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner text="Loading test history..." />
      </div>
    );
  }

  const trend = getPerformanceTrend();

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Test History & Analytics</h1>
        <p className="text-gray-600">Track your progress and analyze your performance over time</p>
      </div>

      {/* Analytics Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <Trophy className="w-8 h-8 text-yellow-500" />
              <span className="text-2xl font-bold text-gray-900">
                {analytics.total_tests || 0}
              </span>
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Total Tests</h3>
            <p className="text-xs text-gray-500">Tests completed</p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <Target className="w-8 h-8 text-blue-500" />
              <span className="text-2xl font-bold text-gray-900">
                {analytics.average_score?.toFixed(1) || '0.0'}%
              </span>
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Average Score</h3>
            <p className="text-xs text-gray-500">Overall performance</p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <Award className="w-8 h-8 text-green-500" />
              <span className="text-2xl font-bold text-gray-900">
                {analytics.best_score?.toFixed(1) || '0.0'}%
              </span>
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Best Score</h3>
            <p className="text-xs text-gray-500">Personal record</p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <TrendingUp className={`w-8 h-8 ${trend ? trend.color : 'text-gray-400'}`} />
              <span className={`text-2xl font-bold ${trend ? trend.color : 'text-gray-900'}`}>
                {trend ? `${trend.direction === 'up' ? '+' : trend.direction === 'down' ? '-' : ''}${trend.value}%` : 'N/A'}
              </span>
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Recent Trend</h3>
            <p className="text-xs text-gray-500">Last vs previous</p>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search tests..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Subjects</option>
              <option value="physics">Physics</option>
              <option value="chemistry">Chemistry</option>
              <option value="biology">Biology</option>
            </select>
          </div>
        </div>
      </div>

      {/* Test History List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Recent Tests</h2>
          <p className="text-gray-600 mt-1">Your test history and detailed results</p>
        </div>

        {filteredTests.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Tests Found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || filter !== 'all' 
                ? 'No tests match your current filters.' 
                : 'You haven\'t taken any tests yet.'}
            </p>
            <Link to="/test-selection" className="btn-primary">
              Take Your First Test
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredTests.map((test, index) => (
              <div key={test.id || index} className="p-6 hover:bg-gray-50 transition-colors duration-200">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {test.test_name || `Test ${index + 1}`}
                      </h3>
                      {test.subject && (
                        <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded-full">
                          {test.subject}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(test.completed_at || test.date)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{formatTime(test.completed_at || test.date)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Target className="w-4 h-4" />
                        <span>{test.total_questions || test.questions_count} questions</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getGradeColor(test.score_percentage).split(' ')[0]}`}>
                        {test.score_percentage?.toFixed(1) || '0.0'}%
                      </div>
                      <div className="text-sm text-gray-600">
                        {test.correct_answers || 0}/{test.total_questions || 0} correct
                      </div>
                    </div>
                    
                    <Link
                      to={`/results/${test.test_id || test.id}`}
                      className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View Details</span>
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Subject-wise Performance Chart Placeholder */}
      {analytics && analytics.subject_performance && (
        <div className="mt-8 bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Subject-wise Performance</h2>
              <p className="text-gray-600 mt-1">Your performance breakdown by subject</p>
            </div>
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-gray-500" />
              <PieChart className="w-5 h-5 text-gray-500" />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(analytics.subject_performance).map(([subject, data]) => (
              <div key={subject} className="p-4 border border-gray-200 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2 capitalize">{subject}</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Average:</span>
                    <span className="font-medium">{data.average?.toFixed(1) || '0.0'}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Best:</span>
                    <span className="font-medium">{data.best?.toFixed(1) || '0.0'}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Tests:</span>
                    <span className="font-medium">{data.count || 0}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(data.average || 0, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TestHistory;
