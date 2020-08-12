from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseForbidden
from django.views import generic
from django.utils import timezone

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _

from .models import Choice, Question, Author
from .forms import QuestionForm, SignUpForm, AuthorForm, CommentForm
from .funcs import voted_choice, birth_day_context, get_comments_tree


class AuthorsView(generic.ListView):
    template_name = 'polls/authors.html'
    context_object_name = 'authors_list'

    def get_queryset(self):
        return Author.objects.order_by('first_name', 'last_name')[:5]


class DetailAuthorView(generic.DetailView):
    model = Author
    template_name = 'polls/author_detail.html'


@login_required
def authorSettingsView(request):
    author = request.user.author
    if request.method == 'POST':
        form = AuthorForm(data=request.POST)
        if form.is_valid():
            author.first_name = form.cleaned_data['first_name']
            author.last_name = form.cleaned_data['last_name']
            author.birth_date = form.cleaned_data['first_name']
            author.birth_date = form.cleaned_data['birth_date']
            author.save()
            return redirect('polls:author_detail', pk=author.id)
            
        context = {'form': form}
    else:
        data = {
            'first_name': author.first_name,
            'last_name': author.last_name,
        }
        if author.birth_date:
            data = {**data, **birth_day_context(author)}

        context = {'form': AuthorForm(data=data)}
    return render(request, 'polls/author_settings.html', context=context)


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(
                          pub_date__lte=timezone.now()
                      ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous:
            context['voted_choice'] = voted_choice(kwargs['object'].choice_set.all(), self.request.user.author)
        context['comments'] = get_comments_tree(kwargs['object'].comment_set.all())
        context['comment_form'] = CommentForm()
        return context


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voted_choice'] = voted_choice(kwargs['object'].choice_set.all(), self.request.user.author)
        return context


@login_required
def addQuestionView(request):
    if request.method == 'POST':
        choices = []
        form = QuestionForm(data=request.POST)
        for key in request.POST:
            if key.startswith('choice_text'):
                choices.append(request.POST[key])
        if form.is_valid():
            attrs = {
                'question_text': form.cleaned_data['question_text'],
                'pub_date': timezone.now(),
                'author': request.user.author,
            }
            question = Question.objects.create(**attrs)
            for choice in choices:
                attrs = {
                    'question': question,
                    'choice_text': choice,
                }
                Choice.objects.create(**attrs)
            return redirect('polls:index')

        context = {'question_form': form, 'choices': choices}
    else:
        context = {'question_form': QuestionForm(), 'count': 0}
    return render(request, 'polls/add_poll.html', context=context)


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
            'voted_choice': voted_choice(question.choice_set.all(), request.user.author),
        })
    else:
        selected_choice.votes.add(request.user.author)
        selected_choice.save()
        return redirect('polls:results', pk=question.id)


@login_required
def re_vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    voted = voted_choice(question.choice_set.all(), request.user.author)
    voted.votes.remove(request.user.author)
    voted.save()
    return redirect('polls:detail', pk=question.id)


def deleteView(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.author.user:
        if request.method == 'POST':
            Question.objects.get(pk=question_id).delete()
            return redirect('polls:index')
        else:
            return render(request, 'polls/delete_question.html', context={'question': question})
    else:
        return HttpResponseForbidden()


@login_required
def addCommentView(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = CommentForm(data=request.POST)
    if form.is_valid():
        kwargs = {
            'comment_text': form.cleaned_data['comment_text'],
            'pub_date': timezone.now(),
        }
        if form.cleaned_data['rel_comment']:
            kwargs['rel_comment'] = form.cleaned_data['rel_comment']
        else:
            kwargs['question'] = question
        question.comment_set.create(**kwargs)
    return render(request, 'polls/detail.html', {
        'question': question,
        'voted_choice': voted_choice(question.choice_set.all(), request.user.author),
        'comments': get_comments_tree(question.comment_set.all()),
        'comment_form': form,
    })


def signupView(request):
    if request.method == 'POST':
        form = SignUpForm(data=request.POST)
        print(form.errors)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            kwargs = {
                'username': username,
                'password': password,
                'email': email,
            }
            user_obj = User.objects.create(**kwargs)

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            day = form.cleaned_data['birth_day']
            month = form.cleaned_data['birth_month']
            year = form.cleaned_data['birth_year']
            kwargs = {
                'user': user_obj,
                'first_name': first_name,
                'last_name': last_name,
            }
            if day and month and year:
                kwargs['birth_date'] = timezone.datetime(year, month, day)
            Author.objects.create(**kwargs)

            login(request, user_obj)
            return redirect('polls:index')
        return render(request, 'registration/signup.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})