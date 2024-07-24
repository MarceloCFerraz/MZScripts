from concurrent.futures import ThreadPoolExecutor

from utils import fleets, hubs, utils

nodes = []


def get_hubs(env: str, org_id: str, hubs_ids: list[str]) -> None:
    with ThreadPoolExecutor() as pool:
        for hub_id in hubs_ids:
            pool.submit(get_hub, env, org_id, hub_id)

    pool.shutdown(wait=True)


def get_hub(env: str, org_id: str, hub_id: str) -> None:
    hub = hubs.get_hub_config(env, org_id, hub_id)

    if hub:
        nodes.append(hub)


def main(env, org_id, fleet_id):
    hub_ids = fleets.get_hubs_from_fleet(env, org_id, fleet_id)
    get_hubs(env, org_id, hub_ids)

    print(f"Found {len(nodes)} hubs")

    for hub in nodes:
        # print(hub)
        print(f"{hub['hubName']} - {hub['hubId']}")


if __name__ == "__main__":
    env = utils.select_env()
    org_id = utils.select_org(env)
    fleet_id = input("Type the fleet ID: ")

    main(env, org_id, fleet_id)
