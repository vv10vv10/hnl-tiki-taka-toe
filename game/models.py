from django.db import models

# Create your models here.
class Drzava(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Klub(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Igrac(models.Model):
    name = models.CharField(max_length=100)
    clubs = models.ManyToManyField(Klub)
    country = models.ForeignKey(Drzava,on_delete=models.CASCADE)

    def __str__(self):
        return self.name