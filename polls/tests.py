import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
            was_published_recently() returns False for questions whose pub_date is in
            the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
            was_published_recently() returns False for questions whose pub_date
            is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_que = Question(pub_date=time)
        self.assertIs(old_que.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
            was_published_recently() returns True for questions whose pub_date
            is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_que = Question(pub_date=time)
        self.assertIs(recent_que.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
            If no question exists, an appropriate msg is displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
            Questions with pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question],)

    def test_future_question(self):
        """
            Questions with a pub_date in the future aren't displayed on the index page
        """
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
            Even if both past and future questions exist, only past questions are displayed
        """
        question = create_question(question_text='Past question.', days=-30)
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question],)

    def test_two_past_question(self):
        """
            The questions index page may display multiple questions.
        """
        question1 = create_question(question_text='Past question 1.', days=-30)
        question2 = create_question(question_text='Past question 2.', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question2, question1],)


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
            Detail view of a question with a future pub_date returns 404 not found
        """
        future_que = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_que.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
            Detail view of a question with a past pub_date displays the question text
        """
        past_que = create_question(question_text='Past question.', days=-5)
        url = reverse('polls:detail', args=(past_que.id,))
        response = self.client.get(url)
        self.assertContains(response, past_que.question_text)

