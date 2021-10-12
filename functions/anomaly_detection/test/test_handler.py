from cognite.client import CogniteClient
from cognite.client.data_classes.datapoints import Datapoints
from cognite.client.testing import monkeypatch_cognite_client


def test_handle():
    with monkeypatch_cognite_client():
        c = CogniteClient()
        c.datapoints.retrieve_latest.return_value = Datapoints(value=[5])
        handle(
            data={
                "sensor_11": "sensor_11",
                "anomaly_pc1": "anomaly_pc1"
            },
            client=c,
            secrets={},
        )

        handle(
            {
                "sensor_11": "sensor_11",
                "anomaly_pc1": "anomaly_pc1",
                "backfilling": "True",
            },
            client=c,
            secrets={},
        )
