from flask import render_template
from app import user

def render_template_with_nav(file, **kwargs):
    u = user.get_current_user()
    sidebar = render_template("sidebar.html", **kwargs, user=u)
    nav = render_template("nav.html", **kwargs, user=u)
    
    html = render_template(file, **kwargs, user=u)
    html = html.replace('<div id="nav-sidebar"></div>', sidebar)
    html = html.replace('<div id="nav"></div>', nav)

    return html