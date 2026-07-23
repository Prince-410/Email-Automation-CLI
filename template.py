import os
import jinja2
from typing import List

def load_template(template_path: str) -> jinja2.Template:
    """
    Loads an HTML template file and returns a Jinja2 Template object.
    
    Args:
        template_path (str): The path to the template file.
        
    Returns:
        jinja2.Template: The loaded Jinja2 template object.
        
    Raises:
        FileNotFoundError: If the template file does not exist.
        jinja2.TemplateSyntaxError: If the template has syntax errors.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")
        
    # Get the directory and filename
    template_dir, template_name = os.path.split(template_path)
    
    # Set up the Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir or '.'),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )
    
    try:
        template = env.get_template(template_name)
        return template
    except jinja2.TemplateSyntaxError as e:
        raise jinja2.TemplateSyntaxError(f"Syntax error in template '{template_path}': {e.message}", e.lineno, e.name, e.filename) from e

def render_template(template: jinja2.Template, context: dict) -> str:
    """
    Renders the template with the given context dict.
    
    Args:
        template (jinja2.Template): The Jinja2 template object.
        context (dict): The context data for rendering the template.
        
    Returns:
        str: The rendered template string.
    """
    return template.render(**context)

def get_available_templates(template_dir: str = 'templates') -> List[str]:
    """
    Lists available .html template files in the specified directory.
    
    Args:
        template_dir (str, optional): The directory to search. Defaults to 'templates'.
        
    Returns:
        List[str]: A list of available .html template filenames.
    """
    if not os.path.isdir(template_dir):
        return []
        
    templates = []
    for filename in os.listdir(template_dir):
        if filename.endswith('.html'):
            templates.append(filename)
            
    return templates
