from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuration for uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# This dictionary simulates a database for simplicity
food_events = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', food_events=food_events)

@app.route('/organizer', methods=['GET', 'POST'])
def organizer():
    if request.method == 'POST':
        event_name = request.form['event_name']
        description = request.form['description']
        location = request.form['location']  # Capture the location input
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(save_path)
            image_url = url_for('static', filename=os.path.join('uploads', filename))
        else:
            image_url = None
        food_events[event_name] = {
            'description': description,
            'queue': [],
            'image_url': image_url,
            'location': location  # Save location
        }
        return redirect(url_for('index'))
    return render_template('organizer.html')


@app.route('/student/<event_name>', methods=['GET', 'POST'])
def student(event_name):
    student_name = ""  # Initialize to an empty string
    message = ""  # Initialize message to ensure it always has a value
    event_details = food_events.get(event_name, {})  # Get event details, or an empty dict if not found

    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        if student_name:
            if student_name not in event_details.get('queue', []):
                event_details['queue'].append(student_name)
                message = "You've been added to the queue."
            else:
                message = "You are already in the queue."
        else:
            message = "Please enter a valid name."

    # Always calculate the total number of people in the queue
    total_in_queue = len(event_details.get('queue', []))

    # Check if the student's name is in the queue for specific calculations
    if student_name in event_details.get('queue', []):
        queue_position = event_details['queue'].index(student_name) + 1
        total_ahead_in_queue = queue_position - 1
    else:
        queue_position = None
        total_ahead_in_queue = total_in_queue  # Before joining, all are ahead

    image_url = event_details.get('image_url', '')
    location = event_details.get('location', '')  # Location for map link

    return render_template('student.html', event_name=event_name, queue_position=queue_position,
                           total_in_queue=total_in_queue, total_ahead_in_queue=total_ahead_in_queue,
                           message=message, image_url=image_url, location=location)




if __name__ == '__main__':
    app.run(debug=True)
