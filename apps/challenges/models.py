import os
from django.db import models
from apps.accounts.models import Account
import math


class Category(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self):
        return self.name


class Challenge(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, null=False, blank=False)
    author = models.CharField(max_length=64, null=True, blank=True)
    description = models.TextField(null=False, blank=False)
    points = models.IntegerField()
    visible = models.BooleanField(default=True)

    @property
    def sorted_by_solves_set(self):
        return self.solves.order_by('points')


class Hint(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)


class Flag(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)


class Attachment(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    data = models.FileField(upload_to='media/attachments/', max_length=500)

    def filename(self):
        return os.path.basename(self.data.name)


class Solves(models.Model):
    challenge = models.ForeignKey(Challenge, related_name='solves', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, related_name='solves', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None):
        self.account.points += self.challenge.points
        # Dynamic Score
        # based on https://github.com/CTFd/CTFd/tree/master/CTFd/plugins/dynamic_challenges/README.md
        min_val = 10
        max_solv = 50
        print('Logging of dynamic score')
        print(self.challenge.id)
        solved = self.challenge.solves.count()
        ini_pts = 1000
        past_pts = int(math.ceil((((min_val - ini_pts) / (max_solv ** 2)) * ((solved-1) ** 2)) + ini_pts))
        value = int(math.ceil((((min_val - ini_pts) / (max_solv ** 2)) * (solved ** 2)) + ini_pts))
        if value < min_val:
            value = min_val
        # end of based formula

        #FirstBlood bonus
        if solved <= 10:
            self.account.points = self.account.points + 10 - solved
        self.account.save()
        super().save()

        # Check if an score update is needed
        if value > min_val or past_pts > min_val :
            lchallenge = Challenge.objects.get(pk=self.challenge.id)
            # Save the next score, the future value
            fut_value = int(math.ceil((((min_val - ini_pts) / (max_solv ** 2)) * ((solved+1) ** 2)) + ini_pts))
            if fut_value < min_val:
                fut_value = min_val
            lchallenge.points = fut_value
            lchallenge.save()
            # Update all the accounts points!
            for i in range(1, Account.objects.count()):
                solves = Solves.objects.prefetch_related('challenge').prefetch_related('challenge__category').filter(account=i)
                next((x for x in solves if x.challenge.id == self.challenge.id), None)
                for solve in solves:
                    if solve.challenge.id == self.challenge.id:
                        laccount = Account.objects.get(pk=i)
                        laccount.points = laccount.points - past_pts + value
                        laccount.save()


    def delete(self, *args, **kwargs):
        if self.account.points > self.challenge.points:
            self.account.points -= self.challenge.points
        else:
            self.account.points = 0
        self.account.save()
        super().delete(*args, **kwargs)


class FirstBlood(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class BadSubmission(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    flag = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
