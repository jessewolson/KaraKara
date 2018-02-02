"""
https://pypi.python.org/pypi/pyramid-notebook#id22

{

    # Extra Python script executed on notebook startup - this is saved as startup.py
    "startup": ""

    # Markdown text displayed at the beginning of the notebook
    "greeting": ""

    # List of paths where to load IPython Notebook Jinja templates
    # http://ipython.org/ipython-doc/3/config/options/notebook.html
    "extra_template_paths": []

    # The port where Notebook daemon is supposed to start listening to
    "http_port",

    # Notebook daemon process id - filled it in by the daemon itself
    "pid",

    # Notebook daemon kill timeout in seconds - filled in by the the daemon itself after parsing command line arguments
    "kill_timeout",

    # Bound localhost port for this notebook - filled in by the daemon itself after parsing command line arguments
    "http_port",

    # Set Notebook HTTP Allow Origin header to tell where websockets are allowed to connect
    "allow_origin"

    # Override websocket URL
    "websocket_url",

    # Path in URL where Notebook is proxyed, must match notebook_proxy() view
    "notebook_path",

    # Hash of this context. This is generated automatically from supplied context dictionary if not given. If the hash changes the notebook is restarted with new context data.
    "context_hash",
}

"""

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_notebook import startup
from pyramid_notebook.views import launch_notebook
from pyramid_notebook.views import shutdown_notebook as _shutdown_notebook
from pyramid_notebook.views import notebook_proxy as _notebook_proxy
from pyramid_web20.models import Base


#: Include our database session in notebook so it is easy to query stuff right away from the prompt
#from pyramid_web20.models import DBSession as session
SCRIPT = """

"""

#* **session** - SQLAlchemy database session
GREETING="""

"""


@view_config(route_name="notebook_proxy", permission="shell")
def notebook_proxy(request):
    """Proxy IPython Notebook requests to the upstream server."""
    return _notebook_proxy(request, request.user.username)


@view_config(route_name="admin_shell", permission="shell")
def admin_shell(request):
    """Open admin shell with default parameters for the user."""
    # Make sure we have a logged in user
    nb = {}

    # Pass around the Pyramid configuration we used to start this application
    global_config = request.registry.settings["pyramid_web20.global_config"]

    # Get the reference to our Pyramid app config file and generate Notebook
    # bootstrap startup.py script for this application
    config_file = global_config["__file__"]
    startup.make_startup(nb, config_file)
    startup.add_script(nb, SCRIPT)
    startup.add_greeting(nb, GREETING)

    #: Include all our SQLAlchemy models in the notebook variables
    startup.include_sqlalchemy_models(nb, Base)

    return launch_notebook(request, request.user.username, notebook_context=nb)


@view_config(route_name="shutdown_notebook", permission="shell")
def shutdown_notebook(request):
    """Shutdown the notebook of the current user."""
    _shutdown_notebook(request, request.user.username)
    return HTTPFound(request.route_url("home"))