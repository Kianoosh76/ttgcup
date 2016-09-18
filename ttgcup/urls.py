from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^fixtures/', include('fixture.urls', namespace='fixture')),
    url(r'^admin/', include(admin.site.urls)),
]
