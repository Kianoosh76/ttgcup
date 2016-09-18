from django.db import models
from django.db.models.signals import post_migrate
from polymorphic.models import PolymorphicModel

from fixture.config import group_fixtures, group_num


class Group(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)


class Player(models.Model):
    group = models.ForeignKey(to=Group, related_name='players')
    index = models.IntegerField()
    name = models.CharField(max_length=30)
    score = models.IntegerField(default=0)
    goals_scored = models.IntegerField(default=0)
    goals_conceded = models.IntegerField(default=0)
    goal_diff = models.IntegerField(default=0)
    goal_ratio = models.FloatField(default=0)

    def save(self, **kwargs):
        self.goal_diff = self.goals_scored - self.goals_conceded
        print(self.goal_diff)
        try:
            self.goal_ratio = self.goals_scored / self.goals_conceded
        except ZeroDivisionError:
            self.goal_ratio = 0

        super().save(**kwargs)

        g = GroupFixtureIndex.objects.filter(group_fixture__group=self.group, index=self.index)
        for fixture_index in g:
            FixturePlayer.objects.get_or_create(fixture=fixture_index.group_fixture, player=self,
                                                place=fixture_index.place)

    @property
    def games_played(self):
        return FixturePlayer.objects.filter(player=self, score__isnull=False).count()

    def __str__(self):
        return self.name


class Fixture(PolymorphicModel):
    def set_score(self):
        p1 = self.player1
        p2 = self.player2
        p1.player.goals_scored += p1.score
        p1.player.goals_conceded += p2.score

        p2.player.goals_scored += p2.score
        p2.player.goals_conceded += p1.score

        if p1.score < p2.score:
            p1, p2 = p2, p1

        if p2.score <= 15:
            p1.player.score += 3
        else:
            p1.player.score += 2
            p2.player.score += 1

        p1.player.save()
        p2.player.save()

    @property
    def player1(self):
        return self.players.get(place=True)

    @property
    def player2(self):
        return self.players.get(place=False)


class GroupFixture(Fixture):
    group = models.ForeignKey(to=Group, related_name='fixtures')
    matchday = models.IntegerField()

    def __str__(self):
        return 'group {} matchday {} :{} {}'.format(str(self.group), self.matchday,
                                                    self.indexes.first().index,
                                                    self.indexes.last().index)


class GroupFixtureIndex(models.Model):
    group_fixture = models.ForeignKey(to=GroupFixture, related_name='indexes')
    index = models.IntegerField()
    place = models.BooleanField()


class FixturePlayer(models.Model):
    fixture = models.ForeignKey(to=Fixture, related_name='players')
    player = models.ForeignKey(to=Player, related_name='fixture_parts')
    score = models.IntegerField(null=True, blank=True)
    place = models.BooleanField()


def add_groups_and_fixtures(sender, **kwargs):
    print("called")
    for i in range(group_num):
        Group.objects.get_or_create(number=str(i + 1))

    for group in Group.objects.all():
        for matchday, fixture_set in enumerate(group_fixtures):
            if GroupFixture.objects.filter(matchday=matchday + 1, group=group).count() == len(
                    fixture_set):
                continue
            for fixture in fixture_set:
                g = GroupFixture.objects.create(matchday=matchday + 1, group=group)
                GroupFixtureIndex.objects.create(group_fixture=g, index=fixture[0],
                                                 place=True)
                GroupFixtureIndex.objects.create(group_fixture=g, index=fixture[1],
                                                 place=False)


post_migrate.connect(add_groups_and_fixtures, sender=None)
