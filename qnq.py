#!/usr/bin/env python
from collections import defaultdict
import csv
import json
import numpy as np
import os
from enum import Enum
import argparse

from nltk.corpus import wordnet as wn
from textblob import TextBlob
# import epitran

# epi = epitran.Epitran('eng-Latn')
DATA_DIR = 'data'

exclusions = [wn.synset('axis.n.01'), wn.synset('point_source.n.01')]


def munge(s):
    blob = TextBlob(s)
    # TODO proper pluralisation using head nouns
    idx = -1
    for i, tag in enumerate(blob.tags):
        if tag[1] == 'IN':
            idx = i - 1
    blob.words[idx] = blob.words[idx].singularize().pluralize()
    return ' '.join(blob.words).title()


def prep(save=False):
    # TODO better source of place nouns
    location = [
        wn.synset('location.n.01'),
        wn.synset('building.n.01'),
        wn.synset('geological_formation.n.01'),
        wn.synset('land.n.02'),
        wn.synset('vegetation.n.01')
    ]
    hypo = lambda s: [x for x in s.hyponyms() if x not in exclusions]
    locs = list({
        z.replace('_', ' ')
        for x in location
        for y in x.closure(hypo)
        for z in y.lemma_names()
    })

    # with open(os.path.join(DATA_DIR, 'monsters.json'), 'r') as f:
    #     data = json.load(f)
    # names = [x['name'] for x in data]
    with open(os.path.join(DATA_DIR, 'kfc-monsters.csv'), 'r') as f:
        reader = csv.reader(f)
        names = [row[2] for row in reader][1:]

    locs = [munge(x) for x in locs]
    names = [munge(x) for x in names]

    # locs_ipa = [epi.transliterate(w) for w in locs]
    # names_ipa = [epi.transliterate(w) for w in names]

    dungeons = defaultdict(list)
    for i in range(len(locs)):
        dungeons[locs[i][0]].append(locs[i])

    dragons = defaultdict(list)
    for i in range(len(names)):
        dragons[names[i][0]].append(names[i])

    if save:
        with open(os.path.join(DATA_DIR, 'dungeons.json'), 'w+') as f:
            json.dump(dungeons, f)
        with open(os.path.join(DATA_DIR, 'dragons.json'), 'w+') as f:
            json.dump(dragons, f)

    return dungeons, dragons


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
    # dungeons, dragons = prep(save=True)
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
