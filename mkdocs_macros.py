from datetime import datetime

# This file is used by mkdocs-macros-plugin

def define_env(env):
    """Define variables and functions to be available in MkDocs templates and Markdown.

    Usage in Markdown: {{ year }} or {{ now().year }}
    """
    env.variables['year'] = datetime.utcnow().year
    env.variables['now'] = datetime.utcnow
