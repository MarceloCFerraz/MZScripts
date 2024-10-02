from concurrent.futures import ThreadPoolExecutor

from utils import packages, utils


def main(env: str, org_id: str, key_type: str, key: str, notes: str | None):
    pkgs = []

    pkgs = packages.get_package_details(env, org_id, key_type, key)

    if len(pkgs) == 0:
        print("> NO PACKAGES FOUND <\n")

    print(f"\n{'':=<50}")
    print(f"Found {len(pkgs)} packages, Applying filters")

    with ThreadPoolExecutor() as pool:
        for package in pkgs:
            status = package["packageStatuses"]["status"]
            package_id = package["packageId"]

            if status == "DELIVERED":
                print(f"--> Package {package_id} already delivered")
                continue

            pool.submit(
                packages.mark_package_as_delivered, env, org_id, package_id, notes
            )


if __name__ == "__main__":
    env = utils.select_env()
    org_id = utils.select_org(env)

    key = input(
        "Type in the package number (e.g. 0510220444761000002, 00000009370592381919): "
    )
    key_type = input("Type in the package number type (e.g. bc, ori, pi, etc): ")

    notes = input("Type in the notes (optional): ")

    main(env, org_id, key_type, key, notes if notes else None)
