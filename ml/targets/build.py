from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.targets.activity import (
    create_activity_targets,
)

from ml.targets.behavioral import (
    create_behavioral_targets,
)

from ml.targets.events import (
    create_event_targets,
)

from ml.targets.financial import (
    create_financial_targets,
)

from ml.targets.health import (
    create_health_targets,
)

from ml.targets.location import (
    create_location_targets,
)

from ml.targets.patterns import (
    create_pattern_targets,
)

from ml.targets.travel import (
    create_travel_targets,
)


def build_target_dataset():
    """
    Build the final machine-learning target dataset.

    Pipeline:

        Database
            ↓
        Data Preparation
            ↓
        Target Engineering
            ↓
        Final Target Dataset
    """

    prepared_data = get_prepared_dataset()

    target_dataset = []

    for row in prepared_data:

        targets = {
            'Date': row['Date'],
        }

        targets.update(
            create_activity_targets(row)
        )

        targets.update(
            create_behavioral_targets(row)
        )

        targets.update(
            create_event_targets(row)
        )

        targets.update(
            create_financial_targets(row)
        )

        targets.update(
            create_health_targets(row)
        )

        targets.update(
            create_location_targets(row)
        )

        targets.update(
            create_pattern_targets(row)
        )

        targets.update(
            create_travel_targets(row)
        )

        target_dataset.append(targets)

    return target_dataset