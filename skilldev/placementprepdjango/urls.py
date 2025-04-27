from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('',views.home, name='home'),
    path('accounts/login/', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('final-quiz/unlock/', views.final_quiz_unlock, name='final_quiz_unlock'),
    path('final-quiz/', views.take_final_quiz, name='final_quiz'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('topics/<str:journey_name>/', views.topic_list, name='topic_list'),
    path('quiz/<int:topic_id>/<str:level>', views.take_quiz, name='take_quiz'),
    path('code_editor/<int:question_id>/', views.code_editor, name='code_editor'),
    path('run_code/', views.run_code, name='run_code'),
    path('code_qns/',views.code_qns,name='code_qns'),
    path('card/',views.select_learning_journey,name='card'),
    path('level/',views.level,name='level'),
    path('quiz2/',views.quiz2,name='quiz2'),
    path('lead/',views.lead,name='lead'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('leaderboard/<int:topic_id>/', views.leaderboard_view, name='topic_leaderboard'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)