from django.http import HttpResponse
from movies.models import *
from django.views import View
from django.shortcuts import get_object_or_404
import jwt
from movies_project.settings import JWT_SECRET_KEY
import json

def authenticate(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.exceptions.DecodeError:
        payload = {'username': ""}
        print('token error!')

    try:
        user = User.objects.get(username=payload['username'])
    except User.DoesNotExist:
        return None
    return user


def admin_access(view):
    def wrapper(*args, **kwargs):
        user = authenticate(args[1].headers.get('token'))
        if user is None or user.role == 0:  # normal user or guest
            print('user not admin')
            return HttpResponse(status=403, content='not Authorized')
        print("user is admin")
        return view(*args, **kwargs)
    return wrapper


def normal_user_access(view):
    def wrapper(*args, **kwargs):
        user = authenticate(args[1].headers.get('token'))
        if user is None:  # guest
            return HttpResponse(status=403, content='not Authorized')
        print("user is normal user")
        return view(*args, **kwargs)
    return wrapper


################# Admin #################

# insert a new movie
class AddMovie(View):
    @admin_access
    def post(self, request):
        try:
            body = json.loads(request.body.decode())
            name = body['name']
            description = body['description']
        except KeyError:
            return HttpResponse(status=400, content='Bad request')

        Movie.objects.create(name=name, description=description)
        return HttpResponse(status=204)


# edit a movie
class EditMovie(View):
    @admin_access
    def put(self, request, id):
        movie = get_object_or_404(Movie, id=id)
        try:
            body = json.loads(request.body.decode())
            new_name = body['name']
            new_description = body['description']
        except KeyError:
            return HttpResponse(status=400, content='Bad request')

        movie.name = new_name
        movie.description = new_description
        movie.save()
        return HttpResponse(status=204)

    @admin_access
    def delete(self, request, id):
        movie = get_object_or_404(Movie, id=id)
        movie.delete()
        return HttpResponse(status=204)


# edit or remove comments
class EditComment(View):
    @admin_access
    def put(self, request, id):
        body = json.loads(request.body.decode())
        approved = body['approved']
        comment = get_object_or_404(Comment, id=id)
        comment.approved = approved
        comment.save()
        return HttpResponse(status=204)

    @admin_access
    def delete(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        comment.delete()
        return HttpResponse(status=204)


################# Normal User #################

# add vote
class AddVote(View):
    @normal_user_access
    def post(self, request):
        try:
            body = json.loads(request.body.decode())
            movie_id = body['movie_id']
            vote = body['vote']
        except KeyError:
            return HttpResponse(status=400, content='Bad request')

        if not (0 < vote < 10):
            return HttpResponse(status=400, content='Bad request')

        movie = get_object_or_404(Movie, id=movie_id)
        movie.rating = (vote/10)
        movie.save()
        return HttpResponse(status=204)


# add comment
class AddComment(View):
    @normal_user_access
    def post(self, request):
        try:
            body = json.loads(request.body.decode())
            movie_id = body['movie_id']
            comment_body = body['comment_body']
        except KeyError:
            return HttpResponse(status=400, content='Bad request')

        movie = get_object_or_404(Movie, id=movie_id)
        user = authenticate(request.headers.get('token'))

        Comment.objects.create(movie_id=movie, user=user, comment=comment_body)
        return HttpResponse(status=204)


################# Guests #################

# see list of the movies
class MovieList(View):
    def get(self, request):
        movies = Movie.objects.all()
        return HttpResponse(movies)


# see info of a movie
class GetMovie(View):
    def get(self, request, id):
        movie = Movie.objects.get(id=id)
        return HttpResponse(movie)


# see comments of a movie
class CommentsOfMovie(View):
    def get(self, request):
        try:
            movie_id = int(request.GET['movie'])
            comments = get_object_or_404(Movie, id=movie_id).comments.filter(approved=True)

            comments_array = []
            for c in comments:
                comments_array.append(str(c))

            return HttpResponse("\n".join(comments_array))
        except KeyError: 
            return HttpResponse(content='Bad request.', status=400)