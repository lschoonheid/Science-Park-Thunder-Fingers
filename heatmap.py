"""
Individueel onderdeel
Interface for executing heatmap program.

Execute: `python3 heatmap.py`.

Student: Julia Geisler
Course: Algoritmen en Heuristieken 2023
"""

import random, warnings, argparse
import matplotlib.pyplot as plt
import numpy as np
from program_code import (
    Data,
    generate_solutions,
    Randomize,
    Schedule,
    Result)

WEEK_DAYS = ["MA", "DI", "WO", "DO", "VR"]
ROOMS = ["A1.04","A1.06","A1.08","A1.10","B0.201","C0.110","C1.112"]
COLORS = ['pink', 'lightgreen', 'lightblue', 'wheat', 'salmon', 'red', 'yellow']

def plot_heatmap(schedule: Schedule):
    heat = Result(schedule)
    total_heat = heat.score
    print(f'total heat = {total_heat}')
    shape = (5,35)
    mat = np.zeros(shape,dtype=int)
    
    # timeslots in order of day - period - room
    timeslots = sorted(list(schedule.timeslots.values()), key=lambda x: x.moment)
    for timeslot in timeslots:
        subheat = heat.sub_score(timeslot)
        row = timeslot.period
        column = ROOMS.index(timeslot.room.name) + (len(ROOMS) *timeslot.day)
        mat[row][column] = subheat
    plt.imshow(mat)
    plt.title("Heatmap")
    output_path = f"output/heatmap.png"
    plt.savefig(output_path, dpi=200)

def plot_full_timetable(schedule: Schedule):
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
        ax[weekday_plot].set_aspect('equal', adjustable='box')

    # timeslots in order of day - period - room
    timeslots = sorted(list(schedule.timeslots.values()), key=lambda x: x.moment)
    for timeslot in timeslots:
        # print(f'subheat of {subheat}')
        activity = list(timeslot.activities.values())[0]
        event = activity.course.name + "\n" + activity.act_type
        room = ROOMS.index(timeslot.room.name) - 0.48
        period = timeslot.period_names[timeslot.period]
        end = period+2
        ax[timeslot.day].fill_between([room, room+0.96], period, end, color=COLORS[ROOMS.index(timeslot.room.name)], edgecolor='k', linewidth=0.5)
        ax[timeslot.day].text(room+0.48, (period+end)*0.5, event, ha='center', va='center', fontsize=1)
    output_path = f"output/timetable.png"
    plt.savefig(output_path, dpi=200)

""" 
main function is a selected copy from main.py 
to assure timetable.py can be run independently
"""
def main(stud_prefs_path: str, courses_path: str, rooms_path: str, n_subset: int, verbose: bool = False, **kwargs):
    """Interface for executing scheduling program."""
    # Load dataset
    input_data = Data(stud_prefs_path, courses_path, rooms_path)
    students_input = input_data.students
    courses_input = input_data.courses
    rooms_input = input_data.rooms

    # Optionally take subset of data
    if n_subset:
        if n_subset > len(students_input):
            warnings.warn("WARNING: Chosen subset size is larger than set size, continuing anyway.")
        else:
            students_input = random.sample(students_input, n_subset)

    # Generate (compressed) results: only return scorevector and edges
    results_compressed = generate_solutions(
        Randomize(
            students_input,
            courses_input,
            rooms_input,
            verbose=verbose,
        ),
        **kwargs,
    )

    # Take random sample and rebuild schedule from edges
    sampled_result = random.choice(results_compressed)
    sampled_result.decompress(
        students_input,
        courses_input,
        rooms_input,
    )
    plot_heatmap(sampled_result.schedule)
    plot_full_timetable(sampled_result.schedule)

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