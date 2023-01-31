import warnings

from ..classes import Schedule, Timeslot, dump_result
from .generate import generate_solutions
from .randomizer import Randomizer
from .mutator import Mutator
from .mutationsuppliers import MutationSupplier, DirectedSA, SimulatedAnnealing, HillClimber, Mutation
from ..classes.result import Result
import copy
from tqdm import tqdm
import matplotlib
import numpy as np

import matplotlib.pyplot as plt

import time
import multiprocessing


# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolver(Mutator):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        population_size=5,
        max_generations=30000,
        method="uniform",
        mutation_supplier: MutationSupplier = SimulatedAnnealing(),
        verbose=False,
    ) -> None:
        self.students_input = students_input
        self.courses_input = courses_input
        self.rooms_input = rooms_input

        self.population_size = population_size
        self.max_generations = max_generations

        self.method = method
        self.mutation_supplier = mutation_supplier

        self.verbose = verbose

    def fitness(self, score: float | int):
        """Get fitness of a result."""
        return 10000 / (1 + score)

    def solve(
        self,
        schedule_seed: Schedule | None = None,
        i_max: int | None = None,
        self_repair=False,
        show_progress=True,
        save_result=True,
        plot=True,
    ):
        # TODO: hillclimber for first part, then simulated annealing for second part? Forget swapping timeslots third part

        process_id = multiprocessing.current_process()._identity[0]

        if i_max is None:
            i_max = self.max_generations

        # Initialize population from prototype
        if schedule_seed is None:
            self.population = generate_solutions(
                Randomizer(self.students_input, self.courses_input, self.rooms_input, method=self.method),
                n=self.population_size,
                compress=True,
                show_progress=False,
            )
        else:
            self.population = [Result(copy.deepcopy(schedule_seed)).compress() for i in range(self.population_size)]

        population_sorted: list[Result] = self.sort_objects(self.population, "score")  # type: ignore
        current_best: Result = population_sorted[0].decompress(
            self.students_input, self.courses_input, self.rooms_input
        )
        backup_edges = copy.deepcopy(current_best.schedule.edges)

        start_time = time.time()
        best_fitness = 0
        best_score = None
        track_scores: list[float] = []
        timestamps = []
        generations = 0
        # TODO: in a loop: crossover, mutate, select best fit and repeat
        pbar = tqdm(range(i_max), position=process_id, leave=False, disable=not show_progress)
        for i in pbar:
            # last_score = current_best.score

            # Check if solution is found
            if current_best.score == 0:
                break

            if self_repair and self.fitness(current_best.score) > best_fitness and current_best.check_solved():
                backup_edges = copy.deepcopy(current_best.schedule.edges)
                best_score = current_best.score
                best_fitness = self.fitness(best_score)

            # Get suggestion for possible mutation
            mutation: Mutation = self.mutation_supplier.suggest_mutation(current_best)

            # Apply mutation
            mutation.apply()

            # Check if mutation is better
            if self_repair and not current_best.check_solved():
                # If better, keep mutation, else revert
                # TODO execute inverse of mutation for any mutation
                current_best = Result(Schedule(self.students_input, self.courses_input, self.rooms_input, backup_edges))
                # self.mutation_supplier.tried_timeslot_swaps.add(swapped_ids)
                continue

            #  Clear memory of swaps because of new schedule
            self.mutation_supplier.reset_mutations()

            # Save performance by only updating total score every 50 generations
            if not self_repair and i % 50 == 0:
                current_best.update_score()

                # Describe progress
                pbar.set_description(
                    # f"{type(self).__name__} ({type(self.mutation_supplier).__name__}) (score: {current_best.score}) (best swap memory {len(self.mutation_supplier.swap_scores_memory) } tried swaps memory {len(self.mutation_supplier.tried_timeslot_swaps) })"
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
            # Show score over time
            plt.plot(timestamps, track_scores)
            plt.xlabel("Time (s)")
            plt.ylabel("Score")
            plt.show()

        return current_best
