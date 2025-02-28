from rest_framework import serializers
from .models import Test, Question, Option, TestResult, ScoringRange

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text', 'value', 'order')

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'options')

class ScoringRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringRange
        fields = ('min_score', 'max_score', 'severity', 'description')

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    scoring_ranges = ScoringRangeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Test
        fields = (
            'id', 'name', 'description', 'test_type', 'instructions',
            'estimated_time', 'questions', 'scoring_ranges',
            'created_at', 'updated_at'
        )

class TestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""
    class Meta:
        model = Test
        fields = ('id', 'name', 'description', 'test_type', 'estimated_time')

class TestResultSerializer(serializers.ModelSerializer):
    test = TestListSerializer(read_only=True)
    
    class Meta:
        model = TestResult
        fields = (
            'id', 'user', 'test', 'score', 'severity',
            'answers', 'recommendations', 'completed_at'
        )
        read_only_fields = ('user', 'score', 'severity', 'recommendations')

class SubmitTestSerializer(serializers.ModelSerializer):
    answers = serializers.JSONField(required=True)
    
    class Meta:
        model = TestResult
        fields = ('answers',)

    def validate_answers(self, value):
        """
        Validate that all questions have been answered and the answers are valid.
        """
        test = self.context.get('test')
        if not test:
            raise serializers.ValidationError("Test not found")

        questions = test.questions.all()
        question_ids = set(str(q.id) for q in questions)
        answer_ids = set(str(k) for k in value.keys())

        if question_ids != answer_ids:
            raise serializers.ValidationError("All questions must be answered")

        return value

class TestAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ('id', 'score', 'severity', 'recommendations')
        read_only_fields = fields

class CreateTestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    scoring_ranges = ScoringRangeSerializer(many=True)
    
    class Meta:
        model = Test
        fields = (
            'name', 'description', 'test_type', 'instructions',
            'estimated_time', 'questions', 'scoring_ranges'
        )

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        scoring_ranges_data = validated_data.pop('scoring_ranges')
        
        test = Test.objects.create(**validated_data)
        
        for question_data in questions_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(test=test, **question_data)
            
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)
        
        for range_data in scoring_ranges_data:
            ScoringRange.objects.create(test=test, **range_data)
        
        return test

class TestStatisticsSerializer(serializers.Serializer):
    total_tests_taken = serializers.IntegerField()
    average_score = serializers.FloatField()
    severity_distribution = serializers.DictField()
    completion_rate = serializers.FloatField()
    average_completion_time = serializers.FloatField()
