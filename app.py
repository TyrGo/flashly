import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, Card, User

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///flash'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)


# TODO: add auth for protected routes
# TODO: test

##############################################################################
# Helpers for routes


def seconds_due(due):
    """Calculate seconds card due to reappear"""

    return (due - datetime.now()).total_seconds()


def card_data(card):
    """Make dictionary of card attributes and username"""

    user = User.query.filter(User.id == card.user_id).first()
    return {"id": card.id, "bin": card.bin, "word": card.word,
            "defn": card.defn, "due": seconds_due(card.due),
            "user": user.username}


def get_card(user_id):
    """ Retrieve card for the user

    Return first card overdue or else first card by highest bin
    Except if no cards or all cards beyond bin 11, return message
    """

    cards = Card.query.filter(Card.user_id == user_id).first()
    if not cards:
        return {"message": "Please create new cards."}
    cards_q = Card.query.filter(Card.user_id == user_id, Card.bin < 12).\
        order_by('due')
    cards = cards_q.all()
    cards = [card_data(card) for card in cards]
    cards = [card for card in cards if card["due"] < 0]
    if cards:
        cards.sort(key=lambda card: card["bin"], reverse=True)
        return cards[0]
    card = cards_q.first()
    if card:
        return card_data(card)

    return {"message": "You have no more words to review. You are permanently done!"}


##############################################################################
# Sign/log in routes:


@app.route('/register', methods=["POST"])
def register():
    """Sign up user

    Create new user in database, and return token
    Otherwise return message if username/password invalid
    """

    data = request.get_json()
    try:
        User.sign_up(username=data["username"], password=data["password"])
        db.session.commit()
    except IntegrityError:
        return jsonify({'message': 'unauthorized'}), 401
    user = User.query.filter_by(username=data["username"]).first()
    token = user.generate_token(user.id, user.is_admin).decode('utf-8')

    return jsonify({'token': token})


@app.route('/token', methods=["GET", "POST"])
def log_in():
    """Login user. Return token or else message if invalid username/password"""

    data = request.get_json()
    user = User.authenticate(data["username"], data["password"])
    if user:
        token = user.generate_token(user.id, user.is_admin).decode('utf-8')
        return jsonify({'token': token})

    return jsonify({'message': 'unauthorized'}), 401


##############################################################################
# Card routes:

@app.route('/<int:user_id>/create_card', methods=["POST"])
def create_card(user_id):
    """Create new card in database for user"""

    data = request.get_json()
    card = Card(word=data["word"], defn=data["defn"], bin=0,
                wrongs=0, user_id=user_id)
    db.session.add(card)
    db.session.commit()

    return "card created"


@app.route('/retrieve_cards')
def retrieve_cards():
    """Retrieve all cards for all user from database"""

    cards = Card.query.all()
    cards = [card_data(card) for card in cards]
    cards.sort(key=lambda card: card["id"])

    return jsonify(cards)


@app.route('/<int:user_id>/retrieve_card')
def retrieve_card(user_id):
    """Retrieve next cards a user"""

    card = get_card(user_id)

    return jsonify(card)


@app.route('/<int:card_id>/update_card', methods=["PATCH"])
def update_card(card_id):
    """Updates word, definition and bin attributes of card in database"""

    data = request.get_json()
    card = Card.query.get(card_id)
    card.word, card.defn, card.bin = data["word"], data["defn"], 0
    db.session.commit()

    return jsonify({'message': 'card updated'})


@app.route('/<int:card_id>/bin_up', methods=["POST"])
def bin_up(card_id):
    """Raises bin of a card and resets the due date"""

    card = Card.query.get(card_id)
    card.bin += 1
    card.due = card.reset_due()
    db.session.commit()

    return jsonify({'message': 'bin raised'})


@app.route('/<int:card_id>/bin_down', methods=["POST"])
def bin_down(card_id):
    """Lowers bin and wrongs attributes of a card, resets the due date"""

    card = Card.query.get(card_id)
    card.wrongs += 1
    card.bin = 1
    card.due = card.reset_due()
    if card.wrongs == 10:
        card.bin = 13
    db.session.commit()

    return jsonify({'message': 'bin lowered'})


@app.route('/<int:card_id>/delete_card', methods=["DELETE"])
def delete_card(card_id):
    """Destroys a card from the database"""

    card = Card.query.get(card_id)
    db.session.delete(card)
    db.session.commit()

    return jsonify({'message': 'card deleted'})
