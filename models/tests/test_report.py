"""test_report.py - tests the report module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

import unittest
import os.path
import random
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from models.report import Report, ReportSection
from models import mainmodel

class TestReport(unittest.TestCase):
    """Functional testing for the Report class"""

    def setUp(self):
        self.output_folder = os.path.join(os.path.dirname(__file__), "support_files")
        self.output_file = os.path.join(self.output_folder, "test_report.pdf")
        self.report = Report(self.output_file)

    def generate_sample_plot(self, output_filename, width=5, height=5, title="Sample Data"):
        """Generates a sample plot of random data"""
        # Initialize matplotlib plot formatting to sane defaults
        mainmodel.init_matplotlib_defaults()
        figure = Figure(figsize=(width, height))
        canvas = FigureCanvas(figure)
        axes = figure.gca()
        x = np.arange(-10, 10)
        data = np.sinc(x + random.uniform(-.25, .25))
        linestyles = ['_', '-', '--', ':']
        colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
        axes.plot(x, data, linestyle=random.choice(linestyles), marker=".", color=random.choice(colors))
        axes.set_title(title)
        axes.grid(True)
        figure.savefig(output_filename, format='png')

    def generate_sample_table(self, rows=3, cols=4, header=None):
        """Generates and returns a 2D list suitable for inclusion in a Report as a table.
        If the list header is included, it is prepended to the table as its header."""
        def random_content():
            """Returns some random content for a cell"""
            coin_flip = random.choice([0, 1])
            if coin_flip == 0:
                return random.choice(["Sample Text", "", "Alternate Text", "Lorem Ipsum",
                                      os.path.basename(self.output_file)])
            else:
                return random.uniform(-25, 25)
        table = []
        if header is not None:
            table.append(header)
        for r in range(rows):
            row = []
            for c in range(cols):
                row.append(random_content())
            table.append(row)
        return table

    def test_generate_report(self):
        """Functional test to verify generating a PDF report"""
        self.report.front_matter = os.path.join(self.output_folder, "Sample Front Matter.pdf")
        self.report.end_matter = os.path.join(self.output_folder, "Sample End Matter.pdf")
        lorem_file = os.path.join(self.output_folder, "loremipsum.txt")
        with open(lorem_file, "r") as fidin:
            sample_text = fidin.readlines()
        for i in range(5):
            output_filename = os.path.join(self.output_folder, "plot{0}.png".format(i+1))
            self.generate_sample_plot(output_filename, title="Plot {0}".format(i+1))
            heading = "Section {0}".format(i+1)
            a_section = ReportSection(heading)
            caption = "Sample caption for plot {0}".format(i+1)
            start_idx = random.randint(0, len(sample_text))
            end_idx = start_idx + random.randint(0, len(sample_text)-start_idx)
            text = sample_text[start_idx:end_idx]
            if i%2 == 0:
                _t = self.generate_sample_table(header=["Col 1", "Col 2", "Col 3"])
                _t_caption = "A sample table"
                a_section.add_table(_t, caption=_t_caption)
            a_section.add_figure(output_filename, caption=caption)
            a_section.add_text(text)
            self.report.sections.append(a_section)
        self.report.write()
        print("Please examine the PDF output file {0}.".format(self.output_file))

    def tearDown(self):
            pngs = os.listdir(self.output_folder)
            for png in pngs:
                root, ext = os.path.splitext(png)
                if 'plot' in root and 'png' in ext:
                    try:
                        os.remove(os.path.join(self.output_folder, png))
                    except WindowsError: # Windows reports file in use
                        pass
                    except OSError: # Other operating system error
                        print("Unable to delete test output file {0}.".format(png))

if __name__ == "__main__":
    random.seed()
    unittest.main()