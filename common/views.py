from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import base64
import os


@csrf_exempt
def imagecapture(request):
    save = request.POST['save']
    name = request.POST['name']
    img_type = request.POST['type']
    image = request.POST['image']
    print save
    print name
    print img_type
    if save:
        if name and (img_type is "JPG" or img_type is "PNG"):
            img = base64.b64decode(image)
            full_name = os.path.join(settings.GENERATED_IMG, name + "." + img_type)
            fw = open(full_name, 'w')
            fw.write(img)
            fw.close()
    #response['Content-Type'] = 'text/plain; charset=utf-8'
    #response['Cache-Control'] = 'no-cache'
    response = '/static/generated_img/' + name + "." + img_type
    #print response
    r = HttpResponse()
    r.write(response)
    return r
