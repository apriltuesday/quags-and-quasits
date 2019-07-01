#!/usr/bin/env python
import json
import numpy as np
import os
from enum import Enum
import argparse


DATA_DIR = 'data'


class SamplingMode(Enum):
    DUNGEONS = 1
    DRAGONS = 2
    DUNGEONSANDDRAGONS = 3


def sampler(n, letter, mode):
    with open(os.path.join(DATA_DIR, 'dungeons.json'), 'r') as f:
        dungeons = json.load(f)
    with open(os.path.join(DATA_DIR, 'dragons.json'), 'r') as f:
        dragons = json.load(f)

    if not letter:
        options = list(set(dungeons.keys()).intersection(dragons.keys()))
        probs = np.array(
            [len(dungeons[l]) + len(dragons[l]) for l in options],
            dtype='float64'
        )
        probs /= probs.sum()
        letter = np.random.choice(options, p=probs)
    else:
        letter = letter.upper()

    for _ in range(n):
        if mode == SamplingMode.DUNGEONSANDDRAGONS:
            dungeon = np.random.choice(dungeons[letter])
            dragon = np.random.choice(dragons[letter])
            yield f'{dungeon} and {dragon}'
        if mode == SamplingMode.DUNGEONS:
            dungeon = np.random.choice(dungeons[letter])
            yield f'{dungeon}'
        if mode == SamplingMode.DRAGONS:
            dragon = np.random.choice(dragons[letter])
            yield f'{dragon}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Alliterate quags & quasits')
    parser.add_argument('number', type=int, nargs='?', default=10,
                        help='number of alliterations to produce')
    parser.add_argument('--letter', '-l', metavar='l', dest='letter',
                        help='letter to choose (default: random letter)')
    parser.add_argument('--dungeons', action='store_true', help='dungeons only')
    parser.add_argument('--dragons', action='store_true', help='dragons only')

    args = parser.parse_args()
    if args.dungeons:
        mode = SamplingMode.DUNGEONS
    elif args.dragons:
        mode = SamplingMode.DRAGONS
    else:
        mode = SamplingMode.DUNGEONSANDDRAGONS

    for x in sampler(args.number, args.letter, mode):
        print(x)
