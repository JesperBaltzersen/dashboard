from flask import Flask
from dash import Dash, dash_table
from flask import render_template
from flask import request, flash
import pandas as pd
import os
from werkzeug.utils import secure_filename

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
    


    # Configure upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'csv'}

    # Initialize Flask
    server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    server.secret_key = 'your-secret-key-here'  # Required for flashing messages

    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Global variable to store the DataFrame
    current_df = None

    @server.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        print(f"Upload route hit with method: {request.method}")  # Debug print
        if request.method == 'POST':
            print("POST request received")  # Debug print
            if 'file' not in request.files:
                print("No file in request")  # Debug print
                flash('No file selected')
                return render_template('upload.html')
            
            file = request.files['file']
            
            # If user doesn't select file
            if file.filename == '':
                flash('No file selected')
                return render_template('upload.html')
            
            if file and allowed_file(file.filename):
                try:
                    # Read CSV directly from the uploaded file
                    global current_df
                    current_df = pd.read_csv(file)
                    
                    #Save file (optional)
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(server.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    preview_data = current_df.head()
                    
                    # Create a styled HTML table using pandas
                    table_html = preview_data.to_html(
                        classes='table table-striped table-bordered',
                        index=False,
                        escape=False,
                        float_format=lambda x: '%.2f' % x if isinstance(x, float) else x
                    )

                    flash('File successfully uploaded and processed')
                    return render_template('upload.html', 
                                    table_html=table_html,
                                    row_count=len(current_df))
                except Exception as e:
                    flash(f'Error processing file: {str(e)}')
                    return render_template('upload.html')
            else:
                flash('Allowed file type is CSV')
                return render_template('upload.html')
        
        return render_template('upload.html')