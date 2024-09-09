import os
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.timezone import now, make_aware, is_naive
from Tennis_training_system import settings
from django.db.models import F
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import math
from .utils import check_if_enough_time, get_previous_event, get_following_event
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.shortcuts import get_object_or_404
from .forms import EmailAuthenticationForm,  GameForm, CourtForm, CategoryForm, ProfilePictureUpdateForm, CustomPasswordChangeForm
from django.views.generic import FormView, TemplateView, View
from .models import Game, Category, Participant, Court, CustomUser, RecurringGroup
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, datetime, timezone, time
from django.http import JsonResponse, Http404
import logging

logger = logging.getLogger(__name__)


class RegisterView(FormView):
    """
    View to handle the user registration process.
    """
    template_name = 'Tennis/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Handle the form submission when valid data is provided.
        Saves the new user and logs them in automatically.

        :param form: The valid form containing the user's registration details.
        :return: Redirects to the success URL after the form is successfully submitted.
        """
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(FormView):
    """
    View to handle the user login process.
    """
    form_class = EmailAuthenticationForm
    template_name = 'Tennis/login.html'
    success_url = reverse_lazy('day')
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user is already authenticated.
        If so, redirect them to the success URL (the 'day' view).

        :param request: The HTTP request object.
        :return: A redirect if the user is authenticated, otherwise dispatch the view as normal.
        """
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Handle the form submission when valid data is provided.
        Authenticates the user using their email and password.

        :param form: The valid login form containing the user's email and password.
        :return: Redirects the authenticated user to the success URL, or reloads the form on failure.
        """
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=email, password=password)

        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'Invalid email or password.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Handle the case when the form submission is invalid.
        Displays an error message indicating an invalid email or password.

        :param form: The invalid form containing errors.
        :return: Reloads the login form with error messages.
        """
        messages.error(self.request, 'Invalid email or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    View to handle the user logout process.
    This view logs the user out and displays a success message upon logout.
    """
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        """
        Handle the logout process and display a success message after the user logs out.

        :param request: The HTTP request object.
        :return: Redirects to the next page (login page) after logging out.
        """
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


class DayView(LoginRequiredMixin, TemplateView):
    """
    View for displaying and managing games on a daily basis. This view handles
    the display of games, their creation, update, and deletion, as well as
    the addition of courts and categories.
    """
    model = Game
    template_name = 'Tennis/day.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template. Additional context is added for staff users.

        :param kwargs: Additional context keyword arguments.
        :return: A dictionary of context data.
        """

        context = super().get_context_data(**kwargs)
        context.update(self.get_base_context())
        if self.request.user.is_staff:
            context.update(self.get_staff_context())
        return context

    def get_base_context(self):
        """
        Get the base context data used for rendering the template. This includes the hours,
        breaklines, game form, and available categories.

        :return: A dictionary containing base context data.
        """
        return {
            'hours': range(1, 24),
            'breaklines': range(23),
            'game_form': GameForm(),
            'categories': Category.objects.all(),
        }

    def get_staff_context(self):
        """
        Get additional context data for staff users, including court and category forms.

        :return: A dictionary containing context data specific to staff users.
        """
        return {
            'court_form': CourtForm(),
            'category_form': CategoryForm(),
        }

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True))
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to the view. This method checks if the request is an AJAX request
        and processes it accordingly. Otherwise, it handles the request as a standard GET request.

        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A JSON response for AJAX requests or a rendered template response.
        """
        if self.is_ajax(request):
            if 'fetch_game_details' in request.GET and 'game_id' in request.GET:
                game_id = request.GET.get('game_id')
                game = get_object_or_404(Game, game_id=game_id)
                game_data = {
                    'name': game.name,
                    'start_date_and_time': game.start_date_and_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_date_and_time': game.end_date_and_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'category': game.category.category_id,
                    'category_name': game.category.name,
                    'court': game.court.court_id,
                    'court_name': game.court.name,
                    'participants': list(game.participant_set.values_list('user__email', 'user__username')),
                    'is_creator': (game.creator == request.user),
                    'group': game.group.group_id if game.group else None,
                    'recurrence_type': game.group.recurrence_type if game.group else None,
                    'end_date_of_recurrence': game.group.end_date if game.group else None,
                }
                return JsonResponse(game_data)

            date_str = request.GET.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else now().date()
            events, date_info = self.get_events_and_date_info(date)
            return JsonResponse({
                'events': events,
                **date_info,
            })
        else:
            return super().get(request, *args, **kwargs)

    def is_ajax(self, request):
        """
        Determine if the current request is an AJAX request.

        :param request: The HTTP request object.
        :return: True if the request is an AJAX request, False otherwise.
        """
        return request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'XMLHttpRequest' in request.headers.get(
            'X-Requested-With', '')

    def get_events_and_date_info(self, date):
        """
        Retrieve events and related date information for a specific date.

        :param date: The date for which to retrieve events.
        :return: A tuple containing a list of events and a dictionary with date information.
        """
        user = self.request.user

        events_query = Game.objects.filter(
            start_date_and_time__date=date,
            participant__user=user
        ).annotate(
            alert_status=F('participant__alert')
        ).values(
            'game_id',
            'name',
            'category__name',
            'category__color',
            'start_date_and_time',
            'end_date_and_time',
            'creator',
            'creator__profile_picture',
            'alert_status',
        ).order_by('start_date_and_time')

        events = list(events_query)

        for event in events:
            event['start_date_and_time'] = event['start_date_and_time'].strftime('%Y-%m-%d %H:%M:%S')
            event['end_date_and_time'] = event['end_date_and_time'].strftime('%Y-%m-%d %H:%M:%S')
            start_time = event['start_date_and_time'].split(' ')[1]
            end_time = event['end_date_and_time'].split(' ')[1]
            start_time_minutes = self.convert_string_time_to_minutes(start_time)
            end_time_minutes = self.convert_string_time_to_minutes(end_time)
            duration = end_time_minutes - start_time_minutes
            event['margin_top'] = (start_time_minutes / 60) * 100
            event['height'] = (duration / 60) * 100

            profile_picture = event.get('creator__profile_picture', '')
            if profile_picture:
                event['profile_picture_url'] = f"{settings.MEDIA_URL}{profile_picture}"
            else:
                event['profile_picture_url'] = settings.STATIC_URL + 'images/Ola.png'

            event['is_creator'] = (event['creator'] == self.request.user.user_id)

        date_info = {
            'current_date': date.strftime('%d %B %Y'),
            'current_day_of_week': date.strftime('%A'),
            'prev_date': (date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'next_date': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
        }

        return events, date_info

    def convert_string_time_to_minutes(self, time_str):
        """
        Convert a time string in 'HH:MM:SS' format into the total number of minutes.

        :param time_str: A string representing time in 'HH:MM:SS' format.
        :return: The total number of minutes as an integer.
        """
        hours, minutes, _ = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to the view. Processes various types of form submissions
        including game updates, new game submissions, game deletions, and form submissions
        for courts and categories.

        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A JSON response indicating success or failure of the request.
        """
        if self.is_ajax(request):
            if 'update_game' in request.POST and request.POST.get('game_id'):
                return self.handle_game_update(request)

            elif 'submit_game' in request.POST:
                return self.handle_game_form(request)

            elif 'delete_game' in request.POST:
                return self.handle_game_delete(request)

            elif 'submit_category' in request.POST:
                return self.handle_category_form(request)

        return JsonResponse({'error': 'Invalid request'}, status=400)

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True))
    def handle_game_form(self, request):
        """
        Handle the creation of a new game. Uses the _handle_game_form_logic method
        to process the form and create a new game instance.

        :param request: The HTTP request object.
        :return: A JSON response indicating success or failure of the game creation.
        """
        return self._handle_game_form_logic(request, is_update=False)

    @method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True))
    def handle_game_update(self, request):
        """
        Handle the update of an existing game. Uses the _handle_game_form_logic method
        to process the form and update the existing game instance.

        :param request: The HTTP request object.
        :return: A JSON response indicating success or failure of the game update.
        """
        game_id = request.POST.get('game_id')
        if not game_id:
            return JsonResponse({'success': False, 'message': 'Game ID is required.'}, status=400)

        try:
            game = get_object_or_404(Game, game_id=game_id, creator=request.user)
        except Http404:
            return JsonResponse({'success': False, 'message': 'Game not found or permission denied.'}, status=404)

        return self._handle_game_form_logic(request, is_update=True, game_instance=game)

    def _handle_game_form_logic(self, request, is_update=False, game_instance=None):
        """
        Core logic for handling both creation and update of a game.
        This method processes the game form, checks for scheduling conflicts
        for both the game creator and each participant, and handles recurrence logic.
        """
        game_form = GameForm(request.POST, instance=game_instance) if is_update else GameForm(request.POST)

        if not game_form.is_valid():
            return JsonResponse({'success': False, 'errors': game_form.errors.as_json()}, status=400)

        participants = game_form.cleaned_data.get('participants', [])
        recurrence_type = game_form.cleaned_data.get('recurrence_type')
        end_date_of_recurrence = game_form.cleaned_data.get('end_date_of_recurrence')

        game_instance = self._save_game_instance(game_form, game_instance, request, is_update, commit=False)

        conflicts = self._handle_participants(request, game_instance, participants, is_update, dry_run=True)

        if len(conflicts) > 0 and request.POST.get('confirm') != 'true':
            logger.info(f'Sending conflicts response: {conflicts}')
            return JsonResponse({
                'success': False,
                'message': f"There are conflicts for the following participants:\n" +
                           "\n".join([
                               f"{conflict['participant']}: (Travel: {math.ceil(conflict['travel_time'] or 0)} mins, Gap: {math.ceil(conflict['time_available'] or 0)} mins)"
                               for conflict in conflicts]),
                'confirm_needed': True
            }, status=409)

        if not is_update:
            if recurrence_type not in [None, '', 'none', 'Null', 'null'] and end_date_of_recurrence:
                recurring_group = RecurringGroup.objects.create(
                    recurrence_type=recurrence_type,
                    start_date=game_instance.start_date_and_time.date(),
                    end_date=end_date_of_recurrence
                )
                game_instance.group = recurring_group

        game_instance = self._save_game_instance(game_form, game_instance, request, is_update, commit=True)
        self._handle_participants(request, game_instance, participants, is_update, dry_run=False)

        game_form.save_m2m()

        if is_update and game_instance.group:
            self._handle_recurrence_update(game_instance, participants)
        elif recurrence_type not in [None, '', 'none', 'Null', 'null'] and end_date_of_recurrence:
            self._handle_recurrence(game_instance, participants, recurrence_type, end_date_of_recurrence)

        return JsonResponse({'success': True, 'message': 'Game added successfully'})

    def _save_game_instance(self, game_form, game_instance, request, is_update, commit=True):
        """
        Save the game instance and assign the creator if it's a new game.
        If commit is False, it saves the instance but doesn't commit to the database yet.
        """
        game_instance = game_form.save(commit=False)  # Save the form but don't commit yet
        if not is_update:
            game_instance.creator = request.user

        if commit:
            game_instance.save()  # Now commit to the database if commit is True
        return game_instance

    def _handle_participants(self, request, game_instance, participants, is_update, dry_run=False):
        conflicts = []
        current_participants = set()

        # Only retrieve current participants if it's an update and game_instance is saved
        if game_instance.game_id and is_update:
            current_participants = set(game_instance.participant_set.all().values_list('user', flat=True))

        if is_update:
            new_participants = set(participants.values_list('user_id', flat=True))
            participants_to_remove = current_participants - new_participants
            participants_to_add = new_participants - current_participants

            if not dry_run:
                for participant_id in participants_to_remove:
                    Participant.objects.filter(user__user_id=participant_id, game=game_instance).delete()

                for user_id in participants_to_add:
                    user_instance = CustomUser.objects.get(user_id=user_id)
                    Participant.objects.get_or_create(user=user_instance, game=game_instance)

                simulated_participants = set(game_instance.participant_set.all().values_list('user', flat=True))
            else:
                simulated_participants = new_participants
        else:
            simulated_participants = set(participants.values_list('user_id', flat=True))

            if not dry_run:
                for user in participants:
                    Participant.objects.get_or_create(user=user, game=game_instance)

        for user_id in simulated_participants:
            user_instance = CustomUser.objects.get(user_id=user_id)
            print(f'looping through {user_instance}')
            if not dry_run:
                participant_instance, _ = Participant.objects.get_or_create(user=user_instance, game=game_instance)
            else:
                participant_instance = Participant(user=user_instance, game=game_instance)

            participant_games = Game.objects.filter(
                participant__user=user_instance,
                start_date_and_time__date=game_instance.start_date_and_time.date()
            ).order_by('start_date_and_time')

            participant_preceding_event = get_previous_event(participant_games, game_instance.start_date_and_time)
            if participant_preceding_event:
                conflict = self._check_participant_conflict(
                    request, participant_instance, participant_preceding_event, game_instance, dry_run
                )
                if conflict:
                    conflicts.append(conflict)

            participant_following_event = get_following_event(participant_games, game_instance)
            if participant_following_event:
                following_event_participants = participant_following_event.participant_set.all()
                for following_participant in following_event_participants:
                    conflict = self._check_participant_conflict(
                        request, following_participant, game_instance, participant_following_event, dry_run
                    )
                    if conflict:
                        conflicts.append(conflict)

        return conflicts

    def _check_participant_conflict(self, request, participant_instance, preceding_event, following_event, dry_run=False):
        """
        Helper function to handle participant conflict checks.
        If dry_run is False, it also saves the calculated travel time, available time, and alert to the database.
        """
        if preceding_event is None:
            participant_instance.alert = False
            participant_instance.travel_time = None
            participant_instance.time_available = None
            participant_instance.save()
            return None

        event_end_time = preceding_event.end_date_and_time
        new_game_start = following_event.start_date_and_time
        event_court = preceding_event.court
        new_game_court = following_event.court

        if not event_court:
            return

        travel_time, time_available, alert = check_if_enough_time(
            event_end_time,
            new_game_start,
            event_court,
            new_game_court,
            request
        )

        if not dry_run:
            participant_instance.alert = alert
            participant_instance.travel_time = travel_time
            participant_instance.time_available = time_available
            participant_instance.save()

        if travel_time is not None and time_available is not None:
            if travel_time > time_available:
                return {
                    'participant': participant_instance.user.username,
                    'travel_time': travel_time,
                    'time_available': time_available,
                    'alert': alert
                }

        return None

    def _handle_recurrence_update(self, game, participants):
        print("handling reccurence update!!!!!!")
        current_start = game.start_date_and_time
        current_end = game.end_date_and_time
        idx = 0

        if game.group_id:
            games_in_group = Game.objects.filter(group_id=game.group.group_id).order_by('start_date_and_time')

            for idx, game_instance in enumerate(games_in_group):
                if idx == 0:
                    game_instance.start_date_and_time = current_start
                    game_instance.end_date_and_time = current_end
                else:
                    delta = self._get_delta_by_recurrence_type(game.group.recurrence_type, idx)
                    game_instance.start_date_and_time = current_start + delta
                    game_instance.end_date_and_time = current_end + delta

                game_instance.court = game.court
                game_instance.name = game.name
                game_instance.save()

                game_instance.participant_set.all().delete()
                for user in participants:
                    Participant.objects.create(user=user, game=game_instance)

                for participant in participants:
                    print(f"Processing participant: {participant.username}")

                    participant_games = Game.objects.filter(
                        participant__user=participant,
                        start_date_and_time__date=game.start_date_and_time.date()
                    ).order_by('start_date_and_time')

                    participant_preceding_event = get_previous_event(participant_games, game.start_date_and_time)
                    if participant_preceding_event:
                        self._check_participant_conflict(
                            None, participant, participant_preceding_event, game, dry_run=False
                        )

                    participant_following_event = get_following_event(participant_games, game)
                    if participant_following_event:
                        following_event_participants = participant_following_event.participant_set.all()
                        for following_participant in following_event_participants:
                            self._check_participant_conflict(
                                None, following_participant, game, participant_following_event, dry_run=False)

    def _handle_recurrence(self, game, participants, recurrence_type, end_date_of_recurrence):
        """
        Handles the creation of recurring game events based on recurrence type and end date.

        :param game: The original game instance.
        :param participants: List of participants for the game.
        :param recurrence_type: The type of recurrence (e.g., daily, weekly).
        :param end_date_of_recurrence: The end date for the recurrence.
        """
        print("Handling recurrence creation")
        end_date_of_recurrence = make_aware(datetime.combine(end_date_of_recurrence, time(23, 59)))
        current_start = game.start_date_and_time
        current_end = game.end_date_and_time
        idx = 1

        while current_start <= end_date_of_recurrence:
            if current_start != game.start_date_and_time:
                print(f"Creating game for date: {current_start}")
                new_game = Game.objects.create(
                    name=game.name,
                    category=game.category,
                    court=game.court,
                    creator=game.creator,
                    start_date_and_time=current_start,
                    end_date_and_time=current_end,
                    group=game.group
                )
                for user in participants:
                    Participant.objects.create(user=user, game=new_game)

                # Check for adjacent games (preceding and following) for each participant
                for participant in participants:
                    print(f"Processing participant: {participant.username}")

                    participant_games = Game.objects.filter(
                        participant__user=participant,
                        start_date_and_time__date=game.start_date_and_time.date()
                    ).order_by('start_date_and_time')

                    participant_preceding_event = get_previous_event(participant_games, game.start_date_and_time)
                    if participant_preceding_event:
                        self._check_participant_conflict(
                            None, participant, participant_preceding_event, game, dry_run=False
                        )

                    participant_following_event = get_following_event(participant_games, game)
                    if participant_following_event:
                        following_event_participants = participant_following_event.participant_set.all()
                        for following_participant in following_event_participants:
                            self._check_participant_conflict(
                                None, following_participant, game, participant_following_event, dry_run=False)

            delta = self._get_delta_by_recurrence_type(recurrence_type, idx)

            print(f"Before applying delta: Start={current_start}, End={current_end}, Delta={delta}")
            current_start += delta
            current_end += delta
            print(f"After applying delta: Start={current_start}, End={current_end}")

            idx = 1

    def _get_delta_by_recurrence_type(self, recurrence_type, idx):
        """
        Return the appropriate time delta based on recurrence type and index.
        """
        if recurrence_type == 'daily':
            return timedelta(days=idx)
        elif recurrence_type == 'weekly':
            return timedelta(weeks=idx)
        elif recurrence_type == 'biweekly':
            return timedelta(weeks=2 * idx)
        elif recurrence_type == 'monthly':
            return relativedelta(months=idx)
        return timedelta(0)

    def handle_game_delete(self, request):
        """
        Handle the deletion of a game. Checks if the user is the creator of the game
        and deletes it if permitted. Also, updates travel time, time available, and alert
        for participants in adjacent games after the deletion.

        :param request: The HTTP request object.
        :return: A JSON response indicating success or failure of the game deletion.
        """
        game_id = request.POST.get('game_id')
        game = get_object_or_404(Game, game_id=game_id, creator=request.user)

        if game.creator != request.user:
            return JsonResponse({'success': False, 'message': 'You do not have permission to delete this game'},
                                status=403)

        # Identify participants of the game to be deleted
        participants = game.participant_set.all()

        adjacent_games = {}
        for participant in participants:
            preceding_game, following_game = self._get_adjacent_games(participant.user, game)
            if preceding_game or following_game:
                adjacent_games[participant.user] = (preceding_game, following_game)

        # Delete the game (either group or single occurrence)
        if game.group not in [None, '', 'none', 'Null', 'null']:
            Game.objects.filter(group=game.group).delete()
        else:
            Game.objects.filter(game_id=game_id).delete()

        # After deletion, update travel time, time available, and alert for adjacent games
        for user, (preceding_game, following_game) in adjacent_games.items():
            self._update_conflicts_after_deletion(user, preceding_game, following_game)

        return JsonResponse({'success': True, 'message': 'Game(s) deleted successfully'})

    def _get_adjacent_games(self, user, game):
        """
        Get the preceding and following games for a participant on the same day as the given game.
        """
        games_on_same_day = Game.objects.filter(
            participant__user=user,
            start_date_and_time__date=game.start_date_and_time.date()
        ).exclude(game_id=game.game_id).order_by('start_date_and_time')

        preceding_game = get_previous_event(games_on_same_day, game.start_date_and_time)
        following_game = get_following_event(games_on_same_day, game)

        return preceding_game, following_game

    def _update_conflicts_after_deletion(self, user, preceding_game, following_game):
        """
        Updates travel time, available time, and alert between adjacent games.
        Handles cases where either preceding or following game is None.
        """
        if preceding_game and following_game:
            # Both games exist, handle conflicts between them
            participant_instance = Participant.objects.get(user=user, game=following_game)
            self._check_participant_conflict(
                request=None,
                participant_instance=participant_instance,
                preceding_event=preceding_game,
                following_event=following_game,
                dry_run=False
            )
        elif preceding_game:
            participant_instance = Participant.objects.get(user=user, game=preceding_game)
            pre_preceding_current = self._get_adjacent_games(participant_instance.user, preceding_game)
            pre_preceding = pre_preceding_current[0]
            self._check_participant_conflict(
                request=None,
                participant_instance=participant_instance,
                preceding_event=pre_preceding,
                following_event=preceding_game,
                dry_run=False
            )
        elif following_game:
            # Only the following game exists, no preceding game
            participant_instance = Participant.objects.get(user=user, game=following_game)
            # Reset the alert, travel_time, and available_time for this game
            participant_instance.alert = False
            participant_instance.travel_time = None
            participant_instance.time_available = None
            participant_instance.save()

    def handle_category_form(self, request):
        """
        Handle the submission of a new category form. Validates and saves the category data.

        :param request: The HTTP request object.
        :return: A JSON response indicating success or failure of the category creation.
        """
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return JsonResponse({'success': True, 'message': 'Category added successfully'})

        return JsonResponse({'success': False, 'errors': category_form.errors.as_json()}, status=400)


class UsersProfile(LoginRequiredMixin, View):
    """
    View for displaying and managing the user's profile. This view handles both
    updating the profile picture and changing the user's password.
    """
    template_name = 'Tennis/users_profile.html'

    def get(self, request):
        """
        Handle GET requests to display the user's profile page.
        This includes a form for updating the profile picture and
        a form for changing the password.

        :param request: The HTTP request object.
        :return: A rendered template response containing the profile and password forms.
        """
        profile_form = ProfilePictureUpdateForm()
        password_form = CustomPasswordChangeForm(user=request.user)

        context = {
            'profile_form': profile_form,
            'password_form': password_form,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, self.template_name, context)

    def save_profile_picture(self, profile_picture):
        """
        Save the uploaded profile picture to the media directory.

        :param profile_picture: The uploaded profile picture file.
        :return: The file path where the profile picture is saved.
        """
        file_name = profile_picture.name
        file_path = os.path.join('profile_pictures', file_name)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'wb+') as destination:
            for chunk in profile_picture.chunks():
                destination.write(chunk)

        return file_path

    def post(self, request):
        """
        Handle POST requests for updating either the profile picture or the password.
        This method processes the form submissions and handles form validation,
        saving the updated profile picture or password if valid.

        :param request: The HTTP request object.
        :return: A rendered template response with updated forms and success/error messages.
        """
        if 'profile_picture' in request.FILES:
            profile_form = ProfilePictureUpdateForm(request.POST, request.FILES)
            if profile_form.is_valid():
                profile_picture = profile_form.cleaned_data['profile_picture']
                file_path = self.save_profile_picture(profile_picture)
                request.user.profile_picture = file_path
                request.user.save()
                messages.success(request, 'Your profile picture has been updated.')
            else:
                messages.error(request, 'There has been an error while updating the profile picture.')

        elif 'old_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated.')
            else:
                messages.error(request, 'Please correct the error below.')

        profile_form = ProfilePictureUpdateForm()
        password_form = CustomPasswordChangeForm(user=request.user)

        context = {
            'profile_form': profile_form,
            'password_form': password_form,
        }
        return render(request, self.template_name, context)


class CourtsView(LoginRequiredMixin, TemplateView):
    """
    View to list all courts, and handle the updates and deletion. Updates and deletion can be done only by admins.
    """
    model = Court
    template_name = 'Tennis/courts.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for the template. Additional context is added for staff users.

        :param kwargs: Additional context keyword arguments.
        :return: A dictionary of context data.
        """
        context = super().get_context_data(**kwargs)
        context['courts'] = Court.objects.all()
        if self.request.user.is_staff:
            context['court_form'] = CourtForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle form submissions for adding or updating a court,
        and handle AJAX requests to fetch court data.
        """
        if not request.user.is_staff:
            return JsonResponse({'error': 'You do not have permission to perform this action'}, status=403)

        if self.is_ajax(request) and 'fetch_court_data' in request.POST:
            court_id = request.POST.get('court_id')
            court = get_object_or_404(Court, court_id=court_id)
            data = {
                'name': court.name,
                'building_number': court.building_number,
                'street': court.street,
                'city': court.city,
                'postal_code': court.postal_code,
                'country': court.country,
                'latitude': court.latitude,
                'longitude': court.longitude,
            }
            return JsonResponse(data)

        court_id = request.POST.get('court_id')
        if 'delete_court' in request.POST:
            return self.handle_court_delete(request)

        if court_id:
            court = get_object_or_404(Court, court_id=court_id)
            court_form = CourtForm(request.POST, instance=court)
        else:
            court_form = CourtForm(request.POST)

        if court_form.is_valid():
            court_form.save()
            return JsonResponse({'success': True, 'message': 'Court added/updated successfully'})
        return JsonResponse({'success': False, 'errors': court_form.errors.as_json()}, status=400)

    def handle_court_delete(self, request):
        """
        Handle the deletion of a court. Only admin users are allowed to delete a court.

        :param request: The HTTP request object.
        :return: A JSON response indicating success or failure of the court deletion.
        """
        court_id = request.POST.get('court_id')
        if not court_id:
            return JsonResponse({'success': False, 'message': 'Court ID is missing'}, status=400)
        court = get_object_or_404(Court, court_id=court_id)

        if request.user.is_staff:
            court.delete()
            return JsonResponse({'success': True, 'message': 'Court deleted successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'You do not have permission to delete this court'},
                                status=403)

    def is_ajax(self, request):
        """
        Determine if the current request is an AJAX request.

        :param request: The HTTP request object.
        :return: True if the request is an AJAX request, False otherwise.
        """
        return request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'XMLHttpRequest' in request.headers.get(
            'X-Requested-With', '')