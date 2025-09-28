from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portal.models import TProfile, SProfile
from classroom.models import Classroom
from assignment.models import Assignment
from itempool.models import Itempool
from paper.models import Paper
from question.models import Question, StandardAnswer
from student.models import StudentAnswer
from django.utils.html import strip_tags
import random
import pickle
import os
from algo.standard import Standard
from entity.models import Years, Levels, Subjects
from datetime import timedelta, datetime


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'add some test data'

    def handle(self, *args, **options):
        weiyan = User.objects.create_user("demo", "yan, wei_sjtu@yahoo.cn", "demo")
        stu = []
        try:
            stu.append(User.objects.create_user("li", "stu@a.com", "1"))
            stu.append(User.objects.create_user("qu", "stu@b.com", "1"))
            stu.append(User.objects.create_user("hu", "stu@c.com", "1"))
            stu.append(User.objects.create_user("lu", "stu@d.com", "1"))
            stu.append(User.objects.create_user("yun", "stu@e.com", "1"))
            stu.append(User.objects.create_user("wang", "stu@f.com", "1"))
            stu.append(User.objects.create_user("he", "stu@g.com", "1"))
            stu.append(User.objects.create_user("lin", "stu@h.com", "1"))
            stu.append(User.objects.create_user("wade", "stu@i.com", "1"))
            stu.append(User.objects.create_user("tim", "stu@j.com", "1"))
            weiyantp = TProfile.objects.create(user=weiyan,
                                               gender='male', cellphone="13671670930")
        except:
            pass

        stusp = []
        for i in range(10):
            stusp.append(SProfile.objects.create(user=stu[i],
                                                 gender=random.choice(["female", "male"]),
                                                 cellphone="125453"))

        clazz = []
        for i in range(10):
            clazz.append(Classroom.objects.create(roomname="c%d" % (i + 1), volume='20'))
            weiyantp.classrooms.add(clazz[i])
            weiyantp.save()
            stusp[i].classroom = clazz[i]
            stusp[i].teacher = weiyantp
            stusp[i].save()

        itempool = []
        for i in range(10):
            itempool.append(Itempool.objects.create(poolname="i%d" % (i + 1),
                                                    teacher=weiyantp,
                                                    description="hello"))

        assignment = []
        for i in range(10):
            assignment.append(Assignment.objects.create(assignmentname="a%d" % (i + 1),
                                                        teacher=weiyantp,
                                                        description="hello"))
            assignment[i].students = stusp
            assignment[i].deadline = datetime.now() + timedelta(seconds=18000)
            assignment[i].save()

        year = Years.objects.all()
        level = Levels.objects.all()
        subject = Subjects.objects.all()

        standardanswer = []
        question = []
        testStandardAnswerFile = "Q1_html.txt"
        filePath = os.path.join("algo/testdata/raw/Q1", testStandardAnswerFile)
        if not os.path.isfile(filePath):
            assert False
        fh = open(filePath, "r")
        filetext = fh.read()
        fh.close()
        sinst = Standard()
        markscheme = "only P0.3 and P0.4,2,only P0.3 or P0.4,1,all,8,all less 2 combinations of 1.1;1.2;3.0,7,all less 1.1 or 1.2 or 2.0,7,all less 1.1 and 1.2 and 2.0,6,all less 3.0,5,all less 1.1 and 1.2 and 2.0 and 3.0,4,all less 4.0 or 5.0 or 6.0,3,all less 2 combinations of 4.0;5.0;6.0,2,all less 4.0 and 5.0 and 6.0,1"
        rulelist = [{'Mark': 10, 'Point': ['P1.1', 'P1.2', 'P2', 'P3', 'P4', 'P5', 'P6']},
                    {'Mark': 9, 'Point': ['P2', 'P1.1', 'P6', 'P4', 'P5']},
                    {'Mark': 9, 'Point': ['P2', 'P1.2', 'P6', 'P4', 'P5']},
                    {'Mark': 9, 'Point': ['P2', 'P3', 'P6', 'P4', 'P5']},
                    {'Mark': 9, 'Point': ['P2', 'P3', 'P6', 'P4', 'P5', 'P1.2']},
                    {'Mark': 9, 'Point': ['P2', 'P3', 'P6', 'P4', 'P5', 'P1.1']},
                    {'Mark': 9, 'Point': ['P3', 'P6', 'P4', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 8, 'Point': ['P3', 'P6', 'P4', 'P5']},
                    {'Mark': 7, 'Point': ['P2', 'P6', 'P4', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 6, 'Point': ['P6', 'P4', 'P5']},
                    {'Mark': 5, 'Point': ['P2', 'P3', 'P6', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 5, 'Point': ['P2', 'P3', 'P6', 'P4', 'P1.2', 'P1.1']},
                    {'Mark': 5, 'Point': ['P2', 'P3', 'P4', 'P5', 'P1.2', 'P1.1']},
                    {'Mark': 4, 'Point': ['P2', 'P3', 'P1.1', 'P4', 'P1.2']},
                    {'Mark': 4, 'Point': ['P2', 'P3', 'P1.1', 'P1.2', 'P5']},
                    {'Mark': 4, 'Point': ['P2', 'P3', 'P1.1', 'P6', 'P1.2']},
                    {'Mark': 3, 'Point': ['P2', 'P3', 'P1.1', 'P1.2']},
                    {'Mark': 2, 'Point': ['P3', 'P1.2']},
                    {'Mark': 2, 'Point': ['P3', 'P1.1']},
                    {'Mark': 2, 'Point': ['P1.2', 'P1.1']},
                    {'Mark': 1, 'Point': ['P1.1']},
                    {'Mark': 1, 'Point': ['P1.2']},
                    {'Mark': 1, 'Point': ['P2']},
                    {'Mark': 1, 'Point': ['P3']}]
        try:
            stdanswerstring = strip_tags(filetext.replace('< /br>', '\n'))
            stdanswerstring = strip_tags(filetext.replace('&nbsp', ' '))
            pointlist, textfdist, slist = sinst.Analysis(stdanswerstring)
            #pointlist, textfdist, slist = sinst.Analysis(stdanswerstring)
            textfdist_dumpped = pickle.dumps(textfdist)
            sentencelist_dumpped = pickle.dumps(slist)
            pointlist_dumpped = pickle.dumps(pointlist)
            rulelist_dumpped = pickle.dumps(rulelist)
        except Exception as e:
            print(e)
            textfdist_dumpped = None
            sentencelist_dumpped = None
            sentencelist_dumpped = None
        for i in range(500):
            standardanswer.append(StandardAnswer.objects.create(name='std%d' % (i + 1),
                                                                fullmark=10,
                                                                textfdist=textfdist_dumpped,
                                                                sentencelist=sentencelist_dumpped,
                                                                pointlist=pointlist_dumpped,
                                                                rulelist=rulelist_dumpped
                                                                ))
            question.append(Question.objects.create(qname="q%d" % (i + 1),
                                                    category="test",
                                                    description="test_q%d" % (i + 1),
                                                    qtype=random.choice(["Formal", "Review"]),
                                                    itempool=random.choice(itempool),
                                                    qtext=stdanswerstring,
                                                    qhtml=filetext,
                                                    markscheme=markscheme,
                                                    teacher=weiyantp
                                                    ))

            try:
                question[i].stdanswer = standardanswer[i]
                question[i].infocompleted = 7
                question[i].stdanswertext = stdanswerstring
                question[i].stdanswerhtml = filetext
            except:
                pass
            question[i].save()

        paper = []
        for i in range(25):
            paper.append(Paper.objects.create(papername="p%d" % (i + 1),
                                              owner=weiyan,
                                              ptype="Formal",
                                              duration="02:00",
                                              passpoint=40,
                                              year=random.choice(year),
                                              subject=random.choice(subject),
                                              level=random.choice(level),
                                              assignment=random.choice(assignment)))
            paper[i].save()

        for i in range(25):
            paper.append(Paper.objects.create(papername="p%d" % (i + 25),
                                              owner=random.choice(stu),
                                              ptype="Review",
                                              duration="02:00",
                                              passpoint=40,
                                              year=random.choice(year),
                                              subject=random.choice(subject),
                                              level=random.choice(level)))
            paper[i + 25].save()

        for q in question:
            q.paper.add(random.choice(paper))
            q.save()

        for p in paper:
            qs = Question.objects.filter(paper=p, infocompleted=Question.ALLCOMPLETED)
            questionseq = ([q.id for q in qs])
            p.total = len(qs)
            p.questionseq = pickle.dumps(questionseq)
            p.save()

        filelist = []

        for i in range(32):
            filelist.append("algo/testdata/raw/Q1/Q1_SS%d.docx" % (i + 1))

        studentanswer = []
        for i in range(500):
            mark = random.randint(0, 10)
            pointmarklist = ['1.2', '2', '4', '5', '6']
            html_answer = filetext
            txt_answer = filetext
            omittedcontent = ['1.1 . In the context of the essay, scarcity would be defined as limited resources which needs to be managed, because of men&rsquo;s unlimited wants , Choice is an inevitable consequence of scarcity&nbsp; which is the need to answer the four question&nbsp; of&nbsp; what to produce&nbsp; , how and how much to produce&nbsp; and&nbsp; for whom .',
                              '1.2 . The definition of opportunity cost would be defined as the cost arising from using limited resources to satisfy unlimited wants in terms of the next best alternative foregone . It is a consequence of choice.',
                              '6 . Opportunity cost&nbsp; can be identified on the PPC by its gradient , as one moves to the production of more consumer goods as seen in the diagram. The gradient from point &ldquo;A to B is not as steep as the gradient from B to C . It can be seen in the diagram that by producing more of consumer goods, the opportunity cost would be the forgoing of capital goods. This concave shaped of the PPC , relative to the origin,&nbsp;\
                              demonstrates the law of increasing opportunity cost, whereby to produce an equal amounts of another good, society must sacrifice an ever increasing amount of the other good. A real life example would be the production of the consumer good whereby the opportunity cost would be forgoing the production of capital goods.']
            omitted = pickle.dumps(omittedcontent)
            studentanswer.append(StudentAnswer.objects.create(student=stusp[1],
                                                              mark=int(mark),
                                                              pointmarklist=str(pointmarklist).strip('[]'),
                                                              question=question[i],
                                                              html_answer=html_answer,
                                                              txt_answer=txt_answer,
                                                              omitted=omitted,
                                                              taked=False
                                                              ))
        self.stdout.write('Add test data successfully\n')
