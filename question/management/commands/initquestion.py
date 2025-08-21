from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group,Permission
from django.conf import  settings
import os

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Init question folders for upload'

    def handle(self, *args, **options):
        upload_dir = settings.UPLOADFOLDER
        thumbnail_dir = settings.THUMBNAILFOLDER
        generated_img_dir = settings.GENERATED_IMG
        if not os.path.isdir(upload_dir):
            os.makedirs(upload_dir)
        else:
            self.stdout.write("folder exists, ignore!\n")
        if not os.path.isdir(thumbnail_dir):
            os.makedirs(thumbnail_dir)
        else:
            self.stdout.write("folder exists, ignore!\n")
        if not os.path.isdir(generated_img_dir):
            os.makedirs(generated_img_dir)
        else:
            self.stdout.write("folder exists, ignore!\n")


        self.stdout.write('Successfully init\n')
