# -*- coding: utf-8 -*-     # * *  necessary for pycharm/python to understand hebrew!!!! * *

import sys
from xhtml2pdf import pisa
import cStringIO as StringIO
# from fpdf import FPDF
import io
import sys


# https://stackoverflow.com/questions/4047095/trouble-using-xhtml2pdf-with-unicode
from bidi import algorithm as bidialg       # pip install python-bidi
from xhtml2pdf import pisa                  # pip install xhtml2pdf

# src: url(my_fonts_dir / DejaVuSans.ttf);

HTMLINPUT = """
            <!DOCTYPE html>
            <html>
            <head>
               <meta http-equiv="content-type" content="text/html; charset=utf-8">
               <style>
                  @page {
                      size: a4;
                      margin: 1cm;
                  }

                  @font-face {
                      font-family: DejaVu;
                      src: url(DejaVuSans.ttf);
                  }

                  html {
                      font-family: DejaVu;
                      font-size: 11pt;
                  }
               </style>
            </head>
            <body>
               <div>Something in English - משהו בעברית</div>
            </body>
            </html>
            """

fw11 = open('test11.pdf', 'w')
outputfile = fw11
pdf = pisa.CreatePDF(bidialg.get_display(HTMLINPUT, base_dir="L"), outputfile)

# I'm using base_dir="L" so that "< >" signs in HTML tags wouldn't be
# flipped by the bidi algorithm




# sys.setdefaultencoding('UTF-8')     # still heb strings log lft->rgt reversed(?)

fw22 = open('test22.pdf', 'w')
outputfile = fw22

with open('layout.html', 'r') as f:
# with io.open('arb.html', 'r', encoding='utf-8') as f:
    html_fread = f.read()
    html_fread = bidialg.get_display(html_fread, base_dir="L")
    # pdf = pisa.pisaDocument(f, dest=result)
    # pdf = pisa.pisaDocument(StringIO.StringIO(input), dest=result)
    # pdf = pisa.CreatePDF(bidialg.get_display(input, base_dir="L"), outputfile)
    pdf = pisa.CreatePDF(html_fread, outputfile)


# pdf = FPDF()
# pdf.add_page()
# pdf.set_font('Arial', 'B', 16)
# # pdf.cell(40, 10, 'Hello World!')
# pdf.cell(40, 10, output)
# pdf.output('tuto1.pdf', 'F')


# from django.template.loader import get_template
# from django.template import Context
# def html_to_pdf_directly(request):
	# template = get_template("template_name.html")
	# context = Context({'pagesize':'A4'})
	# html = template.render(context)
# result = StringIO.StringIO()
# pdf = pisa.pisaDocument(output, dest=result)
# pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
# pdf = pisa.pisaDocument(StringIO.StringIO(output), dest=result)
# if not pdf.err:
#     return HttpResponse(result.getvalue(), content_type='application/pdf')
# else: return HttpResponse('Errors')
