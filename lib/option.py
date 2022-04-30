

from dataclasses import dataclass, field
from typing import List


@dataclass
class Option:
    master_dir: str = 'var/master'
    master_start_trg: str = 'master_start.trg'
    master_end_trg: str = 'master_end.trg'
    common_feature_dir: str = 'var/feature'
    common_feature_trg: str = 'common_feature.trg'
    ticket_dir: str = 'var/tickets'
    market_feature_dir: str = 'var/markets'
    market_feature_trg: str = 'market_feature.trg'
    aiml_dir: str = 'var/aiml'
    aiml_trg: str = 'aiml.trg'
    workers: List[str] = field(default_factory=lambda: [
                               'one', 'two', 'three', 'four'])
