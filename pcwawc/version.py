"""
Created on 2025-03-12

@author: wf
"""

from dataclasses import dataclass

import pcwawc


@dataclass
class Version(object):
    """
    Version handling for play chess with a Webcam
    """

    name = "pcwawc"
    version = pcwawc.__version__
    date = "2019-10-21"
    updated = "2025-03-12"
    description = "Play Chess with a Webcam"

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/PlayChessWithAWebCam"
    chat_url = "https://github.com/WolfgangFahl/play-chess-with-a-webcam/discussions"
    cm_url = "https://github.com/WolfgangFahl/play-chess-with-a-webcam"

    license = f"""Copyright 2019-2025     contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
