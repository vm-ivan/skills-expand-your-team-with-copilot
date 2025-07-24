# Mergington High School Activities

A comprehensive web application for managing extracurricular activities at Mergington High School. The system provides a modern, responsive interface for students to discover and learn about activities, while enabling teachers to manage student registrations.

## Features

### For Students
- **Browse Activities**: View all available extracurricular activities with detailed information
- **Advanced Filtering**: Filter activities by category (Sports, Arts, Academic, Technology, Community), day of the week, and time of day
- **Search Functionality**: Search activities by name or description
- **Activity Details**: View schedules, descriptions, participant counts, and availability
- **Real-time Updates**: See current enrollment numbers and available spots

### For Teachers
- **Secure Authentication**: Teacher login system for administrative access
- **Student Registration**: Register students for activities via email
- **Participant Management**: View and manage current participants for each activity

### Activity Categories
- **Sports**: Soccer Team, Basketball Team, Morning Fitness
- **Arts**: Art Club, Drama Club
- **Academic**: Chess Club, Math Club, Debate Team, Science Olympiad
- **Technology**: Programming Class, Weekend Robotics Workshop
- **Community**: Various community service activities

## Technology Stack

- **Frontend**: Modern vanilla JavaScript with responsive CSS design
- **Backend**: FastAPI (Python) REST API
- **Database**: MongoDB with in-memory fallback for development
- **Authentication**: Secure password hashing with Argon2
- **Deployment**: Uvicorn ASGI server

## API Endpoints

- `GET /activities` - Retrieve all activities with optional filtering
- `POST /activities/{activity_name}/signup` - Register a student for an activity
- `POST /auth/login` - Teacher authentication
- `GET /activities/days` - Get available activity days

## Development Guide

For detailed setup and development instructions, please refer to our [Development Guide](../docs/how-to-develop.md).
