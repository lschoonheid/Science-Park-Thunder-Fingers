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
    Data,
    SolverSC,
    generate_solutions,
    Randomizer,
    Greedy,
    GeneticSolver,
    HillClimber,
    SimulatedAnnealing,
    DirectedSA,
    GraphVisualization,
    plot_statistics,
)
from sched_csv_output import schedule_to_csv

# TODO: write interface code to execute complete program from command line
def main(
    stud_prefs_path: str,
    courses_path: str,
    rooms_path: str,
    n_subset: int,
    method: str,
    verbose: bool = False,
    do_plot: bool = True,
    show_progress=True,
    **kwargs,
):
    """Interface for executing scheduling program."""
    # Load dataset
    input_data = Data(stud_prefs_path, courses_path, rooms_path)
    data_arguments = input_data.__dict__

    # Optionally take subset of data
    # TODO #40 take random students of subset to prevent overfitting
    if n_subset:
        if n_subset > len(input_data.students_input):
            warnings.warn("WARNING: Chosen subset size is larger than set size, continuing anyway.")
        else:
            data_arguments["students_input"] = random.sample(input_data.students_input, n_subset)

    # Initialize solver

    match method:
        case "baseline":
            solver = Randomizer(**data_arguments, method="uniform")
        case "directed_sa":
            solver = GeneticSolver(**data_arguments, mutation_supplier=DirectedSA())
        case "simulated_annealing":
            solver = GeneticSolver(**data_arguments, mutation_supplier=SimulatedAnnealing())
        case "hillclimber":
            solver = GeneticSolver(**data_arguments, mutation_supplier=HillClimber())
        case _:
            raise ValueError("Invalid method chosen.")

    # Generate (compressed) results: only return scorevector and edges
    results_compressed = generate_solutions(
        solver,
        show_progress=show_progress,
        **kwargs,
    )

    # Take random sample and rebuild schedule from edges
    sampled_result = random.choice(results_compressed)
    sampled_result.decompress(**data_arguments)

    # Visualize graph
    if verbose:
        sampled_result.score_vector
        print(sampled_result)

    if not do_plot:
        return

    G = GraphVisualization(sampled_result.schedule)
    G.visualize()
    schedule_to_csv(sampled_result.schedule)

    # Visualize score dimensions
    plot_statistics(results_compressed)


if __name__ == "__main__":
    # Create a command line argument parser
    parser = argparse.ArgumentParser(prog="main.py", description="Make a schedule.")

    parser.add_argument(
        "-m",
        dest="method",
        choices=[
            "baseline",
            "min_overlap",
            "min_gaps",
            "min_gaps_overlap",
            "directed_sa",
            "simulated_annealing",
            "hillclimber",
            "greedy",
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

    # Read arguments from command line
    args = parser.parse_args()
    kwargs = vars(args)

    # Run program through interface with provided arguments
    main(**kwargs)
