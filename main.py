"""
Interface for executing scheduler program.

Execute: `python3 main.py -h` for usage.

Student: Anna Neefjes, Julia Geisler, Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


import argparse
import random
import warnings
from program_code import (
    InputData,
    generate_solutions,
    Randomizer,
    Greedy,
    EvolutionSolver,
    HillClimber,
    SimulatedAnnealing,
    DirectedSA,
    dump_result,
    schedule_to_csv,
    visualize_graph,
    plot_histogram,
    Heatmap,
    plot_timetable,
)


def main(
    stud_prefs_path: str,
    courses_path: str,
    rooms_path: str,
    n_subset: int,
    method: str,
    verbose: bool = False,
    show_progress=True,
    do_plot: bool = True,
    do_save: bool = True,
    **kwargs,
):
    """Interface for executing scheduling program."""
    # Load dataset
    input_data = InputData(stud_prefs_path, courses_path, rooms_path)
    data_arguments = input_data.__dict__

    # Optionally take (random) subset of data
    if n_subset:
        if n_subset > len(input_data.students_input):
            warnings.warn("WARNING: Chosen subset size is larger than set size, continuing anyway.")
        else:
            data_arguments["students_input"] = random.sample(input_data.students_input, n_subset)

    do_multithreading = False
    do_compression = False

    # Initialize solver with correct strategy
    match method:
        case "baseline":
            # Baseline algorithm, most random
            do_compression = True
            solver = Randomizer(**data_arguments, method="uniform")
        case "greedy":
            # Greedy algorithm
            do_multithreading = True
            solver = Greedy(**data_arguments)
        case "min_overlap":
            # Improvement on baseline with bias towards least course conflicts
            do_compression = True
            solver = Randomizer(**data_arguments, method="min_overlap")
        case "min_gaps":
            # Improvement on baseline with bias towards least gap hours
            do_compression = True
            solver = Randomizer(**data_arguments, method="min_gaps")
        case "min_gaps_overlap":
            # Improvement on baseline with bias towards least gap hours, then least course conflicts
            do_compression = True
            solver = Randomizer(**data_arguments, method="min_gaps_overlap")
        case "hillclimber":
            # Population based solver, only helpful mutations
            do_multithreading = True
            solver = EvolutionSolver(**data_arguments, mutation_supplier=HillClimber())
        case "simulated_annealing":
            # Population based solver, score based mutation acceptance
            do_multithreading = True
            solver = EvolutionSolver(**data_arguments, mutation_supplier=SimulatedAnnealing())
        case "directed_sa":
            # Population based solver, bias towards mutating highest conflict areas
            do_multithreading = True
            warnings.warn("Directed Simulated Annealing not yet fully implemented!")
            solver = EvolutionSolver(**data_arguments, mutation_supplier=DirectedSA())
        case _:
            raise ValueError("Invalid method chosen.")

    # Retrieve results
    results = generate_solutions(
        solver,
        show_progress=show_progress,
        compress=do_compression,
        multithreading=do_multithreading,
        **kwargs,
    )

    # Take random sample and rebuild schedule from edges
    sampled_result = random.choice(results)
    sampled_result.decompress(**data_arguments)

    # Dump results to disk
    if do_save:
        dumped_loc = dump_result(results, f"output/results_{method}_{kwargs}_")
        print("Dumped results to", dumped_loc)
        schedule_to_csv(sampled_result.schedule)
        print("Dumped a sampled schedule to", "output/schedule.csv")

    if verbose:
        # Initialize `score_vector`
        sampled_result.score_vector
        print("Sampled result: ", sampled_result)

    if not do_plot:
        return

    # Visualize graph
    visualize_graph(sampled_result.schedule)

    # Visualize score dimensions
    plot_histogram(results)

    # Plot heatmap of conflict timeslots
    Heatmap(sampled_result.schedule)

    # Visualizer random student's schedule
    plot_timetable(sampled_result.schedule, "student")


if __name__ == "__main__":
    # Create a command line argument parser
    parser = argparse.ArgumentParser(prog="main.py", description="Make a schedule.")

    parser.add_argument(
        "-m",
        dest="method",
        choices=[
            "baseline",
            "greedy",
            "min_overlap",
            "min_gaps",
            "min_gaps_overlap",
            "hillclimber",
            "simulated_annealing",
            "directed_sa",
        ],
        default="simulated_annealing",
        help="Choose method.",
    )
    parser.add_argument("-i", type=int, dest="i_max", help="max iterations per solve cycle.")
    parser.add_argument("-n", type=int, dest="n", default=1, help="amount of results to generate.")
    parser.add_argument(
        "-sub", type=int, dest="n_subset", help="Subset: amount of students to take into account out of dataset."
    )
    parser.add_argument("-v", dest="verbose", action="store_true", help="Verbose: log error messages.")
    parser.add_argument(
        "--prefs",
        dest="stud_prefs_path",
        default="data/studenten_en_vakken.csv",
        help="Path to student enrolments csv.",
    )
    parser.add_argument("--courses", dest="courses_path", default="data/vakken.csv", help="Path to courses csv.")
    parser.add_argument("--rooms", dest="rooms_path", default="data/zalen.csv", help="Path to rooms csv.")
    parser.add_argument("--no_plot", dest="do_plot", action="store_false", help="Don't show matplotlib plot")
    parser.add_argument("--discard", dest="do_save", action="store_false", help="Don't save results to disk.")

    # Read arguments from command line
    args = parser.parse_args()
    kwargs = vars(args)

    # Run program through interface with provided arguments
    main(**kwargs)
