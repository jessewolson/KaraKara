from pyramid.view import view_config

import re

from . import web, method_put_router, is_admin, etag_decorator, generate_cache_key
from ..lib.auto_format import action_ok, action_error
from ..lib.misc import convert_str_with_type

import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------------

def generate_cache_key_homepage(request):
    """
    Custom etag for homepage
    The homepage template has a few if statements to display various buttons
    The buttons can be disables in settings.
    This custom etag takes all 'if' statements in the homepage template    
    """
    return '-'.join((
        generate_cache_key(request),
        str(request.registry.settings.get('karakara.template.menu.disable')),
        str(bool(request.session.get('faves',[]))),
    ))

@view_config(route_name='home')
@etag_decorator(generate_cache_key_homepage)
@web
def home(request):
    return action_ok()

@view_config(route_name='admin_lock')
@web
def admin_lock(request):
    if is_admin(request):
        request.registry.settings['admin_locked'] = not request.registry.settings.get('admin_locked',False)
    return action_ok()

@view_config(route_name='admin_toggle')
@web
def admin_toggle(request):
    if request.registry.settings.get('admin_locked'):
        raise action_error(message='additional admin users have been prohibited', code=403)
    request.session['admin'] = not request.session.get('admin',False)
    return action_ok()

@view_config(route_name='remote')
@web
def remote(request):
    cmd = request.params.get('cmd')
    if is_admin(request) and cmd:
        log.debug("sending {0}".format(cmd))
        request.registry['socket_manager'].recv(cmd.encode('utf-8'))
    return action_ok()

@view_config(route_name='settings')
@web
def settings(request):
    """
    Surface settings as an API.
    This allows clients to qurey server settup rather than having to hard code bits into the clients
    """
    
    if method_put_router(None, request):
        # with PUT requests, update settings
        #  only changing in production is bit over zelious #request.registry.settings.get('karakara.server.mode')!='production'
        if request.registry.settings.get('karakara.server.mode')!='test' and not is_admin(request):
            raise action_error(message='Settings modification for non admin users forbidden', code=403)
        
        for key, value in request.params.items():
            fallback_type = None
            if request.registry.settings.get(key):
                fallback_type = type(request.registry.settings.get(key))
            request.registry.settings[key] = convert_str_with_type(value, fallback_type=fallback_type)
    
    setting_regex = re.compile(request.registry.settings.get('api.settings.regex','TODOmatch_nothing_regex'))
    return action_ok(
        data={
            'settings': {
                setting_key:request.registry.settings.get(setting_key)
                for setting_key in
                [key for key in request.registry.settings.keys() if setting_regex.match(key)]
            }
        }
    )

@view_config(route_name='random_images')
@web
def random_images(request):
    """
    The player interface titlescreen can be populated with random thumbnails from the system.
    This is a nice showcase.
    Not optimised as this is rarely called.
    """
    import random
    from karakara.model              import DBSession
    from karakara.model.model_tracks import Attachment
    thumbnails = DBSession.query(Attachment.location).filter(Attachment.type=='thumbnail').all()
    random.shuffle(thumbnails)
    thumbnails = [t[0] for t in thumbnails]
    return action_ok(data={'thumbnails':thumbnails[0:int(request.params.get('count',0) or 100)]})
