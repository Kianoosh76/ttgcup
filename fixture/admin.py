import django
from django.contrib import admin
from django.contrib.admin.options import StackedInline, TabularInline
from polymorphic.admin.childadmin import PolymorphicChildModelAdmin
from polymorphic.admin.parentadmin import PolymorphicParentModelAdmin

from fixture.models import Group, Player, Fixture, GroupFixture, FixturePlayer


class FixtureAdmin(PolymorphicParentModelAdmin):
    base_model = Fixture
    child_models = (GroupFixture, )


class FixtureChildAdmin(PolymorphicChildModelAdmin):
    base_model = Fixture


class FixturePlayerInline(TabularInline):
    model = FixturePlayer
    fields = ('player', 'score', 'place',)
    extra = 0


class GroupFixtureAdmin(FixtureChildAdmin):
    base_model = GroupFixture
    show_in_index = True

    inlines = [FixturePlayerInline]


admin.site.unregister(django.contrib.auth.models.Group)
admin.site.register(Group)
admin.site.register(Player)

admin.site.register(Fixture, FixtureAdmin)
admin.site.register(GroupFixture, GroupFixtureAdmin)