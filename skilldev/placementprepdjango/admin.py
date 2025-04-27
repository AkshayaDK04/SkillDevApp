from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import LearningJourney, Topic, Quiz, UserQuiz, UserScore,CustomUser,CodingQuestion,Leaderboard  # Import your models


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    ordering = ['email']
    search_fields = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )

# Register the Topic model
@admin.register(CodingQuestion)
class CodingQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'test_cases')  # Fields to display in the admin list view
    search_fields = ('question_text',)  # Fields to search in the admin


@admin.register(Leaderboard)
class LeaderBoardAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic','score')  # Fields to display in the admin list view
    search_fields = ('user','score')


@admin.register(LearningJourney)
class LearningJourneyAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Fields to display in the admin list view
    search_fields = ('name',)  # Fields to search in the admin


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Fields to display in the admin list view
    search_fields = ('name',) 


# Register the Quiz model
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('question', 'topic', 'correct_option')  # Fields to display
    list_filter = ('topic',)  # Filter by topic
    search_fields = ('question',)  # Search by question

# Register the UserQuiz model
@admin.register(UserQuiz)
class UserQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'selected_option', 'is_correct', 'timestamp')  # Displayed fields
    list_filter = ('user', 'quiz', 'is_correct')  # Filters
    search_fields = ('user__username', 'quiz__question')  # Search by user and quiz

# Register the UserScore model
@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score')  # Displayed fields
    list_filter = ('user', 'quiz')  # Filters
    search_fields = ('user__username', 'quiz__question')  # Search by user and quiz

