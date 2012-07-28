<%inherit file="_base.mako"/>

<%!
    import string
%>

<%def name="title()">Search Tracks</%def>

<%def name="search_url(tags=None,keywords=None,route='search_tags')"><%
        if tags    ==None: tags     = data.get('tags'    ,[])
        if keywords==None: keywords = data.get('keywords',[])
        route_path = h.search_url(tags,keywords,route)
%>${route_path}</%def>


% for tag in data['tags']:
    <%
        tags_modifyed = list(data['tags'])
        tags_modifyed.remove(tag)
    %>
    <a href="${search_url(tags=tags_modifyed)}" data-role="button" data-icon="delete">${tag}</a>
% endfor
% for keyword in data['keywords']:
    <%
        keywords_modifyed = list(data['keywords'])
        keywords_modifyed.remove(keyword)
    %>
    <a href="${search_url(keywords=keywords_modifyed)}" data-role="button" data-icon="delete">${keyword}</a>
% endfor

<!-- add keywords -->
<form action="${search_url()}" method="GET">
    <input type="text" name="keywords" placeholder="Add search keywords">
</form>

<a href="${search_url(route='search_list')}" data-role="button" data-icon="arrow-r">List ${len(data.get('trackids',[]))} Tracks</a>

<!-- sub tags -->
% for parent_tag in data.get('sub_tags_allowed',[]):
<h2>${parent_tag}</h2>
    <%
        tags = [tag for tag in data.get('sub_tags',[]) if tag.get('parent')==parent_tag]  # AllanC - humm .. inefficent filtering in a template .. could be improved
        
        try   : renderer = jquerymobile_accordian if tags[-1]['parent'] in ['from','artist'] and len(tags)>40 else jquerymobile_list
        except: renderer =                                                                                         jquerymobile_list
    %>
    ${renderer(tags)}
% endfor

<%def name="tag_li(tag)">
        <li><a href="${search_url(data['tags'] + [tag['full']])}">${tag['name']} <span class="ui-li-count">${tag['count']}</span></a></li>
</%def>

<%def name="jquerymobile_list(tags)">
    <ul data-role="listview" data-inset="true">
    % for tag in tags:
        ${tag_li(tag)}
    % endfor
    </ul>
</%def>

<%def name="jquerymobile_accordian(tags)">
    <%
        grouped_tags = {}
        for tag in tags:
            i = tag['name'][0]
            if i not in grouped_tags:
                grouped_tags[i] = []
            grouped_tags[i].append(tag)
    %>
    <div data-role="collapsible-set">
    % for letter in string.ascii_lowercase:
        <div data-role="collapsible" data-collapsed="True">
            <h3>${letter.upper()} (${len(grouped_tags.get(letter,[]))})</h3>
            <ul data-role="listview">
                % for tag in grouped_tags.get(letter,[]):
                ${tag_li(tag)}
                % endfor
            </ul>
        </div>
    % endfor
    </div>
</%def>
