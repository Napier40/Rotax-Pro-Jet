# Rotax Pro Jet

A Flask web application for calculating optimal carburetor jetting for Rotax kart engines based on environmental conditions.

## Overview

Rotax Pro Jet is a comprehensive tool designed for kart racers to optimize their carburetor jetting based on temperature, humidity, and altitude. The application uses mathematical models derived from the Bowmain Consulting document on Rotax Carburetor Jetting to provide accurate recommendations for main jet size, needle position, and float height.

## Features

- **Real-time Weather Data**: Automatically fetch current weather conditions for your location
- **Manual Input Option**: Enter environmental parameters manually when automatic data is unavailable
- **Multiple Engine Support**: Calculations for Senior MAX EVO, Junior MAX EVO, and Mini MAX engines
- **Custom Reference Conditions**: Set your own baseline conditions for jetting calculations
- **Save & Compare Settings**: Store your jetting configurations and track performance
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **User Accounts**: Save your settings and access them from anywhere

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python, Flask
- **Database**: SQLAlchemy with SQLite (configurable for other databases)
- **APIs**: Weather API, Elevation API
- **Payment Processing**: Stripe

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Napier40/Rotax-Pro-Jet.git
   cd Rotax-Pro-Jet
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///rotax_pro_jet.db
   WEATHER_API_KEY=your_weather_api_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

7. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
Rotax-Pro-Jet/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this file)
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
├── static/                # Static files
│   ├── css/               # CSS files
│   ├── js/                # JavaScript files
│   └── images/            # Image files
└── templates/             # Jinja2 templates
    ├── base.html          # Base template
    ├── index.html         # Home page
    ├── calculator.html    # Calculator page
    └── ...                # Other templates
```

## Mathematical Model

The jetting calculations are based on the formula derived from the Bowmain Consulting document:

```
j₂ = j₁ × (ρ₂/ρ₁)^(1/4)
```

Where:
- j₂ is the new jet size
- j₁ is the reference jet size
- ρ₂ is the current air density
- ρ₁ is the reference air density

Air density is calculated using:

```
ρ = (P / (Rd × T)) × (1 - 0.378 × (Pw/P))
```

Where:
- ρ = air density (kg/m³)
- P = atmospheric pressure (Pascals)
- Pw = water vapor pressure (Pascals)
- Rd = gas constant for dry air (287.05 J/(kg*K))
- T = temperature (Kelvin)

## API Endpoints

### Authentication
- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Log in a user

### Jetting
- `POST /api/calculate`: Calculate jetting based on environmental parameters
- `POST /api/settings/save`: Save a jetting configuration
- `GET /api/settings/<user_id>`: Get saved jetting configurations for a user
- `DELETE /api/settings/<setting_id>`: Delete a saved jetting configuration

### Weather
- `GET /api/weather/current`: Get current weather data by coordinates
- `GET /api/weather/elevation`: Get elevation data by coordinates
- `GET /api/weather/search`: Search for locations by name

### Payment
- `GET /api/payment/plans`: Get subscription plans
- `POST /api/payment/create-checkout-session`: Create a checkout session for subscription
- `POST /api/payment/webhook`: Handle webhook from payment provider

## Subscription Plans

- **Basic Plan** ($4.99/month):
  - Basic jetting calculations
  - Manual weather input
  - Limited history (5 saves)

- **Pro Plan** ($9.99/month):
  - Advanced jetting calculations
  - Automatic weather data
  - Unlimited history
  - Track-specific recommendations
  - Email support

- **Team Plan** ($24.99/month):
  - All Pro features
  - Up to 5 team members
  - Team data sharing
  - Priority support
  - Custom engine profiles

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Bowmain Consulting for their research on Rotax Carburetor Jetting
- Rotax for their kart racing engines
- The karting community for their feedback and support