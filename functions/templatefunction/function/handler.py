from cognite.air import AIRClient
from cognite.air.utils import is_string_truthy
from cognite.client.data_classes import Event


# Please add model code under the handle function
def handle(data, client, secrets):
    air_client = AIRClient(data, client, secrets)

    # retrieving fields specified in the config.yaml
    temperature_ts, pressure_ts = air_client.retrieve_fields(["temperature_ts", "pressure_ts"])

    # retrieve previous alerts
    model_output_alerts = air_client.events.list_alerts(limit=100)
    # retrieve previous events
    model_output_events = air_client.events.list(limit=100)
    print(f"Previous alerts: {len(model_output_alerts)}; previous events: {len(model_output_events)}")

    latest_temperature_value = client.datapoints.retrieve_latest(external_id=temperature_ts.external_id)
    latest_pressure_value = client.datapoints.retrieve_latest(external_id=pressure_ts.external_id)

    # configure backfilling
    if air_client.backfilling.in_progress:
        if not is_string_truthy(data.get("backfilling")):
            print("Call from schedule but should be backfilled first")
            return ()
        # backfilling code
        pass

    # none backfilling code:
    if latest_temperature_value.value[0] > 100 and latest_pressure_value.value[0] > 4:
        air_client.events.create_alert(
            Event(
                description="Alert!",
                metadata={"notification_message": "Something bad happened!"},  # send message in email
            )
        )
    elif latest_temperature_value.value[0] > 100 or latest_pressure_value.value[0] > 4:
        air_client.events.create(Event(description="Not so bad yet!"))
