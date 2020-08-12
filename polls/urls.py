from django.urls import path

from django.conf.urls import include

from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/delete', views.deleteView, name='delete_question'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('<int:question_id>/re-vote/', views.re_vote, name='re-vote'),
    path('add_poll/', views.addQuestionView, name='add_poll'),
    path('authors/', views.AuthorsView.as_view(), name='authors'),
    path('authors/<int:pk>/', views.DetailAuthorView.as_view(), name='author_detail'),
    path('authors/settings', views.authorSettingsView, name='author_settings'),
    path('<int:question_id>/comment', views.addCommentView, name='add_comment')
]
