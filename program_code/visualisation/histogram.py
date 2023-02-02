import numpy as np
import matplotlib.pyplot as plt
from ..classes.result import Result


def plot_histogram(results: list[Result]):
    """Plot histogram of result scores. Seperate plots per score dimension."""
    evening_timeslots = [result.score_vector[0] for result in results]
    student_overbookings = [result.score_vector[1] for result in results]
    gaps_1, gaps_2, gaps_3 = [[result.score_vector[i] for result in results] for i in range(2, 5)]
    total_scores = [result.score for result in results]

    fig, ax = plt.subplots(2, 3, figsize=(9, 4.5), tight_layout=True, sharex=True, sharey=False)

    axtot = ax[0, 0]  # type: ignore
    axtot.hist(total_scores, 100)
    axtot.set_title(f"Total score \n mean: ${np.mean(total_scores):.2f} ± {np.std(total_scores):.2f}$")

    axevn = ax[0, 1]  # type: ignore
    axevn.hist(evening_timeslots, 100)
    axevn.set_title(f"Evening timeslots \n mean: ${np.mean(evening_timeslots):.2f} ± {np.std(evening_timeslots):.2f}$")

    axconf = ax[0, 2]  # type: ignore
    axconf.hist(student_overbookings, 100)
    axconf.set_title(
        f"Course conflicts \n mean: ${np.mean(student_overbookings):.2f} ± {np.std(student_overbookings):.2f}$"
    )

    axg1 = ax[1, 0]  # type: ignore
    axg1.hist(gaps_1, 100)
    axg1.set_title(f"1 gap \n mean: ${np.mean(gaps_1):.2f} ± {np.std(gaps_1):.2f}$")

    axg1 = ax[1, 1]  # type: ignore
    axg1.hist(gaps_2, 100)
    axg1.set_title(f"2 gaps \n mean: ${np.mean(gaps_2):.2f} ± {np.std(gaps_2):.2f}$")

    axg1 = ax[1, 2]  # type: ignore
    axg1.hist(gaps_3, 100)
    axg1.set_title(f">2 gaps \n mean: ${np.mean(gaps_3):.2f} ± {np.std(gaps_3):.2f}$")

    plt.savefig("output/image.png")
    plt.show()
