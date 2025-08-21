from django.conf.urls import patterns, url
from canvas.views import CanvasView


urlpatterns = patterns('intemass.canvas.views',
                       url(r'^$', CanvasView.as_view(), name='canvas'),
                       url(r'upload/$', 'canvas_upload', name='canvas_upload'),
                       url(r'get/$', 'canvas_get', name='canvas_get'),
                       )
