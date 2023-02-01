"""
Individual part
Class for executing population based algorithms.

Execute from main.py: choose strategy (HillClimber, Simulated Annealing, Directed Simulated Annealing).

Student: Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""

import copy
import time
import multiprocessing
from tqdm import tqdm
import matplotlib.pyplot as plt
from .mutationsuppliers import MutationSupplier, SimulatedAnnealing, Mutation
from ..classes import Schedule
from .statistics import Statistics
from .randomizer import Randomizer
from .generate import generate_solutions
from ..classes.result import Result
from ..helpers.data import dump_result


class EvolutionSolver:
    """Evolution based algorithm for improving schedule.
    Takes a solved schedule as input and applies mutations upon it to improve score."""

    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        population_size=5,
        max_generations=30000,
        method="bias",
        mutation_supplier: MutationSupplier = SimulatedAnnealing(),
        verbose=False,
    ) -> None:
        # Build initial population with input
        self.students_input = students_input
        self.courses_input = courses_input
        self.rooms_input = rooms_input

        # Set algorithm bounds
        self.population_size = population_size
        self.max_generations = max_generations

        # `method` defines solving method for baseline solution
        self.method = method
        # Select mutation strategy
        self.mutation_supplier = mutation_supplier

        # Show details of solution process
        self.verbose = verbose

    def fitness(self, score: float | int):
        """Get fitness score of a result."""
        return 10000 / (1 + score)

    def solve(
        self,
        schedule_seed: Schedule | None = None,
        i_max: int | None = None,
        self_repair=False,
        show_progress=True,
        save_result=True,
        plot=False,
    ):
        if i_max is None:
            i_max = self.max_generations

        # If current solving process is a child of a multithreaded operation, take appropriate space in terminal
        try:
            process_id = multiprocessing.current_process()._identity[0]
        except:
            process_id = 0

        # Initialize population from (solved) prototype
        if schedule_seed is None:
            self.population = generate_solutions(
                Randomizer(self.students_input, self.courses_input, self.rooms_input, method=self.method),
                n=self.population_size,
                show_progress=False,
                multithreading=False,
            )
        else:
            assert Result(schedule_seed).is_solved, "Can only improve solved schedules."
            self.population = [
                Result(schedule_seed).deepcopy(self.students_input, self.courses_input, self.rooms_input)
                for i in range(self.population_size)
            ]

        # Sort population by score to pick best specimen
        population_sorted: list[Result] = Statistics.sort_objects(self.population, "score")  # type: ignore
        current_best: Result = population_sorted[0].decompress(
            self.students_input, self.courses_input, self.rooms_input
        )

        # Save backup for repairment in case of errors
        backup_edges = copy.deepcopy(current_best.schedule.edges)

        # Initialize progress tracking variables
        best_score = None
        best_fitness = 0
        track_scores: list[float] = []
        start_time = time.time()
        timestamps = []
        generations = 0

        # Each iteration a mutation is applied and score is checked
        pbar = tqdm(range(i_max), position=process_id, leave=False, disable=not show_progress)
        for i in pbar:
            # Check if a perfect solution is found
            if current_best.score == 0:
                break

            # If required, save current best solution to memory
            if self_repair and self.fitness(current_best.score) > best_fitness and current_best.check_solved():
                backup_edges = copy.deepcopy(current_best.schedule.edges)
                best_score = current_best.score
                best_fitness = self.fitness(best_score)

            # Get suggestion for possible mutation
            mutation: Mutation = self.mutation_supplier.suggest_mutation(current_best)

            # Apply mutation
            mutation.apply()

            # Check whether solution is still valid and an improvement, possibly replace it with last valid solution
            if self_repair and not current_best.check_solved():
                # If better, keep mutation, else revert
                if mutation.inverse is not None:
                    mutation.revert()
                else:
                    current_best = Result(
                        Schedule(self.students_input, self.courses_input, self.rooms_input, backup_edges)
                    )
                continue

            # Clear memory of swaps because of new schedule conditions
            self.mutation_supplier.reset_mutations()

            # Save performance by only updating total score every 50 generations
            if not self_repair and i % 50 == 0:
                # Describe progress
                current_best.update_score()
                pbar.set_description(
                    f"{process_id}: {type(self).__name__} ({type(self.mutation_supplier).__name__}) (score: {current_best.score})"
                )

            # Track progress
            generations = i
            track_scores.append(current_best.score)  # type: ignore
            # if current_best.score > last_score:
            #     pass
            timestamps.append(time.time() - start_time)
        pbar.close()

        if self.verbose:
            # Output results to console
            print(
                f"\nBest score: {current_best.score} \
                \nIterations: {generations} \t solved: {current_best.check_solved()} \
                \nScore vector: {current_best.score_vector}"
            )

        if save_result:
            # Dump results
            strategy_name = self.mutation_supplier.__class__.__name__
            current_best.update_score()
            score = current_best.score

            arguments = copy.deepcopy(self.__dict__)
            del arguments["population"]
            del arguments["students_input"]
            del arguments["rooms_input"]
            del arguments["courses_input"]

            setattr(current_best, "_solve_arguments", arguments)
            dump_result(
                [track_scores, timestamps],
                f"output/genetic_{strategy_name}_score_{score}_scorestime_{generations}_",
            )
            output_path = dump_result(current_best, f"output/genetic_{strategy_name}_{score}_{generations}_")
            if self.verbose:
                print(f"Saved at {output_path}")

        if plot:
            # Show score over time/iterations
            plt.plot(timestamps, track_scores)
            plt.xlabel("Time (s)")
            plt.ylabel("Score")
            plt.show()

        return current_best
