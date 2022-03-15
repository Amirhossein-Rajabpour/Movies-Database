from django.urls import path
from movies.views import *


urlpatterns = [
    path('admin/movie/', AddMovie.as_view()),
    path('admin/movie/<int:id>/', EditMovie.as_view()),
    path('admin/comment/<int:id>/', EditComment.as_view()),

    path('user/vote/', AddVote.as_view()),
    path('user/comment/', AddComment.as_view()),

    path('movies/', MovieList.as_view()),
    path('movie/<int:id>/', GetMovie.as_view()),
    path('comments/', CommentsOfMovie.as_view()),
]
