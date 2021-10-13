from cognite.air import AIRClient
from cognite.air.alert_utils import AlertCreator
from cognite.air.ts_utils import current_time_in_ms
from cognite.air.utils import is_string_truthy
from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries
from cognite.client.utils import ms_to_datetime

ALERT_WINDOW = int(12 * 3600 * 1e3)
WINDOW_SIZE_MS = int(12 * 3600 * 1e3)
BACKFILLING_WINDOW_SIZE = int(3 * 24 * 3600 * 1e3)
MERGE_PERIOD_IN_MS = int(10 * 60 * 1e3)
BACKFILLING_OFFSET = int(60 * 60 * 1e3)
MIN_SIZE_OF_OUTAGE = int(10 * 60 * 1e3)
MAX_LENGTH_OF_ALERT = int(12 * 3600 * 1e3)
BACKFILL_RUNS = 1500
MAX_EVENTS_TO_BE_PROCESSED = 1000
JP_DEMO_API_KEY = "ZWU3MTFjNGItNTVkZC00ODIxLWE1ZjEtMjY3NzlhNzcxMjY0"


def handle(data, client: CogniteClient, secrets):
    air_client = AIRClient(data, client, secrets, debug=True)
    print(data["schedule_asset_ext_id"])
    integration = is_string_truthy(data.get("integretation"))
    time_series: TimeSeries = air_client.retrieve_field("ts_ext_id")
    if time_series.is_string:
        return
    if time_series.first() is None:
        print(f"Time Series {time_series.external_id} has no data")
        if air_client.backfilling.in_progress:
            air_client.backfilling.mark_as_completed()
        return ()
    threshold: float = air_client.retrieve_field("threshold")
    min_length_of_alert: int = int(air_client.retrieve_field("min_minutes") * 60 * 1e3)

    ac = AlertCreator(air_client, MERGE_PERIOD_IN_MS, min_length_of_alert, MAX_LENGTH_OF_ALERT, ALERT_WINDOW)
    if air_client.backfilling.in_progress:
        if not is_string_truthy(data.get("backfilling")):
            print("Call from schedule but should be backfilled first")
            return ()
        # if backfilling is in progress either take latest_backfilling_timestamp or first events created time + 1min
        first_timestamp = time_series.first().timestamp  # type: ignore
        end = air_client.backfilling.latest_timestamp or first_timestamp
        end += BACKFILLING_WINDOW_SIZE
        for i in range(BACKFILL_RUNS):
            if end - BACKFILLING_WINDOW_SIZE > current_time_in_ms():
                air_client.backfilling.mark_as_completed()
                break
            end = run(
                client,
                ac,
                time_series,
                end,
                BACKFILLING_WINDOW_SIZE,
                threshold,
                integration,
            )
            air_client.backfilling.update_latest_timestamp(end)
            end += BACKFILLING_WINDOW_SIZE
    else:
        end = current_time_in_ms()
        run(
            client,
            ac,
            time_series,
            end,
            WINDOW_SIZE_MS,
            threshold,
            integration,
        )


def run(
    client: CogniteClient,
    alert_creator: AlertCreator,
    time_series: TimeSeries,
    end: int,
    window_size: int,
    threshold: float,
    integration: bool = False,
) -> int:
    dp = (
        client.datapoints.retrieve(
            id=time_series.id,
            start=end - window_size - BACKFILLING_OFFSET,
            end=end,
            aggregates=["max"],
            granularity="1m",
        )
        .to_pandas()
        .dropna()
    )
    #print(f"covered period from {ms_to_datetime(end-window_size)} until {ms_to_datetime(end)}")
    #print(f"length of data {0 if dp is None else len(dp)}")
    if dp.shape[0] == 0:
        return end

    notification_message = f"A threshold on the time series {time_series.name} has been breached (X > {threshold})."
    dp.columns = ["value"]
    dp["deviation"] = dp["value"] > threshold

    _, _, endpoint = alert_creator.create_alerts(
        dp[["deviation"]],
        end,
        notification_message,
        MAX_EVENTS_TO_BE_PROCESSED,
    )
    return endpoint