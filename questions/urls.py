from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('vote/<str:kind>/<int:item_id>/', views.vote, name='vote'),
    path('question/<int:question_id>/correct/', views.correct, name='correct'),
    path('ask/', views.ask, name='ask'),
]
