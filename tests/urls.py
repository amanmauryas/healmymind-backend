from django.urls import path
from . import views

urlpatterns = [
    # Test management
    path('', views.TestListView.as_view(), name='test-list'),
    path('<str:test_id>/', views.TestDetailView.as_view(), name='test-detail'),
    path('<str:test_id>/questions/', views.TestQuestionsView.as_view(), name='test-questions'),
    
    # Test taking and results
    path('<str:test_id>/start/', views.StartTestView.as_view(), name='start-test'),
    path('<str:test_id>/submit/', views.SubmitTestView.as_view(), name='submit-test'),
    path('results/<str:result_id>/', views.TestResultView.as_view(), name='test-result'),
    path('results/', views.UserTestResultsView.as_view(), name='user-test-results'),
    
    # AI Analysis
    path('results/<str:result_id>/analysis/', views.TestAnalysisView.as_view(), name='test-analysis'),
    path('suggest/', views.TestSuggestionView.as_view(), name='test-suggestion'),
    
    # Admin endpoints
    path('admin/create/', views.CreateTestView.as_view(), name='create-test'),
    path('admin/<str:test_id>/update/', views.UpdateTestView.as_view(), name='update-test'),
    path('admin/<str:test_id>/delete/', views.DeleteTestView.as_view(), name='delete-test'),
    path('admin/statistics/', views.TestStatisticsView.as_view(), name='test-statistics'),
]
