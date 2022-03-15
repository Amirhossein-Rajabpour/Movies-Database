from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractBaseUser):

    ROLE_CHOICES = (
        (0, "user"),
        (1, "admin"),
    )
    username = models.CharField(max_length=20)
    USERNAME_FIELD = 'username'
    role = models.IntegerField(choices=ROLE_CHOICES)
    # password is handled in AbstractBaseUser
    

class Movie(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    rating = models.FloatField(null=True, validators=[
                    MinValueValidator(0.0),
                    MaxValueValidator(1.0),])

    @property
    def comments(self):
        return Comment.objects.filter(pk=self.id)

    def __str__(self) -> str:
        return "name: " + self.name + " --  description: " + self.description + " -- rate: " + str(self.rating) + "\n"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000)
    approved = models.BooleanField(null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username + ": " + self.comment


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
