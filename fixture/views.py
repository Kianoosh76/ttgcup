from django.http.response import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from fixture.models import GroupFixture, Player


class GroupFixturesView(TemplateView):
    model = GroupFixture
    template_name = 'fixture/fixtures.html'

    def dispatch(self, request, *args, **kwargs):
        self.group = int(self.kwargs['group_id'])
        if request.method == 'POST' and not request.user.is_superuser:
            return HttpResponseForbidden("You cannot change score")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fixtures = self.get_queryset()
        context['fixture_set'] = [fixtures.filter(matchday=m) for m in range(1, 4)]

        players = Player.objects.filter(group__number=self.group)
        context['standings'] = players.order_by('-score', '-goal_diff', '-goal_ratio')
        return context

    def get_queryset(self):
        queryset = GroupFixture.objects.filter(group__number=self.group)
        return queryset

    def post(self, request, *args, **kwargs):
        for fixture in self.get_queryset():
            post1 = 'score-' + str(fixture.id) + '-1'
            post2 = 'score-' + str(fixture.id) + '-2'
            post1 = request.POST.get(post1)
            post2 = request.POST.get(post2)
            if post1 and post2:
                player1 = fixture.player1
                player2 = fixture.player2

                player1.score = int(post1)
                player2.score = int(post2)

                player1.save()
                player2.save()
                fixture.set_score()
        return redirect('fixture:fixtures', self.kwargs['group_id'])