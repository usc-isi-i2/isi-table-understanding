import re
import os

from pslpython.model import Model
from pslpython.partition import Partition
from pslpython.predicate import Predicate
from pslpython.rule import Rule

partition_map = {
    'obs': Partition.OBSERVATIONS,
    'targets': Partition.TARGETS,
    'truth': Partition.TRUTH,
}

def _normalize(filename):
    match = re.match(r'(\w+)_(obs|targets|truth)\.txt', filename)

    if (match is None):
        print("Data filename (%s) is malformed." % (filename))

        return None, None

    pred, partition = match.groups()

    return pred, partition

def write_rules(model: Model, rule_path: str):
    if rule_path is None:
        return

    with open(rule_path, 'w+') as file:
        for rule in model._rules:
            file.write(str(rule) + "\n")

def get_rules(model: Model, rule_path: str):

    with open(rule_path, "r") as f:
        for line in f:
            if line.startswith("//") or line.strip() == "":
                continue

            model.add_rule(Rule(line.strip()))

def add_data(model: Model, data_path: str):

    files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]

    for f in files:

        pred, ptype = _normalize(f)

        if pred is None or Predicate.normalize_name(pred) not in model._predicates:
            continue

        model.get_predicate(pred).add_data_file(partition_map[ptype],
                                                os.path.join(data_path, f))

def clean_model(model: Model):

    for predicate in model.get_predicates().values():

        predicate.clear_data()


def get_predicates(model: Model, psl_pred: str):
    with open(psl_pred, "r") as f:

        for pred in f:

            p = pred.strip().split()

            predicate = Predicate(p[0], closed = True if p[2] == "closed" else False,
                                  size=int(p[1]))

            model.add_predicate(predicate)
