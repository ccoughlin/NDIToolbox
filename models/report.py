"""report - simple PDF report generator for NDIToolbox

Chris R. Coughlin (TRI/Austin, Inc.)
"""

import pyPdf
from reportlab.lib.pagesizes import letter, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import utils
import os.path
import tempfile


class ReportSection(object):
    """Defines a section for the Report class"""

    def __init__(self, heading):
        self.heading = heading
        self.contents = []

    def add_figure(self, figure, caption=None):
        """Adds a figure and optional caption to the contents.  The figure argument should point to the full path
        and filename of the image to include."""
        self.contents.append({'figure':figure,
                              'caption':caption})

    def add_table(self, table, caption=None):
        """Adds a table and optional caption to the contents.  The table should be a 2D list, where table element
        [i][j] becomes the contents of the table cell at row[i] column [j].
        """
        self.contents.append({'table':table,
                              'caption':caption})

    def add_text(self, text):
        """Adds a block of text to the contents.  Text can be a single string or a list of strings; the final text
        block is separated by newline characters (\n).  To insert a blank line between paragraphs use the empty
        string '\n' in the block."""
        if isinstance(text, list):
            text = ''.join(text)
        self.contents.append({'text':text.split('\n')})


class Report(object):
    """Basic PDF report generator for NDIToolbox"""

    def __init__(self, output_filename, front_matter=None, end_matter=None):
        self.output_filename = os.path.normcase(output_filename)
        if front_matter is not None:
            self.front_matter = os.path.normcase(front_matter)
        if end_matter is not None:
            self.end_matter = os.path.normcase(end_matter)
        self.sections = []

    def build_table(self, data):
        """Generates and returns a simple ReportLab table from the specified 2D list.  The first row (data[0]) is taken
        as a header, use an empty row (data[0] = []) to skip."""
        style = [('INNERGRID', (0, 0), (-1, -1), 0.125, (0.53, 0.63, 0.75)),
                 ('BOX', (0, 0), (-1, -1), 0.125, (0.27, 0.32, 0.38))]
        if len(data[0]) > 0:
            style.extend([('BACKGROUND', (0, 0), (-1, 0), (0.31, 0.40, 0.51)),
                          ('TEXTCOLOR', (0,0), (-1, 0), (0.89, 0.82, 0.60)),
                          ('ALIGNMENT', (0, 0), (-1, 0), 'CENTER')])
        else:
            data = data[1:]
        table = Table(data, style=style)
        return table

    def write(self):
        """Assembles the final PDF and writes to disk."""
        pdf_writer = pyPdf.PdfFileWriter()
        if self.front_matter is not None:
            front_matter = pyPdf.PdfFileReader(file(self.front_matter, "rb"))
            for page in range(front_matter.getNumPages()):
                pdf_writer.addPage(front_matter.getPage(page))
        working_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc = SimpleDocTemplate(working_file)
        doc.pagesize = portrait(letter)
        story = []
        styles = getSampleStyleSheet()
        for section in self.sections:
            heading_text = section.heading
            story.append(Paragraph(heading_text, styles['Heading1']))
            for content in section.contents:
                if 'figure' in content:
                    figure = content['figure']
                    if os.path.exists(figure):
                        im = utils.ImageReader(figure)
                        img_width, img_height = im.getSize()
                        aspect = img_height / float(img_width)
                        story.append(Image(figure, width=img_width, height=(img_width*aspect)))
                    if content.get('caption', None) is not None:
                        caption_text = '<font size=10>{0}</font>'.format(content['caption'].strip())
                        story.append(Paragraph(caption_text, styles['Italic']))
                        story.append(Spacer(1, 10))
                if 'table' in content:
                    _t = self.build_table(content['table'])
                    story.append(_t)
                    if content.get('caption', None) is not None:
                        caption_text = '<font size=10>{0}</font>'.format(content['caption'].strip())
                        story.append(Paragraph(caption_text, styles['Italic']))
                        story.append(Spacer(1, 10))
                if 'text' in content:
                    for para in content['text']:
                        story.append(Paragraph(para, styles['Normal']))
                        story.append(Spacer(1, 12))
        doc.build(story)
        body_matter = pyPdf.PdfFileReader(working_file)
        for page in range(body_matter.getNumPages()):
            pdf_writer.addPage(body_matter.getPage(page))
        try:
            os.remove(working_file.name)
        except OSError: # Windows reports file in use, other OS errors, etc.
            pass
        if self.end_matter is not None:
            end_matter = pyPdf.PdfFileReader(file(self.end_matter, "rb"))
            for page in range(end_matter.getNumPages()):
                pdf_writer.addPage(end_matter.getPage(page))
        output_stream = file(self.output_filename, "wb")
        pdf_writer.write(output_stream)