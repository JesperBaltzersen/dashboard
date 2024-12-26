from flask import Flask
from dash import Dash
from flask import render_template

def setup_flask_routes(server):
    @server.route('/')
    def home():
        return render_template('index.html')
    
    @server.route('/about')
    def about():
        return render_template('about.html')

    @server.route('/contact')
    def contact():
        return render_template('contact.html')
    
    @server.route('/dashboard/')
    def dashboard():
        return render_template('dashboard.html')