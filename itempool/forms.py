from django import forms
from itempool.models import Itempool

class ItemPoolDetailForm(forms.Form):
    def __init__(self,*args,**kwargs):
        teacher = kwargs.pop('teacher')
        super(ItemPoolDetailForm,self).__init__(*args,**kwargs)
        if teacher:
            itempools = Itempool.objects.filter(accessible = teacher)
            ips = [(-1,"New Item Pool")] + [(ip.id,ip.poolname) for ip in itempools]
            self.fields['itempoolid'] = forms.ChoiceField(choices=ips,label="Item Pool ID")

    itempoolid = forms.ChoiceField(label="Item Pool ID")
    itempoolname = forms.CharField(label = "Item Pool Name",max_length = 30)
    description = forms.CharField(widget = forms.Textarea(attrs={'cols': 22, 'rows': 3}),
                                  label = 'Description', required = False)

