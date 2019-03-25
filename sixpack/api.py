from models import Experiment, Alternative, Client
from config import CONFIG as cfg


def participate(api_key, experiment, alternatives, client_id,
    force=None,
    traffic_fraction=None,
    prefetch=False,
    datetime=None,
    redis=None):

    exp = Experiment.find_or_create(api_key, experiment, alternatives, traffic_fraction=traffic_fraction, redis=redis)

    alt = None
    if force and force in alternatives:
        alt = Alternative(force, exp, redis=redis)
    elif not cfg.get('enabled', True):
        alt = exp.control
    elif exp.winner is not None:
        alt = exp.winner
    else:
        client = Client(client_id, redis=redis)
        alt = exp.get_alternative(client, dt=datetime, prefetch=prefetch)

    return alt


def convert(api_key, experiment, client_id,
    kpi=None,
    datetime=None,
    redis=None):

    exp = Experiment.find(api_key, experiment, redis=redis)

    if cfg.get('enabled', True):
        client = Client(client_id, redis=redis)
        alt = exp.convert(client, dt=datetime, kpi=kpi)
    else:
        alt = exp.control

    return alt


def client_experiments(api_key, client_id,
                       kpi=None, redis=None,
                       exclude_paused=True,
                       exclude_archived=True):
    client = Client(client_id, redis=redis)
    alternatives = []
    running_experiments = Experiment.all(api_key, redis=redis,
                                         exclude_paused=exclude_paused,
                                         exclude_archived=exclude_archived)
    for experiment in running_experiments:
        alternatives.append(experiment.get_alternative(client))
    return alternatives


def experiment_user_alternatives(api_key, experiment,
                                 redis=None, start=1, end=5000):
    user_alternatives = experiment.client_alternatives(start, end)
    return user_alternatives
