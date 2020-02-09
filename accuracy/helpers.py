import csv
import pathlib
import numpy as np
from pyssa.results import Results

# TODO: see if we want to use this
# CURR_DIR = pathlib.Path(__file__).parent
# DATA_DIR = CURR_DIR.parent / "data"


def read_results(test_id: str):
    """
        Read the simulation results used for accuracy tests.

        Parameters
        ----------
        test_id: str
            The index of the test number to return the results of.

        Returns
        -------
        time_list: List[float]
            Time points at which species amounts are analytically predicted.
        mu_list: List[float]
            Time course of the analytically predicted species amount means.
        std_list: List[float]
            Time course of the analytically predicted species amount standard
            deviations.

        See Also
        --------
        read_results_2sp: Read results for 2 species.

        Notes
        -----
        The accuracy tests are taken from the SBML Test Suite [1]_ .

        References
        ----------
        .. [1] https://github.com/sbmlteam/sbml-test-suite/tree/master/cases/stochastic
    """
    filename = f"data/results_{test_id}.csv"
    time_list = []
    mu_list = []
    std_list = []
    with open(filename) as fid:
        csv_reader = csv.reader(fid, delimiter=",")
        next(csv_reader)
        for time, mu, std in csv_reader:
            time_list.append(float(time))
            mu_list.append(float(mu))
            std_list.append(float(std))
    return time_list, mu_list, std_list


def read_results_2sp(test_id: str):
    """
        Read the simulation results used for accuracy tests when 2 species
        are tracked.

        Parameters
        ----------
        test_id: str
            The index of the test number to return the results of.

        Returns
        -------
        time_list: List[float]
            Time points at which species amounts are analytically predicted.
        mu_list: List[float]
            Time course of the analytically predicted species amount means.
        std_list: List[float]
            Time course of the analytically predicted species amount standard
            deviations.

        See Also
        --------
        read_results: Read results for one species.

        Notes
        -----
        The accuracy tests are taken from the SBML Test Suite [1]_ .

        References
        ----------
        .. [1] https://github.com/sbmlteam/sbml-test-suite/tree/master/cases/stochastic
    """
    filename = f"data/results_{test_id}.csv"
    time_list = []
    mu_list = []
    std_list = []
    with open(filename) as fid:
        csv_reader = csv.reader(fid, delimiter=",")
        next(csv_reader)
        for time, mu1, mu2, std1, std2 in csv_reader:
            time_list.append(float(time))
            mu_list.append(np.array([float(mu1), float(mu2)]))
            std_list.append(np.array([float(std1), float(std2)]))
    return time_list, mu_list, std_list


def calculate_zy(res: Results, time_list: list, mu_list: list, std_list: list):
    z_list = []
    y_list = []
    n_rep = len(res.t_list)
    for ind1, t in enumerate(time_list[1:]):
        results = res.get_state(t)
        mu_obs = np.mean(results)
        std_obs = np.std(results)
        z_list.append(
            np.sqrt(n_rep) * (mu_obs - mu_list[ind1 + 1]) / std_list[ind1 + 1]
        )
        y_list.append(
            np.sqrt(n_rep / 2) * ((std_obs ** 2) / (std_list[ind1 + 1] ** 2) - 1)
        )
        # print(f"From zy : ind={ind1}, t={t}, (mu_data, mu_obs, z, denom, num) = ({mu_list[ind1+1]}, {mu_obs}, {z_list[-1]:.2f}, {std_list[ind1+1]}, {np.sqrt(n_rep):.2f})")
    return np.array(z_list), np.array(y_list)


def calculate_zy_2sp(res: Results, time_list: list, mu_list: list, std_list: list):
    z_list = []
    y_list = []
    n_rep = len(res.t_list)
    for ind1, t in enumerate(time_list[1:]):
        results = res.get_state(t)
        mu_obs = np.mean(results, axis=0)
        std_obs = np.std(results, axis=0)
        # print("While calculating zy, : ", ind1, t, results, mu_obs, mu_list[ind1+1], std_obs, std_list[ind1+1])
        z_list.append(
            np.sqrt(n_rep) * (mu_obs - mu_list[ind1 + 1]) / std_list[ind1 + 1]
        )
        y_list.append(
            np.sqrt(n_rep / 2) * ((std_obs ** 2) / (std_list[ind1 + 1] ** 2) - 1)
        )
    return np.array(z_list), np.array(y_list)


def get_highest_rep_in_path(this_path: str):
    p = pathlib.Path(this_path)
    file_list = list(p.iterdir())
    highest_rep = len(file_list)
    print(f"{highest_rep} reps detected, returning results from all.")
    return highest_rep


def process_r(model="00001", library="GillespieSSA", algo="direct", n_reps=None):
    x_list = []
    t_list = []
    status_list = []
    sim_seeds = []
    res_folder = f"results/{model}/{library}_{algo}/"
    if n_reps is None:
        n_reps = get_highest_rep_in_path(res_folder)

    for rep_no in range(1, n_reps + 1):
        contents = np.loadtxt(res_folder + f"{rep_no}.csv", delimiter=",")
        t_list.append(contents[:, 0])
        this_x = contents[:, 1]
        this_x = this_x.reshape(len(this_x), 1)
        x_list.append(this_x)
        status_list.append(0)
        sim_seeds.append(0)
    res = Results(t_list, x_list, status_list, algo, sim_seeds)
    return res


def process_r_2sp(model="00030", library="GillespieSSA", algo="direct", n_reps=None):
    x_list = []
    t_list = []
    status_list = []
    sim_seeds = []
    res_folder = f"results/{model}/{library}_{algo}/"
    if n_reps is None:
        n_reps = get_highest_rep_in_path(res_folder)

    for rep_no in range(1, 10):
        contents = np.loadtxt(res_folder + f"{rep_no}.csv", delimiter=",")
        t_list.append(contents[:, 0])
        this_x = contents[:, 1:]
        x_list.append(this_x)
        status_list.append(0)
        sim_seeds.append(0)
    res = Results(t_list, x_list, status_list, algo, sim_seeds)
    return res