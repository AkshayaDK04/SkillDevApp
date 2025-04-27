from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import random
from collections import defaultdict
from sklearn.cluster import KMeans
from .models import CodingQuestion, Leaderboard, LearningJourney, Topic, UserScore, Quiz, UserQuiz, CustomUser
from .forms import RegisterForm, LoginForm
import random
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decouple import config
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .tokens import account_activation_token

User = get_user_model()

def send_verification_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()


CustomUser = get_user_model()
# Home view
def home(request):
    return render(request, 'home.html')
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm  # Assuming this is your custom register form
from .models import CustomUser  # Assuming your custom user model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect, render


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Deactivate until email is confirmed
            user.save()
            send_verification_email(request, user)  # Send email verification
            messages.success(request, "Registration successful! Please check your email to activate your account.")
            return redirect('login')  # Redirect to login page
        else:
            return render(request, 'register.html', {'form': form})
    
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm  # Assuming this is your login form
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect('home')
                else:
                    messages.error(request, "Your account is not active. Please check your email for verification.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid username or password")
                return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'login.html', {'form': form})

    form = LoginForm()
    return render(request, 'login.html', {'form': form})


# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid!')



@login_required
def select_learning_journey(request):
    journeys = LearningJourney.objects.all()
    return render(request, 'card.html', {'journeys': journeys})


from django.db.models import Sum

@login_required
def final_quiz_unlock(request):
    total_score = Leaderboard.objects.filter(user=request.user).aggregate(total=Sum('score'))['total'] or 0

    is_unlocked = total_score >= 100

    context = {
        'total_score': total_score,
        'is_unlocked': is_unlocked,
    }
    return render(request, 'final_quiz_unlock.html', context)






import google.generativeai as genai
import os


genai.configure(api_key=config('API_KEY'))

model = genai.GenerativeModel('gemini-1.5-flash-latest')

def get_ai_explanation(question, correct_option, selected_option):
    prompt = f"Question: {question}\nCorrect Answer: {correct_option}\nSelected Answer: {selected_option}\nExplain why the selected answer is wrong and why the correct answer is right:"
    
    response = model.generate_content(prompt)

    explanation = response.text
    return explanation

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans

# Load BERT model
bert_model = SentenceTransformer('all-MiniLM-L6-v2')
@login_required
@csrf_exempt
def take_quiz(request, topic_id, level):
    if request.method == 'POST':
        body = json.loads(request.body)
        question_id = body.get('question_id')
        selected_option = body.get('selected_option')

        try:
            question = Quiz.objects.get(id=question_id)
        except Quiz.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)

        is_correct = (selected_option == question.correct_option)
        explanation = ""

        leaderboard_entry, created = Leaderboard.objects.get_or_create(user=request.user, topic=question.topic)

        if not is_correct:
            explanation = get_ai_explanation(question.question, question.correct_option, selected_option)
            leaderboard_entry.wrong_answers += 1
        else:
            leaderboard_entry.score += 1
            leaderboard_entry.correct_answers += 1
        leaderboard_entry.save()

        return JsonResponse({
            'is_correct': is_correct,
            'explanation': explanation
        })

    # Step 1: Fetch user performance
    leaderboard_entry, _ = Leaderboard.objects.get_or_create(user=request.user, topic_id=topic_id)
    user_score = leaderboard_entry.score
    user_accuracy = leaderboard_entry.correct_answers / max(1, (leaderboard_entry.correct_answers + leaderboard_entry.wrong_answers))

    # Step 2: Get all questions for the topic and difficulty
    questions = list(Quiz.objects.filter(topic_id=topic_id, difficulty=level))
    
    # ✅ Check if no questions available
    if not questions:
        return render(request, 'quiz_completed.html')

    from collections import defaultdict
    import random

    # Step 3: Generate BERT embeddings
    question_texts = [q.question for q in questions]
    embeddings = bert_model.encode(question_texts)

    # Step 4: Apply K-Means clustering to select diverse questions
    num_clusters = min(len(questions), 10)
    kmeans = KMeans(n_clusters=num_clusters, n_init=10)
    kmeans.fit(embeddings)
    cluster_labels = kmeans.labels_

    # Step 5: Group questions by clusters
    cluster_to_questions = defaultdict(list)
    for idx, q in enumerate(questions):
        cluster_to_questions[cluster_labels[idx]].append(q)

    # Step 6: Randomly select one question per cluster
    selected_questions = []
    for cluster_questions in cluster_to_questions.values():
        selected_questions.append(random.choice(cluster_questions))

    # Step 7: Shuffle the selected questions to randomize their order
    random.shuffle(selected_questions)

    # Step 8: If more than 10, randomly select 10 from the shuffled list
    if len(selected_questions) > 10:
        selected_questions = random.sample(selected_questions, 10)

    # Prepare questions for rendering
    questions_list = [{
        'id': q.id,
        'question': q.question,
        'answers': [q.option1, q.option2, q.option3, q.option4],
        'correct': q.correct_option,
        'explanation': q.explanation
    } for q in selected_questions]

    context = {
        'questions': json.dumps(questions_list),
        'topic_id': topic_id,
        'level': level
    }
    return render(request, 'quiz2.html', context)


@login_required
def take_final_quiz(request):
    total_score = Leaderboard.objects.filter(user=request.user).aggregate(total=Sum('score'))['total'] or 0

    if total_score < 100:
        return redirect('final_quiz_unlock')

    if request.method == 'POST':
        body = json.loads(request.body)
        question_id = body.get('question_id')
        selected_option = body.get('selected_option')

        try:
            question = Quiz.objects.get(id=question_id)
        except Quiz.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)

        is_correct = (selected_option == question.correct_option)
        
        return JsonResponse({
            'is_correct': is_correct,
            'explanation': question.explanation if not is_correct else ""
        })

    all_topics = Topic.objects.all()

    learning_path = request.user.profile.learning_path

    difficulty_map = {
        'Basic': 'Easy',
        'Intermediate': 'Medium',
        'Advanced': 'Hard'
    }
    selected_difficulty = difficulty_map.get(learning_path, 'Easy')

    selected_questions = []

    for topic in all_topics:
        questions = list(Quiz.objects.filter(topic=topic, difficulty=selected_difficulty))
        if questions:
            selected_question = random.choice(questions)
            selected_questions.append(selected_question)

    if not selected_questions:
        return render(request, 'quiz_completed.html')  # ✅ Redirect if no questions available

    if len(selected_questions) > 20:
        selected_questions = random.sample(selected_questions, 20)

    question_texts = [q.question for q in selected_questions]
    embeddings = bert_model.encode(question_texts)

    num_clusters = min(len(selected_questions), 20)
    kmeans = KMeans(n_clusters=num_clusters, n_init=10)
    kmeans.fit(embeddings)
    cluster_labels = kmeans.labels_

    from collections import defaultdict
    cluster_to_questions = defaultdict(list)
    for idx, q in enumerate(selected_questions):
        cluster_to_questions[cluster_labels[idx]].append(q)

    final_questions = []
    for cluster_questions in cluster_to_questions.values():
        final_questions.append(random.choice(cluster_questions))

    random.shuffle(final_questions)

    questions_list = [{
        'id': q.id,
        'question': q.question,
        'answers': [q.option1, q.option2, q.option3, q.option4],
    } for q in final_questions]

    context = {
        'questions': json.dumps(questions_list),
    }
    return render(request, 'final_quiz.html', context)







@login_required

def topic_list(request,journey_name):
    topics = Topic.objects.all()
    journey=journey_name
    if(journey == 'basic'):
        level='easy'
    elif(journey=='medium'):
        level='moderate'
    elif(journey=='advanced'):
        level='difficult'
    return render(request, 'level.html', {'topics': topics,'level':level})




def card(request):
    return render(request,'card.html')

def level(request):
    return render(request,'level.html')

def quiz2(request):
    return render(request,'quiz2.html')

def lead(request):
    return render(request,'lead.html')


def leaderboard_view(request, topic_id=None):
    if topic_id:
        # Fetch leaderboard for the specific topic
        topic = Topic.objects.get(id=topic_id)
        leaderboard = Leaderboard.objects.filter(topic=topic).order_by('-score')
        context = {
            'leaderboard': leaderboard,
            'topic': topic
        }
    else:
        # Fetch overall leaderboard
        leaderboard = Leaderboard.objects.all().order_by('-score')
        context = {
            'leaderboard': leaderboard,
            'topic': None
        }

    return render(request, 'lead.html', context)