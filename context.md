# Pilolo Tours - Project Context

## Project Overview

Pilolo Tours is a Django web application for a bicycle tour company based in Ghana. The application allows users to browse available tours, view tour details, and make bookings for specific tour schedules.

## Project Structure

### Core Components

1. **Django Project**: `core`
   - Main Django project settings and configuration
   - Uses SQLite database

2. **Main Application**: `pilolo`
   - Contains models, views, forms, and templates for the tour booking system

### Technology Stack

- **Backend**: Django 5.2.4
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Interactive UI**: HTMX for dynamic content loading
- **Database**: SQLite
- **CSS Processing**: Tailwind CSS (using input.css to output.css)

### Key Files and Directories

#### Project Configuration
- `core/settings.py`: Django project settings
- `core/urls.py`: Main URL routing
- `package.json`: NPM configuration for Tailwind CSS

#### Application Code
- `pilolo/models.py`: Data models
- `pilolo/views.py`: View functions
- `pilolo/urls.py`: Application URL routing
- `pilolo/forms.py`: Form definitions
- `pilolo/admin.py`: Admin interface configuration

#### Templates
- `templates/base.html`: Base template with common layout
- `pilolo/templates/pilolo/home.html`: Homepage template
- `pilolo/templates/pilolo/tour_details.html`: Tour details page
- `pilolo/templates/pilolo/my_bookings.html`: User bookings page
- `pilolo/templates/pilolo/partials/booking_form.html`: Booking form partial (loaded via HTMX)

#### Static Files
- `static/css/input.css`: Tailwind CSS source
- `static/css/output.css`: Compiled CSS
- `static/videos/`: Video assets for the site

## Data Models

### CustomUser
- Extended user model with email as the username field
- Fields: email, first_name, last_name, phone_number, etc.

### Tour
- Represents a bicycle tour offering
- Fields: name, description, duration, price, max_participants, highlights, what_included, what_to_bring, meeting_point, image

### TourSchedule
- Represents available times for a tour
- Fields: tour (FK), day (choices: Saturday/Sunday), start_time, end_time

### Booking
- Represents a user booking for a specific tour schedule
- Fields: user (FK), schedule (FK), participants, booking_date, tour_date, status, phone, special_requirements

## Key Features

1. **Tour Browsing**: Users can view all available tours on the homepage
2. **Tour Details**: Detailed information about each tour with schedules
3. **Booking System**: Modal-based booking form using HTMX for dynamic loading
4. **User Bookings**: Users can view their booking history and status
5. **Admin Interface**: Custom admin views for managing tours, schedules, and bookings

## UI/UX Design

- **Color Scheme**: Uses Ghana flag colors (red, gold, green)
- **Custom CSS Classes**: 
  - `btn-primary`: Green button style
  - `btn-secondary`: Gold button style
  - `form-input`: Styled form inputs
- **Responsive Design**: Mobile-friendly layout using Tailwind CSS
- **Dynamic Content**: HTMX for loading booking forms without full page reloads

## Authentication

- Custom user model with email-based authentication
- Login required for booking management
- Admin interface for staff users

## Future Enhancements

- Payment integration
- Email notifications for bookings
- More tour schedule options
- User reviews and ratings
- Image gallery for tours

## Change Log

### Initial Setup - Current State
- Basic project structure and models implemented
- Tour browsing and booking functionality working
- User authentication system in place
- Admin interface configured

---

*This document will be updated with all future changes to the project.*