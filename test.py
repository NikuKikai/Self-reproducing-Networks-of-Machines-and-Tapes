from typing import Dict, Tuple
import numpy as np
import random
from model import Machine, Tape


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


noise = 0.01
dm = 0.1    # remove rate of old machines
dt = 0.1    # remove rate of old tapes
N = 100     # capacity
c = 10      # new objects

machine_population = {}
tape_population = {}

# Init
machine_population[Machine.from_tape(Tape(1))] = 50
machine_population[Machine.from_tape(Tape(9))] = 50
tape_population[Tape(1)] = 40
tape_population[Tape(3)] = 50
tape_population[Tape(5)] = 20


for g in range(100):
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

    print(f'---- Generation {g} ----')
    for m in machine_population:
        print(f'M{m} population={machine_population[m]}')

