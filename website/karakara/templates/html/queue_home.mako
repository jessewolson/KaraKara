<%inherit file="_base.mako"/>

<%doc>
  Developer Note:
    If you add any 'if' statements to this template, ensure you update the etag generator for the homepage
</%doc>

## Easter Egg for users who look at the code
<!--
    YOU WIN!
    --------
    Welcome iquisitive hax0r!
    Those who look at code deserve a treat.

    Navigate to '${paths['settings']}' to look under the hood at the current settings.
    If you want to look futher then checkout the github repo
        http://github.com/calaldees/karakara/
    Send us a message, get involved, submit a feature request or contribute a new bugfix/feature yourself.

    Hint:
        If you buy the people running the event some snacks, sweets or drinks
        they may bypass the queue and slip a track in for you and a friend.
-->

## TODO - 'request.registry.settings' is depricated for queue level settings
<% disbaled_message = request.queue.settings.get('karakara.template.menu.disable') %>
% if not identity.get('admin', False) and disbaled_message:
    <p>${disbaled_message}</p>
% else:
    <a href="${paths['search_tags']}" data-role="button">${_('mobile.home.search_tags')}</a>
    <a href="${paths['queue_items']}" data-role="button">${_('mobile.home.queue')}</a>

    ##% if identity.get('faves',[]):
    ##<a href="${path_queue}/fave"           data-role="button">${_('mobile.home.fave')}</a>
    ##% endif

    ## Disbaled until we can reimplement it as 'messaging'
    ##<a href="${path_queue}/feedback"       data-role="button">${_('mobile.home.feedback')}</a>
% endif

% if identity.get('admin', False):
    ## TODO: Move these links to comunity
    <a href="${paths['player']}"           data-role="button" class="admin">${_('mobile.home.player')}</a>
    <a href="${paths['track_list']}"       data-role="button" class="admin">${_('mobile.home.track_list')}</a>
    <a href="${paths['settings']}"         data-role="button" class="admin">${_('mobile.home.settings')}</a>
    <a href="${paths['remote_control']}"   data-role="button" class="admin">${_('mobile.home.remote')}</a>
    <a href="${paths['priority_tokens']}"  data-role="button" class="admin">${_('mobile.home.priority_tokens')}</a>
    <a href="/static/form_badgenames.html" data-role="button" class="admin">${_('mobile.home.badgenames')}</a>
    ##<a href="/inject_testdata"    data-role="button" class="admin">${_('mobile.home.inject_testdata')}</a>
    ##<a href="/comunity"           data-role="button" class="admin">${_('mobile.home.comunity')}</a>
% endif