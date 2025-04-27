from django.contrib.auth.models import AbstractUser, Group, Permission,BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with email and password
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # You can add a default username if required, or omit it
        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractUser):
    username = None  # Disable username
    email = models.EmailField(_('email address'), unique=True)  # Use email for login

    USERNAME_FIELD = 'email'  # Make email the primary login field
    REQUIRED_FIELDS = []  # Don't ask for other fields when creating superuser


    objects = CustomUserManager()

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.email




class LearningJourney(models.Model):
    JOURNEY_CHOICES = [
        ('basic', 'Basic'),
        ('medium', 'Medium'),
        ('advanced', 'Advanced'),
    ]
    name = models.CharField(max_length=10, choices=JOURNEY_CHOICES)

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    prompt = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='topic_images/',null=True,blank=True)  # Field for the topic image
   

    def __str__(self):
        return self.name
    
class Leaderboard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.topic.name} - Score: {self.score}"


class Quiz(models.Model):
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('difficult', 'Difficult'),
    ]
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='quizzes')
    difficulty=models.CharField(max_length=200)
    question = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=200)
    explanation = models.TextField(null=True,blank=True)  # Field for explanation of correct/incorrect answers
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS,default="easy")

    def __str__(self):
        return self.question

    def get_explanation(self, selected_option):
        # Returns an explanation based on the selected option
        if selected_option == self.correct_option:
            return f"Correct! {self.explanation}"
        else:
            return f"Incorrect. {self.explanation}"


class UserQuiz(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Use CustomUser instead of User
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)  # Explanation feedback

    def save(self, *args, **kwargs):
        # Override save to generate feedback automatically
        self.is_correct = self.selected_option == self.quiz.correct_option
        self.feedback = self.quiz.get_explanation(self.selected_option)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.question} - {self.selected_option}"


class UserScore(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Use CustomUser here as well
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.quiz.topic.name} - {self.score}"
    


class CodingQuestion(models.Model):
    question_text = models.TextField()
    test_cases = models.JSONField()  # Storing test cases as JSON
    language = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('C', 'C'),
        ('Java', 'Java'),
        ('Python', 'Python'),
        ('C++', 'C++')
    ])
    
    def __str__(self):
        return self.question_text

