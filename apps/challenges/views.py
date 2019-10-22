import time
from ratelimit.mixins import RatelimitMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView, View)

from apps.challenges.forms import (AttachmentAddForm, AttachmentDeleteForm,
                                   FlagAddForm, FlagDeleteForm, HintAddForm,
                                   HintDeleteForm, NewChallengeForm,
                                   SubmitFlagForm)
from apps.challenges.models import (Attachment, BadSubmission, Category,
                                    Challenge, FirstBlood, Flag, Solves,
                                    Hint)
from apps.scoreboard.utils import get_key
from django.core.exceptions import PermissionDenied


class UserIsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class CtfNotEnded(UserPassesTestMixin):
    def test_func(self):
        if get_key('start_time') is None or get_key('end_time') is None:
            return True
        elif int(get_key('start_time')) < int(time.time()) < int(get_key('end_time')):
            return True
        else:
            return False


class ChallengesListView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        solves = Solves.objects.prefetch_related(
            'challenge').prefetch_related('account')

        context['challenges'] = Challenge.objects.prefetch_related(
            'category').prefetch_related('solves').all()
        context['categories'] = Category.objects.prefetch_related('challenge_set').all()
        context['solved_by_user'] = solves.prefetch_related('challenge').values_list(
            'challenge', flat=True).filter(account=self.request.user.pk)
        #context['solves'] = solves.values("challenge__name").annotate(
            #c=Count('challenge')).order_by('-c')
        context['solves'] = solves.values("challenge__name").annotate(
            c=Count('challenge')).order_by('-c')
        context['first_bloods'] = FirstBlood.objects.prefetch_related(
            'account').prefetch_related('challenge')
        return render(self.request, 'templates/challenge/list_challenges.html', context=context)


class SubmitFlagView(RatelimitMixin, CtfNotEnded, LoginRequiredMixin, FormView):
    ratelimit_key = 'user'
    ratelimit_rate = '5/m'
    ratelimit_method = 'POST'
    ratelimit_block = True
    form_class = SubmitFlagForm

    def get_context_data(self, **kwargs):
        context = super(SubmitFlagView, self).get_context_data(**kwargs)
        chall_obj = Challenge.objects.get(pk=self.kwargs['pk'])
        if chall_obj.visible == False:
            raise PermissionDenied()
        else:
            context['challenge'] = chall_obj
            context['solvers'] = Solves.objects.filter(
                challenge=context['challenge'])
            context['solved_by_user'] = Solves.objects.filter(
                account=self.request.user.pk).values_list('challenge', flat=True)
            return context

    def get_template_names(self):
        return list(['templates/challenge/challenge.html'])

    def form_valid(self, form):
        challenge_id = form.cleaned_data['challenge_id']
        flag = form.cleaned_data['flag']
        challenge = Challenge.objects.get(pk=challenge_id)

        if Solves.objects.filter(challenge=challenge, account=self.request.user).count() == 0:
            if flag in challenge.flag_set.all().values_list('text', flat=True):
                if Solves.objects.filter(challenge=challenge).count() == 0:
                    FirstBlood.objects.create(
                        challenge=challenge,
                        account=self.request.user,
                    )

                Solves.objects.create(
                    challenge=challenge,
                    account=self.request.user,
                )

                return render(self.request, 'templates/challenge/flag_success.html', {'challenge': challenge})
            else:
                new_bad_submission = BadSubmission.objects.create(
                    challenge=challenge,
                    account=self.request.user,
                    flag=flag
                )
                return render(self.request, 'templates/challenge/challenge.html', {'challenge': challenge, 'solvers': Solves.objects.filter(challenge=challenge), 'error': 'Bandera errada :('})
        else:
            return render(self.request, 'templates/challenge/challenge.html', {'challenge': challenge, 'solvers': Solves.objects.filter(challenge=challenge), 'error': 'Ya esta hecho!'})


class CreateChallengeView(SuccessMessageMixin, LoginRequiredMixin, UserIsAdminMixin, FormView):
    form_class = NewChallengeForm
    template_name = 'templates/challenge/new_challenge.html'
    success_url = reverse_lazy('administration:challenges')
    success_message = "Challenge %(name)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super(CreateChallengeView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        category = form.cleaned_data['category']

        new_challenge = Challenge(
            category=category,
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            points=form.cleaned_data['points'],
            visible=True
        )

        new_challenge.save()
        new_flag = Flag(
            challenge=new_challenge,
            text=form.cleaned_data['flag']
        )

        if self.request.FILES:
            files = self.request.FILES.getlist('attachments')
            if files:
                for f in files:
                    Attachment.objects.create(
                        challenge=new_challenge,
                        data=f
                    )

        new_flag.save()
        return super(CreateChallengeView, self).form_valid(form)


class UpdateChallengeView(UserIsAdminMixin, UpdateView):
    model = Challenge
    fields = '__all__'
    template_name = 'templates/challenge/update_challenge.html'
    success_url = reverse_lazy('administration:challenges')


class DeleteChallengeView(UserIsAdminMixin, DeleteView):
    model = Challenge
    template_name = 'templates/challenge/delete_challenge.html'
    success_url = reverse_lazy('administration:challenges')


class ToggleChallengeVisibility(UserIsAdminMixin, View):

    def post(self, request, *args, **kwargs):
        challenge_id = request.POST.get('challenge_id')
        if challenge_id is None:
            return HttpResponse(status=400)
        else:
            challenge = Challenge.objects.get(pk=challenge_id)
            if challenge.visible:
                challenge.visible = False
            else:
                challenge.visible = True
            challenge.save()
            return HttpResponse(status=204)


class AddCategoryView(UserIsAdminMixin, CreateView):
    model = Category
    fields = '__all__'
    template_name = 'templates/category/add_category.html'
    success_url = reverse_lazy('administration:challenges')


class UpdateCategoryView(UserIsAdminMixin, UpdateView):
    model = Category
    fields = '__all__'
    template_name = 'templates/category/update_category.html'
    success_url = reverse_lazy('administration:challenges')


class DeleteCategoryView(UserIsAdminMixin, DeleteView):
    model = Category
    template_name = 'templates/category/delete_category.html'
    success_url = reverse_lazy('administration:challenges')


class FlagsView(UserIsAdminMixin, DetailView):
    model = Challenge
    template_name = 'templates/challenge/flags.html'


class FlagAddView(UserIsAdminMixin, View):
    form_class = FlagAddForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            challenge_id = form.cleaned_data['challenge_id']
            flag = form.cleaned_data['flag']
            challenge = Challenge.objects.get(pk=challenge_id)

            Flag.objects.create(
                challenge=challenge,
                text=flag
            )

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)


class FlagDeleteView(UserIsAdminMixin, View):
    form_class = FlagDeleteForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            flag = form.cleaned_data['flag']
            flag = Flag.objects.get(
                pk=flag
            )
            flag.delete()

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)


class HintsView(UserIsAdminMixin, DetailView):
    model = Challenge
    template_name = 'templates/challenge/hints.html'


class HintAddView(UserIsAdminMixin, View):
    form_class = HintAddForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            challenge_id = form.cleaned_data['challenge_id']
            hint = form.cleaned_data['hint']
            challenge = Challenge.objects.get(pk=challenge_id)

            Hint.objects.create(
                challenge=challenge,
                text=hint
            )

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)


class HintDeleteView(UserIsAdminMixin, View):
    form_class = HintDeleteForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            hint = form.cleaned_data['hint']
            hint = Hint.objects.get(
                pk=hint
            )
            hint.delete()

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)


class AttachmentsView(UserIsAdminMixin, DetailView):
    model = Challenge
    template_name = 'templates/challenge/attachments.html'


class AttachmentAddView(UserIsAdminMixin, View):
    form_class = AttachmentAddForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            challenge_id = form.cleaned_data['challenge_id']
            attachment = form.cleaned_data['data']
            challenge = Challenge.objects.get(pk=challenge_id)

            Attachment.objects.create(
                challenge=challenge,
                data=attachment
            )

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)


class AttachmentDeleteView(UserIsAdminMixin, View):
    form_class = AttachmentDeleteForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            attachment = form.cleaned_data['attachment']
            attachment = Attachment.objects.get(
                pk=attachment
            )
            attachment.delete()

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)
