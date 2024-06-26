from django.db import models
from accounts.models import User, Language
from interests.models import Question


class MatchRequest(models.Model):
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATE_CHOICES = [
        (REQUESTED, 'Requested'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    requester = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)


class Match(models.Model):
    requester = models.ForeignKey(User, related_name='requested_matches', on_delete=models.CASCADE)
    acceptor = models.ForeignKey(User, related_name='accepted_matches', on_delete=models.CASCADE)
    state = models.BooleanField(default=True)
    native_lang = models.ForeignKey(Language, related_name='native_matches', on_delete=models.CASCADE)
    learning_lang = models.ForeignKey(Language, related_name='learning_matches', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    withdraw_reason = models.TextField(null=True, blank=True)
    provided_questions = models.ManyToManyField(Question, related_name='match_questions', blank=True)
    current_question = models.ForeignKey(Question, related_name='current_match', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Match between {self.requester.nickname} and {self.acceptor.nickname}"

    def end_match(self, reason):
        self.state = False
        self.withdraw_reason = reason
        self.save()
