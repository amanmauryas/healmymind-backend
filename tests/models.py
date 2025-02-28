from django.db import models
from users.models import User

class Test(models.Model):
    TEST_TYPES = [
        ('PHQ9', 'Depression Screening (PHQ-9)'),
        ('GAD7', 'Anxiety Screening (GAD-7)'),
        ('PCL5', 'PTSD Screening (PCL-5)'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    test_type = models.CharField(max_length=10, choices=TEST_TYPES)
    instructions = models.TextField()
    estimated_time = models.IntegerField(help_text="Estimated time in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.test.name} - Question {self.order}"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    value = models.IntegerField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.question.text} - Option {self.order}"

class TestResult(models.Model):
    SEVERITY_LEVELS = [
        ('MINIMAL', 'Minimal'),
        ('MILD', 'Mild'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    answers = models.JSONField()  # Store detailed answers
    recommendations = models.JSONField(null=True, blank=True)  # AI-generated recommendations
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.email} - {self.test.name} - {self.completed_at.date()}"

class ScoringRange(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='scoring_ranges')
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    severity = models.CharField(max_length=10, choices=TestResult.SEVERITY_LEVELS)
    description = models.TextField()

    def __str__(self):
        return f"{self.test.name} - {self.severity} ({self.min_score}-{self.max_score})"
