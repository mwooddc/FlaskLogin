from . import db
# The UserMixin library allows us to use built in methods called:
# is_authenticated, is_active, is_annoymous, get_id()
#see: https://youtu.be/2dEM-s3mRLE?t=282
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime



# class User(db.Model, UserMixin):
#     #The UserMixin library insists that the field in the database for a user is called
#     #id and not things like UID or user_ID, it has to be called id
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True)
#     username = db.Column(db.String(150), unique=True)
#     password = db.Column(db.String(150))
#     coach_or_player = db.Column(db.String(6)) #Coach or Player
#     date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(150), unique=True)
    Username = db.Column(db.String(150), unique=True)
    Password = db.Column(db.String(150))
    Forename = db.Column(db.String(255), nullable=False)
    Surname = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(50), nullable=False)  # 'Player' or 'Coach'
    survey_completed = db.Column(db.Boolean, default=False, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relationships
    
    # session_attendance = db.relationship('SessionAttendance', backref='user', lazy='dynamic')
    # match_attendance = db.relationship('MatchAttendance', backref='user', lazy='dynamic')
    # team_players = db.relationship('TeamPlayers', backref='user', lazy='dynamic')
    ratings_given = db.relationship('UserRatings', 
                                 foreign_keys='UserRatings.Raterid',
                                 backref='rater', 
                                 lazy='dynamic')
    ratings_received = db.relationship('UserRatings', 
                                    foreign_keys='UserRatings.Rateeid',
                                    backref='ratee', 
                                    lazy='dynamic')


class Match(db.Model, UserMixin):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    tennis_event_id = db.Column(db.Integer, db.ForeignKey('tennis_events.id'), nullable=False)
    tennis_event = db.relationship('TennisEvent', backref='matches')
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    singles_or_doubles = db.Column(db.String(7), nullable=False)
    sets_played = db.Column(db.Integer, nullable=False)
    sets_won = db.Column(db.Integer, nullable=False)
    won_or_lost = db.Column(db.String(4), nullable=False)
    comment = db.Column(db.Text)

    player1 = db.relationship('User', foreign_keys=[player1_id], backref='matches_as_player1')
    player2 = db.relationship('User', foreign_keys=[player2_id], backref='matches_as_player2')


class Notification(db.Model, UserMixin):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Recipient
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Sender
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

    # Relationships
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='notifications_received')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='notifications_sent')
    match = db.relationship('Match', backref='notifications')



class School(db.Model, UserMixin):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # Other school details like address, contact info, etc.

class TennisEvent(db.Model, UserMixin):
    __tablename__ = 'tennis_events'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    home_venue_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)#### needs to be HOME venue ID and AWAY venue ID
    away_venue_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)#### needs to be HOME venue ID and AWAY venue ID
    # Define the relationship with the School model for the home venue
    home_venue = db.relationship('School', foreign_keys=[home_venue_id], backref='home_events')
    # Define the relationship with the School model for the away venue
    away_venue = db.relationship('School', foreign_keys=[away_venue_id], backref='away_events')

class RatingCategory(db.Model, UserMixin):
    __tablename__ = 'rating_category'
    CategoryCode = db.Column(db.Integer, primary_key=True)
    CategoryDescription = db.Column(db.String(255), nullable=False)
    # Relationships
    user_ratings = db.relationship('UserRatings', backref='rating_category', lazy='dynamic')

class UserRatings(db.Model, UserMixin):
    __tablename__ = 'user_ratings'
    UserRatingsID = db.Column(db.Integer, primary_key=True)
    Raterid = db.Column(db.Integer, db.ForeignKey('users.id'))
    Rateeid = db.Column(db.Integer, db.ForeignKey('users.id'))
    RatingCategory = db.Column(db.Integer, db.ForeignKey('rating_category.CategoryCode'))
    Value = db.Column(db.Integer)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class PracticeSessions(db.Model, UserMixin):
    __tablename__ = 'practice_sessions'
    SessionID = db.Column(db.Integer, primary_key=True)
    SessionTime = db.Column(db.DateTime, default=datetime.utcnow)
    Comments = db.Column(db.String(255))
    # Relationships
    session_attendance = db.relationship('SessionAttendance', backref='practice_session', lazy='dynamic')

class SessionAttendance(db.Model, UserMixin):
    __tablename__ = 'session_attendance'
    SessionID = db.Column(db.Integer, db.ForeignKey('practice_sessions.SessionID'), primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    Attended = db.Column(db.Boolean)
    Late = db.Column(db.Boolean)
    Comments = db.Column(db.String(255))

# class Matches(db.Model, UserMixin):
#     __tablename__ = 'matches'
#     MatchID = db.Column(db.Integer, primary_key=True)
#     TeamName = db.Column(db.String(255), db.ForeignKey('teams.TeamName'))
#     OppositionName = db.Column(db.String(255), db.ForeignKey('opposition.OppositionName'))
#     FixtureTime = db.Column(db.DateTime, default=datetime.utcnow)
#     PostMatchFeedback = db.Column(db.String(255))
#     # Relationships
#     match_attendance = db.relationship('MatchAttendance', backref='match', lazy='dynamic')

# class MatchAttendance(db.Model, UserMixin):
#     __tablename__ = 'match_attendance'
#     MatchID = db.Column(db.Integer, db.ForeignKey('matches.MatchID'), primary_key=True)
#     id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
#     Attended = db.Column(db.Boolean)
#     Late = db.Column(db.Boolean)
#     Comments = db.Column(db.String(255))

# class TeamPlayers(db.Model, UserMixin):
#     __tablename__ = 'team_players'
#     TeamName = db.Column(db.String(255), db.ForeignKey('teams.TeamName'), primary_key=True)
#     id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
#     Position = db.Column(db.String(255))



def count_unread_notifications(user_id):
    count = Notification.query.filter_by(receiver_id=user_id, is_read=False).count()
    return count
