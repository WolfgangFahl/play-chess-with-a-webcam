#!/usr/bin/python
# part of https://github.com/WolfgangFahl/play-chess-with-a-webcam
# see:
# https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_image_histogram_calcHist.php
# https://giusedroid.blogspot.com/2015/04/using-python-and-k-means-in-hsv-color.html
from enum import IntEnum

import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class PlotType(IntEnum):
    """kind of Plot"""

    HISTOGRAMM = 0
    PLOT = 1


class PlotLib(object):
    """
    create matplotlib based multipage diagrams e.g. color channel histograms of images
    """

    def __init__(self, title, pagesize, imagesPerPage=4):
        """
        Constructor
        """
        self.title = title
        self.pagesize = pagesize
        self.pagewidth, self.pageheight = self.pagesize
        self.imagesPerPage = imagesPerPage
        self.images = []

    @staticmethod
    def A4(turned=False):
        # A4 canvas
        fig_width_cm = 21  # A4 page size in cm
        fig_height_cm = 29.7
        inches_per_cm = 1 / 2.54  # Convert cm to inches
        fig_width = fig_width_cm * inches_per_cm  # width in inches
        fig_height = fig_height_cm * inches_per_cm  # height in inches
        fig_size = [fig_width, fig_height]
        if turned:
            fig_size = fig_size[::-1]
        return fig_size

    def addPlot(self, image, imageTitle, xvalues=[], yvalues=[], isBGR=False):
        rgb = image
        if isBGR:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.images.append((rgb, imageTitle, xvalues, yvalues))

    def plotImage(self, ax, image, imageTitle, thumbNailSize):
        thumbNail = cv2.resize(image, (thumbNailSize, thumbNailSize))
        ax.imshow(thumbNail)
        ax.title.set_text(imageTitle)
        ax.axis("off")
        pass

    def plotChannel(self, img, ax, channel, prevAx=None):
        cImg = img[:, :, channel]
        ax.hist(np.ndarray.flatten(cImg), bins=256)
        if prevAx is not None:
            # Use matplotlib's sharex parameter instead of manually joining axes
            ax.sharex(prevAx)
            prevAx.set_xticklabels([])

        ax.set_yticklabels([])
        return ax

    def plotHistogramm(self, image, axarr, rowIndex, colIndex):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        rgb = image
        prevAx1 = self.plotChannel(hsv, axarr[rowIndex + 0, colIndex + 0], 0)  # hue
        prevAx2 = self.plotChannel(
            hsv, axarr[rowIndex + 0, colIndex + 1], 1
        )  # saturation
        prevAx3 = self.plotChannel(hsv, axarr[rowIndex + 0, colIndex + 2], 2)  # value
        self.plotChannel(rgb, axarr[rowIndex + 1, colIndex + 0], 0, prevAx1)  # red
        self.plotChannel(rgb, axarr[rowIndex + 1, colIndex + 1], 1, prevAx2)  # green
        self.plotChannel(rgb, axarr[rowIndex + 1, colIndex + 2], 2, prevAx3)  # blue

    def fixPath(self, path):
        if not path.endswith(".pdf"):
            path = path + ".pdf"
        return path

    def addInfos(self, pdf, infos):
        pdfinfo = pdf.infodict()
        for key, info in infos.items():
            pdfinfo[key] = info

    def pixel(self, fig, inch):
        return int(inch * fig.dpi)

    def startPDF(self, path):
        path = self.fixPath(path)
        return PdfPages(path)

    def finishPDFPage(self, pdf):
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    def finishPDF(self, pdf, infos={}):
        self.addInfos(pdf, infos)

    def createHistogramPDF(self, path, plotType=PlotType.HISTOGRAMM, infos={}):
        imageIndex = 0
        with self.startPDF(path) as pdf:
            self.pages = len(self.images) // self.imagesPerPage
            for page in range(self.pages + 1):
                colTitles = ["image", "", "hue/blue", "saturation/green", "value/red"]
                if plotType == PlotType.PLOT:
                    colTitles = ["image", "", "diffSum", ""]
                cols = len(colTitles)
                rows = self.imagesPerPage * 2
                fig, axarr = plt.subplots(rows, cols, figsize=self.pagesize)
                if fig is None:
                    pass
                for ax, colTitle in zip(axarr[0], colTitles):
                    ax.set_title(colTitle)
                thumbNailSize = 512  # self.pixel(fig,self.pageheight)
                for pageImageIndex in range(0, self.imagesPerPage):
                    if imageIndex < len(self.images):
                        image, imageTitle, xvalues, yvalues = self.images[imageIndex]
                        # see https://matplotlib.org/3.1.1/tutorials/intermediate/tight_layout_guide.html#sphx-glr-tutorials-intermediate-tight-layout-guide-py
                        axImage = plt.subplot2grid(
                            (rows, cols), (pageImageIndex * 2, 0), colspan=2, rowspan=2
                        )
                        self.plotImage(axImage, image, imageTitle, thumbNailSize)
                        if plotType == PlotType.HISTOGRAMM:
                            self.plotHistogramm(image, axarr, pageImageIndex * 2, 2)
                        else:
                            axPlot = plt.subplot2grid(
                                (rows, cols),
                                (pageImageIndex * 2, 2),
                                colspan=2,
                                rowspan=2,
                            )
                            axPlot.plot(xvalues, yvalues)

                    else:
                        for col in range(cols):
                            axarr[pageImageIndex * 2, col].remove()
                            axarr[pageImageIndex * 2 + 1, col].remove()
                    imageIndex = imageIndex + 1
                # plt.title("page %d" %(page))
                self.finishPDFPage(pdf)
            self.finishPDF(pdf, infos)
