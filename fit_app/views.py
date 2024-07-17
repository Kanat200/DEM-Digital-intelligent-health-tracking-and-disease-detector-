import os
import json
from pprint import pprint
import numpy as np
import pickle
import sklearn

from django.db.models import Sum, F, Avg
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from allauth.socialaccount.models import SocialAccount
import datetime
import time

from fit_app.models import DataSource, DataPoint, UserProfile, PredictHistory
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = "credentials/client_secret_365722972126-5on9hh3ar4na8ensjfi1he3178ofnpub.apps.googleusercontent.com.json"

SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.activity.write',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.body.write',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.location.write',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
    'https://www.googleapis.com/auth/fitness.nutrition.write',
    'https://www.googleapis.com/auth/fitness.reproductive_health.read',
    'https://www.googleapis.com/auth/fitness.reproductive_health.write',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.write',
    'https://www.googleapis.com/auth/fitness.blood_glucose.read',
    'https://www.googleapis.com/auth/fitness.blood_glucose.write',
    'https://www.googleapis.com/auth/fitness.blood_pressure.read',
    'https://www.googleapis.com/auth/fitness.blood_pressure.write',
    'https://www.googleapis.com/auth/fitness.body_temperature.read',
    'https://www.googleapis.com/auth/fitness.body_temperature.write',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.write',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]


def authorize(request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:8000/oauth2callback'
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return redirect(authorization_url)


def oauth2callback(request):
    state = request.session.get('state')
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri='http://127.0.0.1:8000/oauth2callback'
    )
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    # Fetch user info from Google
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info.get('email')
    first_name = user_info.get('given_name')
    last_name = user_info.get('family_name')

    # Check if user exists, create if not
    user, created = User.objects.get_or_create(email=email, defaults={
        'username': email,
        'first_name': first_name,
        'last_name': last_name,
    })

    # Ensure the user profile is created
    UserProfile.objects.get_or_create(user=user)

    # Ensure social account is linked
    social_account, _ = SocialAccount.objects.get_or_create(user=user, uid=user_info.get('id'), provider='google')

    # Set backend attribute
    user.backend = 'allauth.account.auth_backends.AuthenticationBackend'

    # Log the user in
    django_login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')

    try:
        start = int((time.time() - 7 * 24 * 60 * 60) * 1000000000)
        last_record = DataPoint.objects.filter(user=user).last()
        if last_record:
            start = int(last_record.end_time.timestamp() * 1000000000)

        service = build('fitness', 'v1', credentials=credentials)
        data_sources = service.users().dataSources().list(userId='me').execute()

        for data_source in data_sources['dataSource']:
            data_type = data_source['dataType']['name']
            data_stream_id = data_source['dataStreamId']

            if data_type in ["com.google.active_minutes",
                             "com.google.blood_pressure",
                             "com.google.calories.bmr",
                             "com.google.distance.delta",
                             "com.google.heart_rate.bpm",
                             "com.google.height",
                             "com.google.speed",
                             "com.google.weight"]:
                # Save data source to the database
                data_source_obj, created = DataSource.objects.get_or_create(
                    data_type=data_type,
                )

                data_set_id = f"{start}-{int(time.time() * 1000000000)}"

                dataset = service.users().dataSources().datasets().get(
                    userId='me',
                    dataSourceId=data_stream_id,
                    datasetId=data_set_id
                ).execute()

                points = dataset.get('point', [])
                for point in points:
                    start_time = nanos_to_datetime(int(point['startTimeNanos']))
                    end_time = nanos_to_datetime(int(point['endTimeNanos']))
                    converted_values = [convert_value(data_type, v) for v in point['value']]
                    value = ', '.join(converted_values)

                    # Save data point to the database
                    DataPoint.objects.get_or_create(
                        data_source=data_source_obj,
                        start_time=start_time,
                        end_time=end_time,
                        value=value,
                        user=user
                    )

        return redirect('profile')
    except Exception as e:
        return render(request, 'fit_app/error.html', {'message': str(e)})


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        print("PROFILE UPDATE")
        user_profile = UserProfile.objects.get_or_create(user=user)

        # Update user details
        user.first_name = request.POST.get('name', user.first_name)
        user.email = request.POST.get('email', user.email)

        # Handle avatar upload
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']

        user.save()
        user_profile.save()

        return redirect('profile')

    user_profile = UserProfile.objects.get(user=request.user)

    context = {
        'avatar': user_profile.avatar,
        'name': request.user.first_name,
        'email': request.user.email
    }
    return render(request, 'fit_app/profile.html', context)


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def login(request):
    print(request.user)
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            return redirect('profile')
        else:
            return render(request, 'fit_app/login.html', {'error': 'Invalid username or password'})
    return render(request, 'fit_app/login.html')


def logout(request):
    django_logout(request)
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        name = request.POST['full_name']
        email = request.POST['email']
        username = email
        password = request.POST['password']
        user = User.objects.create_user(username, email, password)
        user.first_name = name
        user.save()
        return redirect('login')
    return render(request, 'fit_app/signup.html')


def get_suffix(type):
    suffix_dict = {
        'com.google.active_minutes': 'm',
        'com.google.blood_pressure': '',
        'com.google.calories.bmr': 'ccal',
        'com.google.distance.delta': 'meter(s)',
        'com.google.heart_rate.bpm': 'BPM',
        'com.google.height': 'cm',
        'com.google.speed': 'm/s',
        'com.google.weight': 'kg',
    }
    return suffix_dict[type]


def get_state(type, value):
    state_dict = {
        'com.google.active_minutes': [30, 500],
        'com.google.blood_pressure': [80, 120],
        'com.google.calories.bmr': [1500, 3000],
        'com.google.distance.delta': [3000, 15000],
        'com.google.heart_rate.bpm': [60, 120],
        'com.google.height': [0, 300],
        'com.google.speed': [3, 30],
        'com.google.weight': [50, 90],
    }
    return state_dict[type][0] <= value <= state_dict[type][1]


@login_required
def profile(request):
    try:
        user = request.user
        if not user:
            credentials = Credentials(**request.session['credentials'])
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            avatar = user_info.get('picture')
            name = user_info.get('name')
            email = user_info.get('email')
        else:
            avatar = None
            name = user.first_name + " " + user.last_name
            email = user.email
        data = {}
        dataSourceDict = {
            'com.google.active_minutes': 'Activity minutes',
            'com.google.blood_pressure': 'Blood Pressure',
            'com.google.calories.bmr': 'Calories BMR',
            'com.google.distance.delta': 'Passed Distance',
            'com.google.heart_rate.bpm': 'Average Heart rate',
            'com.google.height': 'Average Height',
            'com.google.speed': 'Average Speed',
            'com.google.weight': 'Average Weigth',
        }
        sources = DataSource.objects.all()
        for entry in sources:
            key = dataSourceDict[entry.data_type]
            queryset = DataPoint \
                .objects \
                .filter(user=request.user) \
                .filter(data_source_id=entry.id) \
                .annotate(date_only=TruncDate('end_time')) \
                .values('date_only') \
                .annotate(
                total_value=Sum('value') if ['com.google.active_minutes', 'com.google.distance.delta'] else Avg(
                    'value')) \
                .order_by('-date_only')
            if key not in data:
                data[key] = []
            for item in queryset:
                data[key].append({'date': f"{item['date_only']}",
                                  'value': f"{round(item['total_value'], 2)} {get_suffix(entry.data_type)}"})

        context = {
            'avatar': avatar,
            'name': name,
            'email': email,
            'fit_items': data or []
        }

        return render(request, 'fit_app/profile.html', context)
    except Exception as e:
        return render(request, 'fit_app/error.html', {'message': str(e)})


def nanos_to_datetime(nanos):
    return datetime.datetime.fromtimestamp(nanos / 1e9).strftime('%Y-%m-%d %H:%M:%S')


def convert_value(data_type, value):
    if 'fpVal' in value:
        if data_type in ['com.google.height', ]:
            return f"{value['fpVal'] * 100:.2f}"
        elif data_type == 'com.google.weight':
            return f"{value['fpVal']:.2f}"
        elif data_type == 'com.google.calories.expended':
            return f"{value['fpVal']:.2f}"
        elif data_type == 'com.google.distance.delta':
            return f"{value['fpVal']:.2f}"
        elif data_type == 'com.google.speed':
            return f"{value['fpVal']:.2f}"
        else:
            return str(value['fpVal'])
    elif 'intVal' in value:
        if data_type == 'com.google.step_count.delta':
            return f"{value['intVal']}"
        else:
            return str(value['intVal'])
    else:
        return str(value)


@login_required
def get_fit_data(request):
    credentials = Credentials(**request.session['credentials'])
    print(request.user)
    try:
        start = int((time.time() - 7 * 24 * 60 * 60) * 1000000000)
        last_record = DataPoint.objects.last()
        if last_record:
            start = int(last_record.end_time.timestamp() * 1000000000)

        service = build('fitness', 'v1', credentials=credentials)
        data_sources = service.users().dataSources().list(userId='me').execute()

        for data_source in data_sources['dataSource']:
            data_type = data_source['dataType']['name']
            data_stream_id = data_source['dataStreamId']

            if data_type in ["com.google.active_minutes",
                             "com.google.blood_pressure",
                             "com.google.calories.bmr",
                             "com.google.distance.delta",
                             "com.google.heart_rate.bpm",
                             "com.google.height",
                             "com.google.speed",
                             "com.google.weight"]:
                # Save data source to the database
                data_source_obj, created = DataSource.objects.get_or_create(
                    data_type=data_type,
                )

                data_set_id = f"{start}-{int(time.time() * 1000000000)}"

                dataset = service.users().dataSources().datasets().get(
                    userId='me',
                    dataSourceId=data_stream_id,
                    datasetId=data_set_id
                ).execute()

                points = dataset.get('point', [])
                for point in points:
                    start_time = nanos_to_datetime(int(point['startTimeNanos']))
                    end_time = nanos_to_datetime(int(point['endTimeNanos']))
                    converted_values = [convert_value(data_type, v) for v in point['value']]
                    value = ', '.join(converted_values)

                    # Save data point to the database
                    DataPoint.objects.get_or_create(
                        data_source=data_source_obj,
                        start_time=start_time,
                        end_time=end_time,
                        value=value,
                        user=request.user
                    )

        data_sets = DataSource.objects.prefetch_related('data_points').all()
        context = {'data_sets': data_sets}
        return render(request, 'fit_app/fit_data.html', context)
    except Exception as e:
        return render(request, 'fit_app/error.html', {'message': str(e)})


@login_required
def bmi(request):
    return render(request, 'fit_app/bmi.html')


@login_required
def heartbeat(request):
    return render(request, 'fit_app/heartbeat.html')


@login_required
def heartpredict(request):
    if request.method == 'POST':
        try:

            with open('model/heart_disease_model.pkl', 'rb') as f:
                model = pickle.load(f)

            # Load the feature names
            with open('model/feature_names.pkl', 'rb') as f:
                features = pickle.load(f)
            data = {
                'bmi': request.POST.get('bmi'),
                'smoking': request.POST.get('smoking'),
                'alcohol_drinking': request.POST.get('alcohol_drinking'),
                'stroke': request.POST.get('stroke'),
                'physical_health': request.POST.get('physical_health'),
                'mental_health': request.POST.get('mental_health'),
                'diff_walking': request.POST.get('diff_walking'),
                'sex': request.POST.get('sex'),
                'age_category': request.POST.get('age_category'),
                'diabetic': request.POST.get('diabetic'),
                'physical_activity': request.POST.get('physical_activity'),
                'gen_health': request.POST.get('gen_health'),
                'sleep_time': request.POST.get('sleep_time'),
                'asthma': request.POST.get('asthma'),
                'kidney_disease': request.POST.get('kidney_disease'),
                'skin_cancer': request.POST.get('skin_cancer'),
            }
            # data = [
            #    request.POST.get('bmi'),
            #    request.POST.get('smoking'),
            #    request.POST.get('alcohol_drinking'),
            #    request.POST.get('stroke'),
            #    request.POST.get('physical_health'),
            #    request.POST.get('mental_health'),
            #    request.POST.get('diff_walking'),
            #    request.POST.get('sex'),
            #    request.POST.get('age_category'),
            #    request.POST.get('diabetic'),
            #    request.POST.get('physical_activity'),
            #    request.POST.get('gen_health'),
            #    request.POST.get('sleep_time'),
            #    request.POST.get('asthma'),
            #    request.POST.get('kidney_disease'),
            #    request.POST.get('skin_cancer'),
            # ]

            pprint(request.user)
            data = list(data.values())
            data = list(map(float, data))

            # Print the features received from the form
            print("Features received from form:", data)

            # Check if the number of features match
            if len(data) != len(features):
                return {'message': f'Expected {len(features)} features, but got {len(data)}'}

            data = np.array(data).reshape(1, -1)

            prediction = model.predict_proba(data)
            risk_percentage = prediction[0][1] * 100
            context = {
                'risk_percentage': round(risk_percentage, 2)
            }

            record = PredictHistory.objects.create(
                user=request.user,
                value=f"{round(risk_percentage, 2)}"
            )

            return JsonResponse(context)
        except Exception as e:
            return render(request, 'fit_app/error.html', {'message': str(e)})
    return render(request, 'fit_app/heartpredict.html')


@login_required
def tracking(request):
    print(request.user)
    try:
        data = {}
        dataSourceDict = {
            'com.google.active_minutes': 'Activity minutes',
            'com.google.blood_pressure': 'Blood Pressure',
            'com.google.calories.bmr': 'Calories BMR',
            'com.google.distance.delta': 'Passed Distance',
            'com.google.heart_rate.bpm': 'Average Heart rate',
            'com.google.height': 'Average Height',
            'com.google.speed': 'Average Speed',
            'com.google.weight': 'Average Weigth',
        }
        sources = DataSource.objects.all()
        for entry in sources:
            key = dataSourceDict[entry.data_type]
            queryset = DataPoint \
                .objects \
                .filter(user=request.user) \
                .filter(data_source_id=entry.id) \
                .annotate(date_only=TruncDate('end_time')) \
                .values('date_only') \
                .annotate(
                total_value=Sum('value') if ['com.google.active_minutes', 'com.google.distance.delta'] else Avg(
                    'value')) \
                .order_by('-date_only')
            if key not in data:
                data[key] = []
            for item in queryset:
                value = round(item['total_value'], 2)
                data[key].append({'date': f"{item['date_only']}",
                                  'value': f"{value} {get_suffix(entry.data_type)}",
                                  'state': "good" if get_state(entry.data_type, value) else "bad"
                                  })
        predict_items = PredictHistory.objects.filter(user=request.user).order_by("-created_at").all()
        context = {
            'fit_items': data or [],
            'predict_items': predict_items or []
        }
        return render(request, 'fit_app/tracking.html', context=context)
    except Exception as e:
        return render(request, 'fit_app/error.html', {'message': str(e)})


def index(request):
    return render(request, 'fit_app/index.html')
