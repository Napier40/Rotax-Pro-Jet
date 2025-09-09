"""
Rotax Pro Jet - Main Application File
A Flask web application for calculating optimal carburetor jetting for Rotax kart engines.
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///rotax_pro_jet.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Context processor to make datetime available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Constants for calculations
GAS_CONSTANT_DRY_AIR = 287.05  # J/(kg*K)
STANDARD_CONDITIONS = {
    'temperature': 25,  # Celsius
    'pressure': 990,    # hPa
    'humidity': 0,      # Percentage
    'air_density': 1.157  # kg/m³
}

# Engine specifications
ENGINE_SPECS = {
    'Senior MAX EVO': {
        'default_jet': 130,
        'jet_range': {'min': 124, 'max': 136},
        'needle_options': ['K27', 'K98'],
        'default_needle': 'K98',
        'default_needle_position': 2,
        'volumetric_efficiency': 0.91
    },
    'Junior MAX EVO': {
        'default_jet': 130,
        'jet_range': {'min': 124, 'max': 136},
        'needle_options': ['K27', 'K98'],
        'default_needle': 'K98',
        'default_needle_position': 2,
        'volumetric_efficiency': 0.87
    },
    'Mini MAX': {
        'default_jet': 130,
        'jet_range': {'min': 124, 'max': 136},
        'needle_options': ['K27', 'K98'],
        'default_needle': 'K98',
        'default_needle_position': 2,
        'volumetric_efficiency': 0.58
    }
}

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subscription_plan = db.Column(db.String(20), default='free')
    subscription_end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settings = db.relationship('Setting', backref='user', lazy=True)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    temperature = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    engine_type = db.Column(db.String(50), nullable=False)
    reference_jet = db.Column(db.Integer)
    main_jet = db.Column(db.Integer)
    needle_position = db.Column(db.Integer)
    float_height = db.Column(db.Float)
    needle_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility functions for calculations
def calculate_air_density(temperature, pressure, humidity):
    """
    Calculate air density based on temperature, pressure, and humidity
    
    Args:
        temperature (float): Temperature in Celsius
        pressure (float): Atmospheric pressure in hPa
        humidity (float): Relative humidity as a percentage (0-100)
        
    Returns:
        float: Air density in kg/m³
    """
    # Convert temperature to Kelvin
    temp_kelvin = temperature + 273.15
    
    # Convert pressure from hPa to Pascals
    pressure_pascals = pressure * 100
    
    # Calculate saturation vapor pressure
    e = 6.1078
    a = 7.5
    b = 237.3
    saturated_vapor_pressure = e * pow(10, (a * temperature) / (b + temperature))
    
    # Calculate actual vapor pressure
    vapor_pressure = (humidity / 100) * saturated_vapor_pressure * 100  # Convert to Pascals
    
    # Calculate air density
    density = (pressure_pascals / (GAS_CONSTANT_DRY_AIR * temp_kelvin)) * (1 - 0.378 * (vapor_pressure / pressure_pascals))
    
    return density

def calculate_jet_size(reference_jet, reference_air_density, current_air_density):
    """
    Calculate the recommended jet size based on air density
    
    Args:
        reference_jet (int): The jet size known to work at reference conditions
        reference_air_density (float): The air density at reference conditions
        current_air_density (float): The current air density
        
    Returns:
        int: The recommended jet size
    """
    # Using the formula from the Bowmain document: j₂ = j₁ × (ρ₂/ρ₁)^(1/4)
    jet_size = reference_jet * pow(current_air_density / reference_air_density, 0.25)
    
    # Round to the nearest available jet size (typically in increments of 2)
    return round(jet_size / 2) * 2

def calculate_needle_position(reference_position, reference_air_density, current_air_density):
    """
    Calculate the recommended needle position based on air density
    
    Args:
        reference_position (int): The needle position known to work at reference conditions
        reference_air_density (float): The air density at reference conditions
        current_air_density (float): The current air density
        
    Returns:
        int: The recommended needle position (1-5)
    """
    density_ratio = current_air_density / reference_air_density
    
    # If density is higher (colder, higher pressure), we need a richer mixture (lower position)
    # If density is lower (warmer, lower pressure), we need a leaner mixture (higher position)
    if density_ratio > 1.08:
        return max(1, reference_position - 1)
    elif density_ratio < 0.92:
        return min(5, reference_position + 1)
    
    return reference_position

def calculate_float_height(reference_height, reference_air_density, current_air_density):
    """
    Calculate the recommended float height based on air density
    
    Args:
        reference_height (float): The float height known to work at reference conditions
        reference_air_density (float): The air density at reference conditions
        current_air_density (float): The current air density
        
    Returns:
        float: The recommended float height in mm
    """
    density_ratio = current_air_density / reference_air_density
    
    # Adjust float height based on density ratio
    height_adjustment = (1 - density_ratio) * 2
    
    return round((reference_height + height_adjustment) * 10) / 10

def calculate_jetting(params):
    """
    Calculate jetting recommendations based on environmental parameters
    
    Args:
        params (dict): Environmental and engine parameters
        
    Returns:
        dict: Jetting recommendations
    """
    temperature = params.get('temperature')
    pressure = params.get('pressure')
    humidity = params.get('humidity')
    altitude = params.get('altitude')
    engine_type = params.get('engine_type')
    reference_jet = params.get('reference_jet')
    reference_conditions = params.get('reference_conditions')
    
    # Get engine specifications
    engine_spec = ENGINE_SPECS.get(engine_type, ENGINE_SPECS['Senior MAX EVO'])
    
    # Calculate current air density
    current_air_density = calculate_air_density(temperature, pressure, humidity)
    
    # Use provided reference conditions or standard conditions
    ref_conditions = reference_conditions or STANDARD_CONDITIONS
    ref_air_density = reference_conditions and calculate_air_density(
        ref_conditions.get('temperature'),
        ref_conditions.get('pressure'),
        ref_conditions.get('humidity')
    ) or STANDARD_CONDITIONS['air_density']
    
    # Use provided reference jet or default from engine spec
    ref_jet = reference_jet or engine_spec['default_jet']
    
    # Calculate recommended jet size
    recommended_jet = calculate_jet_size(ref_jet, ref_air_density, current_air_density)
    
    # Calculate recommended needle position
    recommended_needle_position = calculate_needle_position(
        engine_spec['default_needle_position'],
        ref_air_density,
        current_air_density
    )
    
    # Calculate recommended float height (assuming 15mm as reference)
    recommended_float_height = calculate_float_height(15, ref_air_density, current_air_density)
    
    # Determine if conditions are near dew point
    is_near_dew_point = humidity > 90 and temperature < 10
    
    # Prepare the response
    result = {
        'input': {
            'temperature': temperature,
            'pressure': pressure,
            'humidity': humidity,
            'altitude': altitude,
            'engine_type': engine_type
        },
        'calculations': {
            'current_air_density': current_air_density,
            'reference_air_density': ref_air_density,
            'density_ratio': current_air_density / ref_air_density
        },
        'recommendations': {
            'main_jet': recommended_jet,
            'needle_position': recommended_needle_position,
            'float_height': recommended_float_height,
            'needle_type': engine_spec['default_needle']
        },
        'warnings': []
    }
    
    # Add warnings if necessary
    if is_near_dew_point:
        result['warnings'].append({
            'type': 'dew_point',
            'message': 'Temperature is close to dew point. Risk of water condensation in fuel system.'
        })
    
    if recommended_jet < engine_spec['jet_range']['min'] or recommended_jet > engine_spec['jet_range']['max']:
        result['warnings'].append({
            'type': 'jet_range',
            'message': f"Recommended jet size ({recommended_jet}) is outside the typical range for this engine."
        })
    
    return result

# Weather API functions
def get_weather_data(latitude, longitude):
    """
    Get weather data for a location
    
    Args:
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        
    Returns:
        dict: Weather data including temperature, pressure, humidity
    """
    # In a production app, we would use a real weather API
    # For now, we'll return mock weather data
    return {
        'temperature': 22.5,  # Celsius
        'pressure': 1013.2,   # hPa
        'humidity': 65,       # Percentage
        'location': {
            'name': 'Sample Location',
            'country': 'Sample Country'
        },
        'timestamp': datetime.utcnow().isoformat()
    }

def get_elevation_data(latitude, longitude):
    """
    Get elevation data for a location
    
    Args:
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        
    Returns:
        dict: Elevation data
    """
    # In a production app, we would use a real elevation API
    # For now, we'll return mock elevation data
    return {
        'elevation': 325,  # meters above sea level
        'resolution': 10,  # meters
        'source': 'Mock Elevation API'
    }

def search_locations(query):
    """
    Search for locations by name
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of matching locations
    """
    # In a production app, we would use a real geocoding API
    # For now, we'll return mock location data
    return [
        {
            'name': 'Sample Track 1',
            'country': 'Sample Country',
            'latitude': 40.7128,
            'longitude': -74.0060
        },
        {
            'name': 'Sample Track 2',
            'country': 'Sample Country',
            'latitude': 34.0522,
            'longitude': -118.2437
        }
    ]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculator')
def calculator():
    engine_types = list(ENGINE_SPECS.keys())
    return render_template('calculator.html', engine_types=engine_types)

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    data = request.json
    result = calculate_jetting(data)
    return jsonify(result)

@app.route('/api/weather/current')
def api_weather_current():
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    weather_data = get_weather_data(latitude, longitude)
    return jsonify(weather_data)

@app.route('/api/weather/elevation')
def api_weather_elevation():
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    elevation_data = get_elevation_data(latitude, longitude)
    return jsonify(elevation_data)

@app.route('/api/weather/search')
def api_weather_search():
    query = request.args.get('query')
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    locations = search_locations(query)
    return jsonify(locations)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not name or not email or not password or not confirm_password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='sha256')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Validate inputs
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('login.html')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
        
        # Log in user
        login_user(user, remember=remember)
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/settings')
@login_required
def settings():
    user_settings = Setting.query.filter_by(user_id=current_user.id).all()
    return render_template('settings.html', settings=user_settings)

@app.route('/api/settings/save', methods=['POST'])
@login_required
def api_settings_save():
    data = request.json
    
    # Create new setting
    new_setting = Setting(
        user_id=current_user.id,
        name=data.get('name'),
        notes=data.get('notes'),
        temperature=data.get('settings', {}).get('temperature'),
        pressure=data.get('settings', {}).get('pressure'),
        humidity=data.get('settings', {}).get('humidity'),
        altitude=data.get('settings', {}).get('altitude'),
        engine_type=data.get('settings', {}).get('engine_type'),
        reference_jet=data.get('settings', {}).get('reference_jet'),
        main_jet=data.get('results', {}).get('main_jet'),
        needle_position=data.get('results', {}).get('needle_position'),
        float_height=data.get('results', {}).get('float_height'),
        needle_type=data.get('results', {}).get('needle_type')
    )
    
    db.session.add(new_setting)
    db.session.commit()
    
    return jsonify({'message': 'Setting saved successfully', 'id': new_setting.id})

@app.route('/api/settings/<int:setting_id>/delete', methods=['DELETE'])
@login_required
def api_settings_delete(setting_id):
    setting = Setting.query.filter_by(id=setting_id, user_id=current_user.id).first()
    
    if not setting:
        return jsonify({'error': 'Setting not found'}), 404
    
    db.session.delete(setting)
    db.session.commit()
    
    return jsonify({'message': 'Setting deleted successfully'})

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5002)