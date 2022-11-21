from typing import Dict, Tuple
import numpy as np
import random
from model import Machine, Tape
from matplotlib import pyplot


def sample(population: dict, nsample: int = 1) -> list:
    ppl_sum = sum(population.values())
    idxs = list(np.random.randint(0, ppl_sum, size=nsample))
    idxs.sort()
    samples = []
    pacc = 0
    for m, p in population.items():
        if len(idxs) == 0:
            break
        pacc += p
        while len(idxs) > 0:
            if idxs[0] < pacc:
                samples.append(m)
                idxs.pop(0)
            else:
                break
    random.shuffle(samples)
    return samples


noise = 0.05
dm = 0.1    # remove rate of old machines
dt = 0.1    # remove rate of old tapes
N = 100     # capacity
c = 10      # new objects

machine_population = {}
tape_population = {}

# Init
# # M1002 T1 fixed point
# machine_population[Machine.from_tape(Tape(1))] = 50
# machine_population[Machine.from_tape(Tape(9))] = 50
# tape_population[Tape(1)] = 40
# tape_population[Tape(3)] = 50
# tape_population[Tape(5)] = 20

# random init
initial_ts = [random.randint(0, 127) for _ in range(10)]
for t in initial_ts:
    machine_population[Machine.from_tape(Tape(t))] = 10
tape_population[Tape(initial_ts[0])] = 10
tape_population[Tape(initial_ts[1])] = 10
tape_population[Tape(initial_ts[2])] = 10


# Log
mpops: Dict[str, list] = {}
tpops: Dict[str, list] = {}

def log(g: int):
    for m, p in machine_population.items():
        m_str = str(m)
        if m_str not in mpops:
            mpops[m_str] = []
        mpops[m_str].append((g, p))
    for t, p in tape_population.items():
        t_str = str(t)
        if t_str not in tpops:
            tpops[t_str] = []
        tpops[t_str].append((g, p))

log(0)

for g in range(200):
    if len(machine_population) == 0 or len(tape_population) == 0:
        break

    # Sample and reaction for c times
    ms = sample(machine_population, c)
    ts = sample(tape_population, c)
    new_ms, new_ts = [], []
    for m, t in zip(ms, ts):
        t_ = m.rewrite_tape(t, noise)
        if t_ is None:
            continue
        m_ = Machine.from_tape(t_)
        new_ms.append(m_)
        new_ts.append(t_)
    # Death
    for m in machine_population:
        machine_population[m] *= 1-dm
    for t in tape_population:
        tape_population[t] *= 1-dt

    # Add new
    for m in new_ms:
        if m not in machine_population:
            machine_population[m] = 0
        machine_population[m] += 1
    for t in new_ts:
        if t not in tape_population:
            tape_population[t] = 0
        tape_population[t] += 1

    # Clean <1 population
    for m in list(machine_population.keys()):
        if machine_population[m] < 1:
            machine_population.pop(m)
    for t in list(tape_population.keys()):
        if tape_population[t] < 1:
            tape_population.pop(t)

    # print(f'---- Generation {g} ----')
    # for m in machine_population:
    #     print(f'M{m} population={machine_population[m]}')
    log(g+1)


# Plot population history
pyplot.figure()
for m_str, pts in mpops.items():
    gs = [pt[0] for pt in pts]
    ps = [pt[1] for pt in pts]
    pyplot.plot(gs, ps, label=f'M{m_str}')
pyplot.legend()

pyplot.figure()
for t_str, pts in tpops.items():
    gs = [pt[0] for pt in pts]
    ps = [pt[1] for pt in pts]
    pyplot.plot(gs, ps, label=f'T{t_str}')
pyplot.legend()

pyplot.show()
