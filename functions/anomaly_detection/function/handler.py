import constants
from cognite.air import AIRClient
from cognite.air.alert_utils import AlertCreator
from cognite.air.ts_utils import current_time_in_ms
from cognite.air.utils import is_string_truthy
from helpers import run

OVERLAP = int(12 * 3600 * 1e3)


def handle(data, client, secrets):
    print(data)  # helpful for debugging
    air_client = AIRClient(data, client, secrets, debug=True)
    # retrieve fields from front end
    time_series = air_client.retrieve_field("time_series")
    if time_series.first() is None:
        print(f"Time Series {time_series.external_id} has no data points.")
        return ()
    std_sensitivity, time_frame_RA = air_client.retrieve_fields(["sensitivity", "time_frame"])
    long_term_interval, short_term_interval, std_threshold = retrieve_std_interval(time_frame_RA, std_sensitivity)

    end: int = current_time_in_ms()  # now
    ac = AlertCreator(
        air_client,
        constants.MERGE_PERIOD_IN_MS,
        constants.MIN_LENGTH_OF_ALERTS,
        constants.MAX_LENGTH_OF_ALERTS,
        constants.ALERT_WINDOW,
    )

    if air_client.backfilling.in_progress:
        if not is_string_truthy(data.get("backfilling")):
            print("Call from schedule but should be backfilled first")
            return ()
        first_timestamp = time_series.first().timestamp  # type: ignore
        end = air_client.backfilling.latest_timestamp or first_timestamp
        end += constants.BACKFILLING_WINDOW_SIZE
        for i in range(constants.BACKFILL_RUNS):
            if end - constants.BACKFILLING_WINDOW_SIZE > current_time_in_ms():
                air_client.backfilling.mark_as_completed()
                break
            end = run(
                client,
                ac,
                time_series,
                end,
                constants.BACKFILLING_WINDOW_SIZE,
                long_term_interval,
                short_term_interval,
                std_threshold,
            )
            air_client.backfilling.update_latest_timestamp(end)
            end += constants.BACKFILLING_WINDOW_SIZE
    else:
        run(
            client,
            ac,
            time_series,
            end,
            constants.WINDOW_SIZE_MS,
            long_term_interval,
            short_term_interval,
            std_threshold,
        )


def retrieve_std_interval(time_frame_RA, std_sensitivity):

    # fixing potential spelling errors - we will remove this after dropdown menu is added to AIR
    if time_frame_RA.strip() in ("VS", "vs", "Vs", "vS"):
        time_frame_RA = "VS"
    elif time_frame_RA.strip() in ("S", "s"):
        time_frame_RA = "S"
    elif time_frame_RA.strip() in ("M", "m"):
        time_frame_RA = "M"
    else:
        time_frame_RA = "L"

    if std_sensitivity.strip() in ("H", "h"):
        std_sensitivity = "H"
    elif std_sensitivity.strip() in ("M", "m"):
        std_sensitivity = "M"
    else:
        std_sensitivity = "L"

    # assign values based on front end selections:
    if time_frame_RA == constants.INTERVAL_NAMES[0]:  # very short term
        long_term_interval = constants.LONG_TERM_INTERVAL[0]
        short_term_interval = constants.SHORT_TERM_INTERVAL[0]
    elif time_frame_RA == constants.INTERVAL_NAMES[1]:  # short term
        long_term_interval = constants.LONG_TERM_INTERVAL[1]
        short_term_interval = constants.SHORT_TERM_INTERVAL[1]
    elif time_frame_RA == constants.INTERVAL_NAMES[2]:  # medium term
        long_term_interval = constants.LONG_TERM_INTERVAL[2]
        short_term_interval = constants.SHORT_TERM_INTERVAL[2]
    else:  # long term
        long_term_interval = constants.LONG_TERM_INTERVAL[3]
        short_term_interval = constants.SHORT_TERM_INTERVAL[3]

    if std_sensitivity == constants.THRESHOLD_NAMES[0]:  # low
        std_threshold = constants.STD_THRESHOLDS[0]
    elif std_sensitivity == constants.THRESHOLD_NAMES[1]:  # medium
        std_threshold = constants.STD_THRESHOLDS[1]
    else:  # high
        std_threshold = constants.STD_THRESHOLDS[2]
    return long_term_interval, short_term_interval, std_threshold