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


WEEK_DAYS = ["MA", "DI", "WO", "DO", "VR"]
ROOMS = ["A1.04", "A1.06", "A1.08", "A1.10", "B0.201", "C0.110", "C1.112"]  # col labels
PERIODS = ["9-11", "11-13", "13-15", "15-17", "17-19"]  # row labels
COLORS = ["pink", "lightgreen", "lightblue", "wheat", "salmon", "red", "yellow"]

# DEFINE CONSTANTS
WEEK_DAYS = ["MA", "DI", "WO", "DO", "VR"]
ROOMS = ["A1.04", "A1.06", "A1.08", "A1.10", "B0.201", "C0.110", "C1.112"]  # col labels
PERIODS = ["9-11", "11-13", "13-15", "15-17", "17-19"]  # row labels
COLORS = ["pink", "lightgreen", "lightblue", "wheat", "salmon", "red", "yellow"]


class Heatmap:
    def __init__(self, result: Result, i=0) -> None:
        schedule = result.schedule
        # timeslots in order of day - period - room
        self.timeslots = sorted(list(schedule.timeslots.values()), key=lambda x: x.moment)
        self.data = self._create_array(schedule)
        # self.timetableplot = self.timetable()
        self.heatmapview = self.plot_heatmap(i, score=result.score)

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
            # Let the horizontal axes labeling appear on top.
            ax[weekday_plot].tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

        for timeslot in self.timeslots:
            # full time table plot
            activity = list(timeslot.activities.values())[0]
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

        print(f"Timetable plot saved to {output_path}")
        plt.savefig(output_path, dpi=200)

    def heatmap(self, row_labels, col_labels, ax, cbarlabel="", **kwargs):
        """Creates heatmap with labels and colorbar"""
        # Initialize Axes, colorbar dictionary, colorbar label
        # ax = plt.gca()

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
        valfmt = matplotlib.ticker.StrMethodFormatter("{x}")

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

    def plot_heatmap(self, i=0, score: float = 0):
        output_path = f"output/heatmap_timetable_{i}.jpg"

        plt.rcParams["figure.figsize"] = [10, 3.50]
        plt.rcParams["figure.autolayout"] = True

        fig, ax = plt.subplots(figsize=(20, 5))
        ax.set_title(f"score = {score} \ni = {i}")

        im, cbar = self.heatmap(
            PERIODS, ROOMS * 5, ax, cmap="rainbow", vmin=0, vmax=25, cbarlabel="conflict [score/period]"
        )
        texts = self.annotate_heatmap(im, size=7)

        fig.tight_layout()
        # print(f"Heatmap saved to {output_path}")
        plt.savefig(output_path, dpi=200)
        plt.close()


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
        save_result=False,
    ):
        """
        TODO mark lower half of population for replacement
        TODO: define crossover
        TODO: define mutations
        TODO do different mutations, depending on highest conflict factor
        TODO: statistics of different methods
        TODO: statistics where most score increase comes from
        - TODO: hillclimber
        - TODO: recursive swapping function
        TODO: index on swaps already tried
        - TODO: simulated annealing PRIORITY
        - TODO: fix swapping function resulting in bad solution PRIORITY
        TODO:  define mutation on swapping students
        TODO: Track score over time
        - TODO: Sub score function per timeslot, only consider students involved with timeslot for much faster score difference calculation
        - TODO: Build population of mutations and take best score differences , steepest decent: number of mutations = decent scope
        - TODO: Simulated annealing

        - TODO: hillclimber for first part, then simulated annealing for second part? PRIORITY

        """

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
            if i > 2900 and i % 100 == 0:
                current_best.update_score()
                hm = Heatmap(current_best, i)

            last_score = current_best.score
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
            # print(f"Score: {current_best.score} \t Generation: {i + 1 }/{ self.max_generations}", end="\r")

            # Track progress
            generations = i
            track_scores.append(current_best.score)  # type: ignore
            if current_best.score > last_score:
                pass
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

        # Show score over time
        # plt.plot(timestamps, track_scores)
        # plt.xlabel("Time (s)")
        # plt.ylabel("Score")
        # plt.show()

        return current_best
