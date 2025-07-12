# Voice Interview Bot

## Overview

This is a Flask-based web application that provides an AI-powered voice interview system for job candidates to practice their interview skills. The application supports multiple job roles including Software Engineer, Data Scientist, Product Manager, Marketing Manager, and Sales Representative. It features speech recognition and text-to-speech capabilities to simulate a real interview experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap for UI components
- **Structure**: Single-page application with dynamic content switching
- **Styling**: Bootstrap dark theme with custom CSS enhancements
- **Speech Integration**: Web Speech API for both recognition and synthesis

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: Simple MVC structure with templates
- **Session Management**: In-memory storage using Python dictionaries
- **API Design**: RESTful endpoints for interview management

### Data Storage
- **Primary Storage**: In-memory Python dictionaries
- **Session Data**: Temporary storage during user sessions
- **Persistence**: No permanent data storage (stateless between server restarts)

## Key Components

### 1. Interview Management System
- **Purpose**: Manages interview sessions and question flow
- **Implementation**: Python class-based structure with session tracking
- **Features**: Role-based question sets, progress tracking, scoring system

### 2. Speech Recognition Module
- **Technology**: Web Speech API (webkitSpeechRecognition)
- **Functionality**: Real-time voice-to-text conversion
- **Browser Support**: Chrome and Edge primary targets

### 3. Text-to-Speech System
- **Technology**: Web Speech Synthesis API
- **Purpose**: Reads questions aloud to simulate interviewer voice
- **Integration**: Seamless with interview flow

### 4. Question Bank
- **Structure**: Role-specific question sets stored as Python dictionaries
- **Roles Supported**: 5 different job categories with tailored questions
- **Extensibility**: Easy to add new roles and questions

### 5. Feedback System
- **Placeholder**: Basic structure for AI feedback integration
- **Future Enhancement**: Ready for LLM integration for answer evaluation

## Data Flow

1. **Session Initialization**: User selects role → Server creates session with unique ID
2. **Question Delivery**: Server provides next question → Frontend displays and optionally speaks
3. **Answer Capture**: Speech recognition converts voice to text → User can edit before submission
4. **Answer Processing**: Text sent to server → Stored with session data
5. **Progress Management**: Server tracks completion → Updates progress indicators
6. **Interview Completion**: Final question answered → Summary generation and display

## External Dependencies

### Frontend Dependencies
- **Bootstrap**: UI framework and styling (CDN)
- **Font Awesome**: Icon library (CDN)
- **Web Speech API**: Browser-native speech capabilities

### Backend Dependencies
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing support

### Browser Requirements
- **Speech Recognition**: Chrome/Edge for optimal experience
- **Modern JavaScript**: ES6+ features required

## Deployment Strategy

### Development Environment
- **Server**: Flask development server
- **Configuration**: Debug mode enabled
- **Host**: All interfaces (0.0.0.0)
- **Port**: 5000

### Production Considerations
- **Session Storage**: Currently in-memory (suitable for single-server deployment)
- **Scaling**: Would require external session storage (Redis/Database) for multi-server
- **Security**: Session secret key configured via environment variable

### Environment Configuration
- **SESSION_SECRET**: Configurable via environment variable
- **Debug Mode**: Enabled for development
- **CORS**: Enabled for cross-origin requests

## Technical Decisions

### Why Flask?
- **Simplicity**: Lightweight framework suitable for focused application
- **Flexibility**: Easy to extend with additional features
- **Python Ecosystem**: Good foundation for future AI/ML integration

### Why In-Memory Storage?
- **Simplicity**: No database setup required
- **Performance**: Fast access for temporary session data
- **Prototype-Friendly**: Easy to develop and test

### Why Web Speech API?
- **Browser Native**: No additional dependencies or API keys required
- **Real-time**: Immediate speech processing
- **Cost-Effective**: No external speech service costs

### Architecture Trade-offs
- **Pros**: Simple setup, fast development, no external dependencies
- **Cons**: Not suitable for production scale, sessions lost on server restart
- **Future Path**: Easy to migrate to database storage and external AI services