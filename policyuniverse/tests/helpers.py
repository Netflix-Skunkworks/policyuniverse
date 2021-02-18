from policyuniverse.statement import Mapping
from policyuniverse.common import Sequence


class CustomSequence(Sequence):
    def __init__(self, data):
        self._sequence = data

    def __getitem__(self, item):
        return self._sequence[item]

    def __len__(self):
        return len(self._sequence)


class CustomMapping(Mapping):
    def __init__(self, data):
        self._mapping = data

    def __getitem__(self, item):
        return self._mapping[item]

    def __len__(self):
        return len(self._mapping)

    def __iter__(self):
        return iter(self._mapping)
