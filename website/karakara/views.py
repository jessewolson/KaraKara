from pyramid.view import view_config
from pyramid.response import Response

from karakara.lib.auto_format import auto_format_output

#from .models import (
#    DBSession,
#    MyModel,
#    )

#@view_config(route_name='home', renderer='templates/mytemplate.pt')
#def my_view(request):
#    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
#    return {'one':one, 'project':'KaraKara'}
##, renderer='karakara:templates/home.mako'

@view_config(route_name='home')
@auto_format_output
def home(request):
    return {}

@view_config(route_name='helloworld')
@auto_format_output
def helloworld(request):
    return {'status':'ok','message':'Hello World'}