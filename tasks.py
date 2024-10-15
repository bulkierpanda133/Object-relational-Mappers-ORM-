from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define Member model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer)

# Define WorkoutSession model
class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer)  # duration in minutes
    member = db.relationship('Member', backref=db.backref('sessions', lazy=True))

# Create Member CRUD routes
# Create a new member
@app.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()
    new_member = Member(name=data['name'], email=data['email'], age=data.get('age', None))
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member created successfully'}), 201

# Get all members
@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': m.id, 'name': m.name, 'email': m.email, 'age': m.age} for m in members])

# Get a specific member
@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get_or_404(id)
    return jsonify({'id': member.id, 'name': member.name, 'email': member.email, 'age': member.age})

# Update a member
@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    data = request.get_json()
    member.name = data.get('name', member.name)
    member.email = data.get('email', member.email)
    member.age = data.get('age', member.age)
    db.session.commit()
    return jsonify({'message': 'Member updated successfully'})

# Delete a member
@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'})

# Create WorkoutSession routes
# Schedule a workout session
@app.route('/workouts', methods=['POST'])
def schedule_workout():
    data = request.get_json()
    new_session = WorkoutSession(
        member_id=data['member_id'],
        workout_type=data['workout_type'],
        date=data['date'],
        duration=data['duration']
    )
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully'}), 201

# View all workout sessions
@app.route('/workouts', methods=['GET'])
def get_workouts():
    sessions = WorkoutSession.query.all()
    return jsonify([{
        'id': s.id,
        'member_id': s.member_id,
        'workout_type': s.workout_type,
        'date': s.date,
        'duration': s.duration
    } for s in sessions])

# View all workout sessions for a specific member
@app.route('/members/<int:id>/workouts', methods=['GET'])
def get_member_workouts(id):
    member = Member.query.get_or_404(id)
    return jsonify([{
        'id': s.id,
        'workout_type': s.workout_type,
        'date': s.date,
        'duration': s.duration
    } for s in member.sessions])

# Create the DB tables and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
