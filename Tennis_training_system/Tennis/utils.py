import math
import requests
from django.utils.timezone import now
from Tennis_training_system import settings
from .models import Game


def ask_MapBox_for_travel_time(origin_lat, origin_lon, dest_lat, dest_lon, api_key):
    """
    Calculate travel time between two locations using the Mapbox Directions API.
    """
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
    params = {
        'access_token': api_key,
        'geometries': 'geojson',
        'overview': 'full',
        'steps': 'true',
    }
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data['routes']:
        travel_time_seconds = data['routes'][0]['duration']
        travel_time_minutes = travel_time_seconds / 60
        return travel_time_minutes
    else:
        print("Error:", data.get('message', 'Unknown error, MapBox'))
        return None


def check_if_enough_time(event_end_time, next_event_start_time, event_court, next_event_court, request=None):
    """
    Check if there is enough time between two events to travel from one court to another.
    Returns travel_time, time_available, and alert status.
    """
    alert = False
    travel_time = None
    time_available = None
    MAPBOX_API_KEY = settings.MAPBOX_API_KEY

    if event_court.court_id != next_event_court.court_id:
        travel_time = ask_MapBox_for_travel_time(
            event_court.latitude, event_court.longitude,
            next_event_court.latitude, next_event_court.longitude,
            MAPBOX_API_KEY
        )

        if travel_time is not None:
            time_available = (next_event_start_time - event_end_time).total_seconds() / 60

            if travel_time > time_available:
                alert = True
                if request:
                    request.session['travel_time'] = travel_time
                    request.session['time_available'] = time_available
                    request.session['alert'] = alert

    return travel_time, time_available, alert


def recalculate_travel_time_for_games(updated_court):
    """
    Recalculate travel time for all games involving an updated court.
    Only affects games scheduled after the court update datetime.
    """
    update_time = now()

    affected_games = Game.objects.filter(
        court=updated_court,
        start_date_and_time__gte=update_time
    )

    print(f"Affected games count: {affected_games.count()}")
    for game in affected_games:
        print(f"Processing game: {game.name}, ID: {game.game_id}")
        user_games = Game.objects.filter(
            creator=game.creator,
            start_date_and_time__gte=update_time
        ).order_by('start_date_and_time')

        preceding_event = get_previous_event(user_games, game.start_date_and_time)
        following_event = get_following_event(user_games, game.end_date_and_time)

        if preceding_event:
            travel_time, time_available, alert = check_if_enough_time(
                preceding_event.end_date_and_time,
                game.start_date_and_time,
                preceding_event.court,
                updated_court
            )
            update_alert_status(game, travel_time, time_available, alert)

        if following_event:
            travel_time, time_available, alert = check_if_enough_time(
                game.end_date_and_time,
                following_event.start_date_and_time,
                updated_court,
                following_event.court
            )
            update_alert_status(game, travel_time, time_available, alert)


def update_alert_status(game, travel_time, time_available, alert):
    """
    Update the alert status, travel time, and available time for a game.
    """
    if travel_time is not None:
        game.alert = alert
        game.travel_time = travel_time
        game.time_available = time_available
        game.save()

        participants = game.participant_set.all()

        for participant in participants:
            participant.alert = alert
            participant.travel_time = travel_time
            participant.time_available = time_available
            participant.save()


def get_previous_event(user_games, new_game_start):
    """
    Get the most recent event that ends before the new game starts.
    :param user_games: A queryset of the user's games.
    :param new_game_start: The start time of the new game.
    :return: The preceding event or None if no such event exists.
    """
    preceding_event = None
    for game in user_games:
        if game.end_date_and_time <= new_game_start:
            preceding_event = game
        else:
            break
    return preceding_event


def get_following_event(user_games, new_game_end):
    """
    Get the next event that starts after the new game ends.
    :param user_games: A queryset of the user's games.
    :param new_game_end: The end time of the new game.
    :return: The following event or None if no such event exists.
    """
    following_event = None
    for game in user_games:
        if game.start_date_and_time >= new_game_end:
            following_event = game
            break
    return following_event