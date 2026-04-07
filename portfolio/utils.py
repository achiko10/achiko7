from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template


def render_to_pdf(template_src, context_dict={}):
    """
    Renders an HTML template into a PDF document (for direct download).
    """
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return None

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def get_pdf_bytes(template_src, context_dict={}):
    """
    Renders an HTML template into PDF bytes (for email attachment).
    """
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return None

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return result.getvalue()
    return None

