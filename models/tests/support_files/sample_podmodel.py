from models.podtk_model import PODModel

class SamplePODModel(PODModel):
    name = "Sample POD Model"
    description = "Generic POD Model used in unit tests"
    authors = "TRI/Austin, Inc."
    version = "1.0"
    url = "www.nditoolbox.com"
    copyright = "Copyright (C) 2012 TRI/Austin, Inc."


    def __init__(self):
        PODModel.__init__(self, self.name, self.description, self.inputdata, self.params,
                          self.settings)

    def run(self):
        """Executes the POD Model"""

        # *** Do something interesting here ***

        # To display a spreadsheet of output data to the user
        # uncomment this line and set it to the NumPy array of interest
        # self._data = None

        # To display a textual summary to the user
        # uncomment this line and set it to a string
        # self.results = "POD Model completed successfully."

    def plot1(self, axes_hdl):
        """Generates the primary plot on the specified matplotlib Axes instance."""

        # If you want to generate a plot in the Plot 1 control. axes_hdl is a handle to
        # the Plot 1 Axes, see http://matplotlib.sourceforge.net/users/pyplot_tutorial.html
        # for examples on usage e.g. axes_hdl.plot([1, 2, 3, 4])
        pass

    def plot2(self, axes_hdl):
        """Generates the secondary plot on the specified matplotlib Axes instance."""

        # If you want to generate a plot in the Plot 2 control. axes_hdl is a handle to
        # the Plot 2 Axes, see http://matplotlib.sourceforge.net/users/pyplot_tutorial.html
        # for examples on usage e.g. axes_hdl.plot([1, 2, 3, 4])
        pass