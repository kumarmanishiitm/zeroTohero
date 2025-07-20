import React from 'react';
import { Link } from 'react-router-dom';
import { 
  BookOpen, 
  Clock, 
  Target, 
  TrendingUp, 
  Users, 
  Award,
  ChevronRight,
  Zap
} from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <BookOpen className="w-8 h-8 text-primary-600" />,
      title: "Comprehensive Subjects",
      description: "Physics, Chemistry, and Biology - all NEET subjects covered with detailed explanations"
    },
    {
      icon: <Target className="w-8 h-8 text-success-600" />,
      title: "Topic-wise Practice",
      description: "Focus on specific topics to strengthen your weak areas and master each concept"
    },
    {
      icon: <Clock className="w-8 h-8 text-warning-600" />,
      title: "Timed Tests",
      description: "Real exam experience with 1 minute per question timer to improve speed and accuracy"
    },
    {
      icon: <TrendingUp className="w-8 h-8 text-purple-600" />,
      title: "Detailed Analysis",
      description: "Get comprehensive performance analysis with explanations for every question"
    }
  ];

  const stats = [
    { label: "Practice Questions", value: "10,000+", icon: <BookOpen className="w-6 h-6" /> },
    { label: "Topics Covered", value: "150+", icon: <Target className="w-6 h-6" /> },
    { label: "Success Rate", value: "95%", icon: <Award className="w-6 h-6" /> },
    { label: "Students Helped", value: "5,000+", icon: <Users className="w-6 h-6" /> }
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 text-balance">
            Master NEET with
            <span className="text-primary-600"> AI-Powered </span>
            Practice Tests
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto text-balance">
            Prepare for NEET with our comprehensive test platform featuring real-time AI question generation, 
            detailed explanations, and performance analytics
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link 
            to="/test-selection" 
            className="btn-primary flex items-center space-x-2 text-lg px-8 py-4"
          >
            <Zap className="w-5 h-5" />
            <span>Start Practice Test</span>
            <ChevronRight className="w-5 h-5" />
          </Link>
          
          <div className="flex items-center space-x-2 text-gray-600">
            <Clock className="w-5 h-5" />
            <span>No registration required</span>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="card text-center space-y-3">
            <div className="flex justify-center text-primary-600">
              {stat.icon}
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </div>
          </div>
        ))}
      </section>

      {/* Features Section */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold text-gray-900">
            Why Choose Our Platform?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Built specifically for NEET aspirants with features that mirror the real exam experience
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card space-y-4 hover:shadow-md transition-shadow duration-300">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  {feature.icon}
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-semibold text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-8 md:p-12 text-center text-white">
        <div className="space-y-6">
          <h2 className="text-3xl font-bold">
            Ready to Start Your NEET Preparation?
          </h2>
          <p className="text-primary-100 text-lg max-w-2xl mx-auto">
            Join thousands of students who are already practicing with our AI-powered question bank. 
            Start your journey towards NEET success today!
          </p>
          <Link 
            to="/test-selection"
            className="inline-flex items-center space-x-2 bg-white text-primary-700 font-semibold px-8 py-4 rounded-lg hover:bg-gray-50 transition-colors duration-200"
          >
            <span>Begin Practice Now</span>
            <ChevronRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
