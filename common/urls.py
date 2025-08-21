from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('intemass.common.views',
    url(r'^deletecallback/$', TemplateView.as_view(template_name="callback.json"),
        name='deleteview_callback'),
    url(r'^imagecapture', 'imagecapture', name='imagecapture'),
)
