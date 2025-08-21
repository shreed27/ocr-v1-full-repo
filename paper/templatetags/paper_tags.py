import pickle
from bs4 import BeautifulSoup
from django import template
from question.views import NUM_CLOSENESS_BANDS
from portal.common import latex_to_img
from canvas.models import Canvas
from question.models import QuestionImage
from portal.common import latex_to_img
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

register = template.Library()


def actual_mark(stu_obj):
    value = stu_obj.question.markscheme
    marks = value.split(",")
    marks = [mark.strip() for mark in marks]
    total_mark = 0
    for i, m in enumerate(marks):
        if "P0." in m:
            if m.count("P0.") == 1 or "ONLY" in m.upper():
                total_mark += (int(marks[i + 1]) * m.count("P0."))
        elif "all" in m:
            total_mark += int(marks[i + 1])
    try:
        canvas_mark = []
        canvas = Canvas.objects.get(question=stu_obj.question, stdanswer=stu_obj.question.stdanswer)
        if canvas.markscheme:
            canvas_mark = pickle.loads(canvas.markscheme)
    except Exception as exp:
        print 'ObjectDoesNotExist = ', exp
        return total_mark
    else:
        for cm in canvas_mark:
            if "all" in cm[0]:
                total_mark +=int(cm[1])
        return total_mark
register.filter('actual_mark',actual_mark)


def format_printout(omitted):
    omitted_items = pickle.loads(str(omitted))
    formatted_answer = ""
    for item in omitted_items:
        if item.startswith("W"):
            formatted_answer = "%s<br><u>%s</u>" % (formatted_answer, item[1:])
        elif item.startswith("C"):
            formatted_answer = "%s<br>%s" % (formatted_answer, item[1:])
        else:
            formatted_answer = "%s<br>%s" % (formatted_answer, item)
    return formatted_answer
register.filter('format_printout', format_printout)

def total_text_mark(value):
    marks = [mark.strip() for mark in value.split(",")]
    return int(marks[marks.index("all") + 1])

def point_text(omitted, value, flag=False):
    omitted_items = pickle.loads(str(omitted))
    max_mark = total_text_mark(value)
    single_point_mark = float(max_mark) / len(omitted_items) if max_mark else 0
    _html = '<table class = "std_table" style="padding:-22px"><tbody>'
    formatted_answer = ""
    for item in omitted_items:
        _html += "<tr>"
        if flag:
            item = template_image(item)
        text = item[1:]
        if item.startswith("W"):
            _html += "<td><span style='color:red;font-weight:bold;'>{}</span></td>".format(text)
        else:
            _html += "<td><span style='color:green;font-weight:bold;'>{}</span></td>".format(text)
        # _html += "<td class='point_mark'>{:.1f}</td></tr>".format(single_point_mark)
    _html += "</tbody></table>"
    return _html
register.filter('point_text', point_text)

def point_text_download(omitted, value):
    return point_text(omitted, value, True)
register.filter('point_text_download', point_text_download)

def closeness(value):
    # Not in use as per requirment
    # closeness_band = 1 + int(value * NUM_CLOSENESS_BANDS)
    # closeness_band = max(1, min(value, NUM_CLOSENESS_BANDS))
    close = round(value * 100, 1)
    return close
register.filter('closeness', closeness)

def image_attr(text, omitted=False):
    width = 150
    height = 50
    if omitted:
        return latex_to_img(text)
    return latex_to_img(text, width, height)
register.filter("img_add_attr", image_attr)

# Supporting function
def template_image(text):
    width = 150
    height = 50
    bs_obj = BeautifulSoup(text)
    for img_tag in bs_obj.find_all("img"):
        img_tag["width"] = width
        img_tag["height"] = height
    return str(bs_obj.body).strip("<body>")[:-2]

def has_canvas(stu_obj, std_obj=0):
    try:
        if std_obj:
            canvas = Canvas.objects.get(question=stu_obj.question, stdanswer=std_obj)
        else:
            canvas = Canvas.objects.get(question=stu_obj.question, stuanswer=stu_obj)
    except ObjectDoesNotExist:
        return False
    else:
        return canvas
register.filter("has_canvas", has_canvas)


def thumbnails(stu_obj, flag=False):
    try:
        # flag is True for sttudent's image
        question = stu_obj.question
        if flag:  # Called for student image
            _thumbnails = QuestionImage.objects.filter(question=question,
                                                       iscorrect=True).exclude(description="del")
            thumbnails_list = [["{}/thumb__{}".format(settings.THUMBNAILPREFIX, t.abspath),
                                    t.imagename,
                                    "{}/{}".format(settings.UPLOADPREFIX, t.abspath),
                                    t.id]
                               for t in _thumbnails]
            _html = render_image_html(thumbnails_list)
        else:
            #[0] thumb,[1] imagename,[2] orig image
            stuthumbnails = stu_obj.stuansimages.all()
            studigests = list(st.digest for st in stuthumbnails)
            stuthumbnails_list= [["{}/thumb__{}".format(settings.THUMBNAILPREFIX, t.abspath),
                                  t.imagename,
                                  "{}/{}".format(settings.UPLOADPREFIX, t.abspath),
                                  t.id]
                                 for t in stuthumbnails]
            _html = render_image_html(stuthumbnails_list)
        return _html
    except Exception as e:
        import traceback
        traceback.print_exc()
register.filter("thumbnails", thumbnails)

def render_image_html(thumb_list):
    thumbhtml = '';
    for thumb in thumb_list:
        thumbhtml += '<li class="ui-widget-content ui-corner-tr">'
        thumbhtml += '<h6 class="ui-widget-header">' + thumb[1][0:5] + '...' + '</h6>'
        thumbhtml += '<a href="/static/' + thumb[2] + '" title="View Larger Image" id = "file_id">'
        try:
            file_name = thumb[1].split(".")
            if file_name[1] in ("pdf", "xls", "xlsx", "docx", "doc", "txt", "odt", "ods"):
                thumbhtml += '<img src="/static/server_img/files.png" id=' + str(thumb[3]) +' alt="' + thumb[1] + '" width="50" height="50"></img></a>'
            else:
                raise IndexError
        except IndexError:
            thumbhtml += '<img src="/static/' + thumb[0] + '" id=' + str(thumb[3]) +' alt="' + thumb[1] + '" width="50" height="50"></img></a>'
        thumbhtml += '</li>'
    return thumbhtml


@register.filter(name='format_stdanswer')
def format_stdanswer(stdanswer):
    """
    removes the '[ENDPOINT]' and latex codes in the
    standard formatted_answer
    """
    return latex_to_img(stdanswer.replace("[ENDPOINT]", "<br>"))
