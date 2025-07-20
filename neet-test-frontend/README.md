# NEET Test Preparation Platform

A comprehensive NEET test preparation platform with AI-powered question generation, real-time timer functionality, and detailed performance analytics.

## 🚀 Features

### Frontend (React + Vite)
- **Modern UI**: Clean, responsive design inspired by professional test platforms
- **Subject Selection**: Physics, Chemistry, Biology with intuitive icons
- **Flexible Testing**: Topic-wise or full subject tests
- **Real-time Timer**: 1 minute per question with auto-submit
- **Live Question Navigation**: Visual progress tracking
- **Detailed Results**: Performance analysis with explanations
- **Toast Notifications**: Real-time feedback for user actions

### Backend (Flask + Azure OpenAI)
- **AI Question Generation**: Real NEET-style questions using Azure OpenAI
- **Timer Management**: Automatic test submission on timeout
- **Performance Analytics**: Detailed scoring and recommendations
- **RESTful API**: Clean API design for frontend integration
- **Database Management**: SQLite for development, easily scalable

## 📋 Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Azure OpenAI API access

## 🛠️ Installation

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd neet-test-backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables are already configured:**
   - Azure OpenAI credentials in `.env` file
   - Ready to use with your API key

4. **Start the backend server:**
   ```bash
   python -m src.main
   ```
   
   Backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd ../neet-test-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   Frontend will run on `http://localhost:3000`

## 🎯 Usage

### Starting a Test

1. **Visit the Application**: Open `http://localhost:3000`
2. **Navigate to Test Selection**: Click "Take Test" or "Start Practice Test"
3. **Configure Your Test**:
   - Select subject (Physics, Chemistry, Biology)
   - Choose test type (Topic-wise or Full Subject)
   - Select specific topic (if topic-wise)
   - Set number of questions (5-30)
4. **Start Test**: Review configuration and click "Start Test"

### Taking the Test

- **Timer**: Displays remaining time with visual warnings
- **Navigation**: Use Previous/Next buttons or click question numbers
- **Progress Tracking**: Visual indicators show answered/unanswered questions
- **Auto-submit**: Test automatically submits when timer expires
- **Manual Submit**: Click "Submit Test" to finish early

### Viewing Results

- **Overall Score**: Percentage score with grade (Excellent/Good/Average/Below Average/Poor)
- **Detailed Breakdown**: Correct/incorrect answers with time taken
- **Performance Analysis**: Personalized recommendations
- **Solution Review**: Question-by-question explanations
- **Retake Options**: Easy access to take another test

## 🏗️ Architecture

### Frontend Structure
```
src/
├── components/          # Reusable UI components
│   ├── Navbar.jsx      # Navigation bar
│   ├── Timer.jsx       # Test timer component
│   └── LoadingSpinner.jsx
├── pages/              # Main application pages
│   ├── Home.jsx        # Landing page
│   ├── TestSelection.jsx # Test configuration
│   ├── TestInterface.jsx # Test taking interface
│   └── TestResults.jsx  # Results display
├── context/            # State management
│   └── TestContext.jsx # Global test state
├── services/           # API communication
│   └── api.js          # API service layer
└── styles/             # Styling
    └── index.css       # Global styles with Tailwind
```

### Backend Structure
```
src/
├── api/routes/         # API endpoints
├── models/             # Database models
├── services/           # Business logic
│   ├── azure_openai_service.py # AI integration
│   ├── question_service.py     # Question management
│   └── test_service.py         # Test management
├── database/           # Database configuration
└── config/             # Application settings
```

## 🎨 Design Features

### Visual Design
- **Color-coded Subjects**: Physics (Blue), Chemistry (Green), Biology (Purple)
- **Intuitive Icons**: Subject-specific icons for easy recognition
- **Progress Indicators**: Visual feedback for test progress
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Professional Styling**: Clean, modern interface

### User Experience
- **One-click Start**: Minimal steps to begin testing
- **Real-time Feedback**: Immediate response to user actions
- **Smart Navigation**: Keyboard shortcuts and quick access
- **Error Handling**: Graceful error messages and recovery
- **Loading States**: Clear feedback during API calls

## 🔧 API Endpoints

### Test Management
- `POST /api/v1/tests/start` - Start a new test
- `POST /api/v1/tests/{id}/submit` - Submit test answers
- `GET /api/v1/tests/{id}/status` - Check test status
- `GET /api/v1/tests/{id}/results` - Get test results

### Content Management
- `GET /api/v1/subjects` - Get all subjects
- `GET /api/v1/subjects/{id}/topics` - Get topics for subject
- `POST /api/v1/questions/generate` - Generate questions

## 🧪 Testing

### Backend Testing
```bash
cd neet-test-backend
python test_integration.py
```

### Frontend Testing
- Manual testing through the UI
- API integration testing via browser developer tools

## 🚀 Production Deployment

### Backend Deployment
- Configure production database (PostgreSQL recommended)
- Set up environment variables for production
- Use WSGI server (Gunicorn) for production
- Set up reverse proxy (Nginx)

### Frontend Deployment
```bash
npm run build
```
- Deploy build files to static hosting (Netlify, Vercel, or CDN)
- Configure API base URL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
- Check the console logs for detailed error messages
- Ensure both backend and frontend servers are running
- Verify Azure OpenAI credentials are configured correctly

## 🎓 NEET Preparation Tips

- **Regular Practice**: Use the platform daily for consistent improvement
- **Topic Focus**: Identify weak areas and practice topic-wise tests
- **Time Management**: Practice with the timer to improve speed
- **Review Explanations**: Study the detailed explanations for wrong answers
- **Track Progress**: Monitor your performance trends over time
