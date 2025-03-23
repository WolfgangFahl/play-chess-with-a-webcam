'''
Created on 2025-03-12

@author: wf
'''
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, ui
from pcwawc.version import Version
from pcwawc.webapp import WebApp

class WebServer(InputWebserver):
    """
    WebServer class that manages the server

    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2019-2025 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right,
            version=Version(),
            default_port=5003,
            short_name="pcwawc",
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = ChessSolution
        return server_config

    def __init__(self):
        """
        Constructs all the necessary attributes for the
        WebServer object.
        """
        config = WebServer.get_config()
        InputWebserver.__init__(self, config=config)

class ChessSolution(InputWebSolution, WebApp):
    """
    A class to handle the UI and integration for PlayChessWithAWebcam.
    """

    def __init__(self, webserver: WebServer, client: Client):
        """
        Initialize the solution

        Calls the constructor of the base solution
        Args:
            webserver (WebServer): The webserver instance associated with this context.
            client (Client): The client instance this context is associated with.
        """
        # Initialize InputWebSolution first
        super(InputWebSolution, self).__init__(webserver, client)

        # Initialize WebApp with webserver's args and logger
        WebApp.__init__(self, webserver.args, logger=webserver.logger)

