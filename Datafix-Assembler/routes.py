import os
import logging
from datetime import datetime
import pytz
from flask import render_template, request, jsonify, send_file
from app import app, db, Feedback, UsageLog

from sql_processor import process_pkg_file

def log_user_activity(created_by, case_id):
    """Log user activity to Database and User_Logs.txt"""
    # Database Log
    try:
        new_log = UsageLog(created_by=created_by, case_id=case_id)
        db.session.add(new_log)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to save usage log to database: {str(e)}")

    # File Log fallback
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
    log_entry = f"Created by: {created_by} | Case#: {case_id} | Timestamp: {timestamp}\n"
    try:
        with open('User_Logs.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logging.error(f"Failed to write to User_Logs.txt: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename or not file.filename.endswith('.pkg'):
        return jsonify({'error': 'Only .pkg files are accepted'}), 400
    
    try:
        content = file.read().decode('utf-8', errors='replace')
        result = process_pkg_file(content)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # Log user activity
        if result.get('created_by') and result.get('case_id'):
            log_user_activity(result['created_by'], result['case_id'])
        else:
            logging.warning(f"Metadata missing for logging: created_by={result.get('created_by')}, case_id={result.get('case_id')}")
        
        return jsonify({
            'success': True,
            'filename': result['filename'],
            'content': result['content'],
            'case_id': result['case_id']
        })
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

from app import app, db, Feedback

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    feedback_text = data.get('feedback', '').strip()
    case_number = data.get('case_id', '').strip() # Assuming case_id might be sent
    
    if not feedback_text:
        return jsonify({'error': 'Feedback cannot be empty'}), 400
    
    # Save to Database
    try:
        new_feedback = Feedback(case_number=case_number, feedback_text=feedback_text)
        db.session.add(new_feedback)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to save feedback to database: {str(e)}")
    
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')
    
    email_sent = False
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = os.environ.get('SMTP_PORT')
        smtp_user = os.environ.get('SMTP_USER')
        smtp_pass = os.environ.get('SMTP_PASS')
        
        if smtp_server and smtp_port and smtp_user and smtp_pass:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = 'girirajpariks@gmail.com'
            msg['Subject'] = f'yDatafix Feedback - {timestamp}'
            msg.attach(MIMEText(feedback_text, 'plain'))
            
            with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            email_sent = True
    except Exception as e:
        logging.warning(f"Email sending failed: {str(e)}")
    
    return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
