from django.conf.urls import url

from fixture.views import GroupFixturesView

urlpatterns = [
    url(r'^group/(?P<group_id>\d+)/$', GroupFixturesView.as_view(), name='fixtures'),
]
