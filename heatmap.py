"""
Individueel onderdeel
Interface for executing heatmap program.

Execute: `python3 heatmap.py`.

Student: Julia Geisler
Course: Algoritmen en Heuristieken 2023
"""

import random, warnings, argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from program_code import (
    Data,
    generate_solutions,
    Randomizer,
    Schedule,
    Result)

WEEK_DAYS = ["MA", "DI", "WO", "DO", "VR"]
ROOMS = ["A1.04","A1.06","A1.08","A1.10","B0.201","C0.110","C1.112"] # col labels
PERIODS = ["9-11","11-13","13-15","15-17","17-19"] # row labels
COLORS = ['pink', 'lightgreen', 'lightblue', 'wheat', 'salmon', 'red', 'yellow']

def heatmap(data, row_labels, col_labels, ax=None, cbar_kw=None, cbarlabel="", **kwargs):
    if ax is None:
        ax = plt.gca()

    if cbar_kw is None:
        cbar_kw = {}
    
    # Plot heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(data.shape[1]), labels=col_labels)
    ax.set_yticks(np.arange(data.shape[0]), labels=row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

def annotate_heatmap(im, data=None, valfmt="{x:.2f}", textcolors=("black", "white"), threshold=None, **textkw):
    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

def array_heatmap(schedule: Schedule):
    heat = Result(schedule)
    shape = (5,35)
    mat = np.zeros(shape,dtype=int)
    
    # timeslots in order of day - period - room
    timeslots = sorted(list(schedule.timeslots.values()), key=lambda x: x.moment)
    for timeslot in timeslots:
        subheat = heat.sub_score(timeslot)
        row = timeslot.period
        column = ROOMS.index(timeslot.room.name) + (len(ROOMS) *timeslot.day)
        mat[row][column] = subheat
    return mat

def plot_full_timetable(schedule: Schedule):
    # Initialize empty array for heatmap
    heat = Result(schedule)
    shape = (5,35)
    mat = np.zeros(shape,dtype=int)
    
    # Set Axis
    fig = plt.figure()
    gs = fig.add_gridspec(1,5, wspace=0)
    ax = gs.subplots(sharey=True,)
    fig.suptitle('Timetable')
    
    # Set y-axis
    fig.supylabel('Time')
    plt.ylim(19, 9)
    plt.yticks(range(9,21,2))
    
    # Set x-axis for all 7 rooms for every day of the work week
    for day in WEEK_DAYS:
        weekday_plot = WEEK_DAYS.index(day)
        ax[weekday_plot].set_xlim(-0.5,len(ROOMS)-0.5)
        ax[weekday_plot].set_xticks(range(0,len(ROOMS)))
        ax[weekday_plot].set_xticklabels(ROOMS, fontsize=5)
        ax[weekday_plot].tick_params(axis=u'y', which=u'both',length=0)

    # timeslots in order of day - period - room
    timeslots = sorted(list(schedule.timeslots.values()), key=lambda x: x.moment)
    for timeslot in timeslots:
        # array for heatmap
        subheat = heat.sub_score(timeslot)
        row = timeslot.period
        column = ROOMS.index(timeslot.room.name) + (len(ROOMS) *timeslot.day)
        mat[row][column] = subheat

        # full time table plot
        activity = list(timeslot.activities.values())[0]
        event = activity.course.name + "\n" + activity.act_type
        room = ROOMS.index(timeslot.room.name) - 0.48
        period = timeslot.period_names[timeslot.period]
        end = period+2
        ax[timeslot.day].fill_between([room, room+0.96], period, end, color=COLORS[ROOMS.index(timeslot.room.name)], edgecolor='k', linewidth=0.5)
        ax[timeslot.day].text(room+0.48, (period+end)*0.5, event, ha='center', va='center', fontsize=5, rotation=90)
    
    output_path = f"output/timetable.png"
    plt.savefig(output_path, dpi=200)
    return mat

""" 
main function is a selected copy from main.py 
to assure timetable.py can be run independently
"""
def main(stud_prefs_path: str, courses_path: str, rooms_path: str, n_subset: int, verbose: bool = False, do_plot: bool = True, show_progress=True, **kwargs):
    """Interface for executing scheduling program."""
    # Load dataset
    input_data = Data(stud_prefs_path, courses_path, rooms_path)
    data_arguments = input_data.__dict__

    # Optionally take subset of data
    if n_subset:
        if n_subset > len(input_data.students_input):
            warnings.warn("WARNING: Chosen subset size is larger than set size, continuing anyway.")
        else:
            data_arguments["students_input"] = random.sample(input_data.students_input, n_subset)

    # Generate (compressed) results: only return scorevector and edges
    solver = Randomizer(**data_arguments, method="uniform")
    results_compressed = generate_solutions(
        solver,
        show_progress=show_progress,
        **kwargs,
    )

    # Take random sample and rebuild schedule from edges
    sampled_result = random.choice(results_compressed)
    sampled_result.decompress(**data_arguments)

    plot_full_timetable(sampled_result.schedule)
    data = array_heatmap(sampled_result.schedule)
    fig, ax = plt.subplots()

    im, cbar = heatmap(data, PERIODS, ROOMS*5, ax=ax,
                    cmap="YlGn", cbarlabel="conflict [score/period]")
    texts = annotate_heatmap(im, valfmt="{x:.1f}")

    fig.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    # Create a command line argument parser
    parser = argparse.ArgumentParser(prog="main.py", description="Make a schedule.")

    parser.add_argument(
        "--prefs",
        dest="stud_prefs_path",
        default="data/studenten_en_vakken.csv",
        help="Path to student enrolments csv.",
    )
    parser.add_argument("-i", type=int, dest="i_max", help="max iterations per solve cycle.")
    parser.add_argument("-n", type=int, dest="n", default=1, help="amount of results to generate.")
    parser.add_argument(
        "-sub", type=int, dest="n_subset", help="Subset: amount of students to take into account out of dataset."
    )
    parser.add_argument("-v", dest="verbose", action="store_true", help="Verbose: log error messages.")
    parser.add_argument("--courses", dest="courses_path", default="data/vakken.csv", help="Path to courses csv.")
    parser.add_argument("--rooms", dest="rooms_path", default="data/zalen.csv", help="Path to rooms csv.")
    parser.add_argument("--no_plot", dest="do_plot", action="store_false", help="Don't show matplotlib plot")

    # Read arguments from command line
    args = parser.parse_args()
    kwargs = vars(args)

    # Run program through interface with provided arguments
    main(**kwargs)