from flask import Blueprint
from ..models import Permission
main = Blueprint('main', __name__)


# when permissions need to be checked form tmplates, Permission class needs to be accessable.
# to avoid having to add template argument in every render_template()
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


from . import views, errors