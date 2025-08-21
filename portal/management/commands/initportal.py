from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group,Permission
from entity.models import Years,Levels,Subjects

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Init portal and add teachers and students groups'

    def handle(self, *args, **options):
        try:
            tg = Group.objects.create(name="teachers")
            sg = Group.objects.create(name="students")
        except:
            self.stderr.write('DB OPS failed\n')
            return

        p1=Permission.objects.get(codename="add_user")
        p2=Permission.objects.get(codename="change_user")
        p3=Permission.objects.get(codename="delete_user")
        p4=Permission.objects.get(codename="add_session")
        p5=Permission.objects.get(codename="change_session")
        p6=Permission.objects.get(codename="delete_session")

        tg.permissions.add(p1)
        tg.permissions.add(p2)
        tg.permissions.add(p3)
        tg.permissions.add(p4)
        tg.permissions.add(p5)
        tg.permissions.add(p6)

        sg.permissions.add(p4)
        sg.permissions.add(p5)
        sg.permissions.add(p6)

        y1 = Years.objects.create(yearname = 'P1')
        y2 = Years.objects.create(yearname = 'P2')
        y3 = Years.objects.create(yearname = 'P3')
        y4 = Years.objects.create(yearname = 'P4')
        y5 = Years.objects.create(yearname = 'P5')
        y6 = Years.objects.create(yearname = 'P6')
        y7 = Years.objects.create(yearname = 'Sec 1')
        y8 = Years.objects.create(yearname = 'Sec 2')
        y9 = Years.objects.create(yearname = 'Sec 3')
        y10 = Years.objects.create(yearname = 'Sec 4')
        y11 = Years.objects.create(yearname = 'JC 1')
        y12 = Years.objects.create(yearname = 'JC 2')

        l1 = Levels.objects.create(levelname = 'HL')
        l2 = Levels.objects.create(levelname = 'SL')
        s1 = Subjects.objects.create(subjectname = 'Physics')
        s2 = Subjects.objects.create(subjectname = 'Pyscology')
        s3 = Subjects.objects.create(subjectname = 'EE')
        self.stdout.write('Successfully init\n')
