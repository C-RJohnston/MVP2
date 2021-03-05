import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from SIRS import SIRS
import pickle


def measure_infections():
    p1s = np.round(np.arange(0, 1, 0.05), 3)
    p3s = np.round(np.arange(0, 1, 0.05), 3)
    p2 = 0.5
    data = {p1: {p3: {'val': 0, 'var': 0} for p3 in p3s} for p1 in p1s}
    tasks = []
    with ProcessPoolExecutor() as e:
        for p1 in p1s:
            for p3 in p3s:
                S = SIRS((50, 50), p1, p2, p3)
                S.randomise(0)
                tasks.append(e.submit(S.measure_infections, 100, 1000))
        i = 0
        for f in as_completed(tasks):
            i += 1
            print(f"Completed {i}/{len(tasks)} measurements")
            inf, p1, p3 = f.result()
            av_inf = np.mean(inf)
            av_inf_squared = np.mean(np.power(inf, 2))

            data[p1][p3]['val'] = round(av_inf / S.size, 3)
            data[p1][p3]['var'] = round((av_inf_squared - av_inf) / S.size, 3)
    with open("SIRSMeasurements", 'wb') as outfile:
        pickle.dump(data, outfile)


if __name__ == "__main__":
    measure_infections()
