"""
Individueel onderdeel
Interface for executing heatmap program.

Execute: `python3 heatmap.py` or use in main by calling heatmap(schedule)

heatmap, annotate_heatmap and plot_heatmap are helpers functions from matplotlib
source code: https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html

Student: Julia Geisler
Course: Algoritmen en Heuristieken 2023
"""

import random, warnings, argparse, matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ..helpers.data import InputData, load_pickle
from ..algorithms import generate_solutions, Randomizer
from ..classes import Schedule
from ..classes.result import Result


# DEFINE CONSTANTS
WEEK_DAYS = ["MA", "DI", "WO", "DO", "VR"]
ROOMS = ["A1.04", "A1.06", "A1.08", "A1.10", "B0.201", "C0.110", "C1.112"]  # col labels
PERIODS = ["9-11", "11-13", "13-15", "15-17", "17-19"]  # row labels
COLORS = ["pink", "lightgreen", "lightblue", "wheat", "salmon", "red", "yellow"]


class Heatmap:
    def __init__(self, schedule: Schedule, verbose=False) -> None:
        self.verbose = verbose
        # timeslots in order of day - period - room
        self.timeslots = sorted(list(schedule.timeslots.values()), key=lambda x: x.moment)
        self.data = self._create_array(schedule)
        self.timetableplot = self.timetable()
        self.heatmapview = self.plot_heatmap()

    def _create_array(self, schedule: Schedule):
        """Creates array of subscores from result.py of 35 (5 days * 7 rooms) by 5 (periods)"""
        # Initialize empty array for heatmap
        heat = Result(schedule)
        shape = (5, 35)
        mat = np.zeros(shape, dtype=int)

        for timeslot in self.timeslots:
            subheat = heat.sub_score(timeslot)
            row = timeslot.period
            column = ROOMS.index(timeslot.room.name) + (len(ROOMS) * timeslot.day)
            mat[row][column] = subheat
        return mat

    def timetable(self):
        """Creates full timetable plot for all rooms in the week"""
        output_path = f"output/timetable.png"

        # Set Axis
        fig = plt.figure()
        gs = fig.add_gridspec(1, 5, wspace=0)
        ax = gs.subplots(
            sharey=True,
        )
        fig.suptitle("Timetable")

        # Set y-axis
        fig.supylabel("Time")
        plt.ylim(19, 9)
        plt.yticks(range(9, 21, 2))

        # Set x-axis for all 7 rooms for every day of the work week
        for day in WEEK_DAYS:
            weekday_plot = WEEK_DAYS.index(day)
            ax[weekday_plot].set_xlim(-0.5, len(ROOMS) - 0.5)
            ax[weekday_plot].set_xticks(range(0, len(ROOMS)), rotation=-30, ha="right", rotation_mode="anchor")
            ax[weekday_plot].set_xticklabels(ROOMS, fontsize=5, rotation=-30, ha="right", rotation_mode="anchor")
            # Let the horizontal axes labeling appear on top
            ax[weekday_plot].tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

        for timeslot in self.timeslots:
            # fill time table plot
            activities = list(timeslot.activities.values())
            if len(activities) != 1:
                continue
            activity = activities[0]
            event = activity.course.name + "\n" + activity.act_type
            room = ROOMS.index(timeslot.room.name) - 0.48
            period = timeslot.period_names[timeslot.period]
            end = period + 2
            ax[timeslot.day].fill_between(
                [room, room + 0.96],
                period,
                end,
                color=COLORS[ROOMS.index(timeslot.room.name)],
                edgecolor="k",
                linewidth=0.5,
            )
            ax[timeslot.day].text(
                room + 0.48, (period + end) * 0.5, event, ha="center", va="center", fontsize=5, rotation=90
            )

        if self.verbose:
            print(f"Timetable plot saved to {output_path}")

    def heatmap(self, row_labels, col_labels, ax, cbarlabel="", **kwargs):
        """Creates heatmap with labels and colorbar"""
        # Initialize Axes, colorbar dictionary, colorbar label

        # Plot heatmap without zeros
        data_masked = np.ma.masked_where(self.data == 0, self.data)
        im = ax.imshow(data_masked, **kwargs)

        # Create colorbar
        im_ratio = self.data.shape[0] / self.data.shape[1]
        # fraction=0.047*im_ratio //  orientation='horizontal'
        cbar = ax.figure.colorbar(im, ax=ax, fraction=0.047 * im_ratio)
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom", fontsize=9)

        # Show all ticks and label them with the respective list entries.
        ax.set_xticks(np.arange(self.data.shape[1]), labels=col_labels, fontsize=7)
        ax.set_yticks(np.arange(self.data.shape[0]), labels=row_labels, fontsize=7)

        # Let the horizontal axes labeling appear on top.
        ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor")

        # Turn spines off and create white grid.
        ax.spines[:].set_visible(False)

        ax.set_xticks(np.arange(self.data.shape[1] + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(self.data.shape[0] + 1) - 0.5, minor=True)
        ax.grid(which="minor", color="w", linestyle="-", linewidth=3)
        ax.tick_params(which="minor", bottom=False, left=False)

        return im, cbar

    def annotate_heatmap(self, im, textcolors=("black", "white"), threshold=None, **textkw):
        """Adds values to every pixel in heatmap"""
        # Normalize the threshold to the images color range.
        if threshold is not None:
            threshold = im.norm(threshold)
        else:
            threshold = im.norm(self.data.max()) / 2.0

        # Set default alignment to center, but allow it to be
        # overwritten by textkw.
        kw = dict(horizontalalignment="center", verticalalignment="center")
        kw.update(textkw)

        # Get the formatter in case a string is supplied
        valfmt = matplotlib.ticker.StrMethodFormatter("{x}")  # type: ignore

        # Loop over the data and create a `Text` for each "pixel".
        # Change the text's color depending on the data.
        texts = []
        for i in range(self.data.shape[0]):
            for j in range(self.data.shape[1]):
                if self.data[i, j] != 0:
                    kw.update(color=textcolors[int(im.norm(self.data[i, j]) > threshold)])
                    text = im.axes.text(j, i, valfmt(self.data[i, j], None), **kw)
                    texts.append(text)

        return texts

    def plot_heatmap(self, vmax=False):
        """Plots heatmap using correct dimensions"""
        output_path = f"output/heatmap.png"
        plt.rcParams["figure.figsize"] = [10, 3.50]
        plt.rcParams["figure.autolayout"] = True
        fig, ax = plt.subplots()
        if vmax:
            im, cbar = self.heatmap(
                PERIODS, ROOMS * 5, ax, cmap="rainbow", vmin=0, vmax=20, cbarlabel="conflict [score/period]"
            )
        else:
            im, cbar = self.heatmap(PERIODS, ROOMS * 5, ax, cmap="rainbow", vmin=0, cbarlabel="conflict [score/period]")
        texts = self.annotate_heatmap(im, size=7)

        fig.tight_layout()
        if self.verbose:
            print(f"Heatmap saved to {output_path}")
        plt.savefig(output_path, dpi=200)
