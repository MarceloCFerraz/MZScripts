import concurrent.futures

from fixPackageAddresses import main
from utils import packages, utils

PACKAGES = []


def fill_packages_list(env, orgId, keyType, key):
    pkgs = packages.get_package_details(env, orgId, "pi", pid)

    for pkg in pkgs:
        PACKAGES.append(pkg)


pids = [
    "37ebc416-2105-42a1-b576-644402ad3234",
    "d01d5031-4eec-4943-9d9a-41ee6146cedf",
    "2d908305-953b-41c9-9846-3863356d78d6",
    "a26ea5cd-b3de-4ae2-a2dd-6b937b8c7b81",
    "cf994444-1baa-4827-b85d-b7bc6fe81bf0",
    "583b47f1-3e89-42d2-85da-d1eb3974fea7",
    "7ee313b9-27ac-4ff6-88e4-c52b058de20a",
    "c67a32c3-3128-4d9e-8456-9c3bf8d91dd2",
    "6fef3807-bcfa-4d38-9b8b-4304a3afcf98",
    "ecc2b503-ea6e-4873-9126-c1fb404390ab",
    "e0909ef4-2289-4770-bac4-ad2e73c997f6",
    "f25ca1c8-b0b6-463f-a063-3d20919f15a6",
    "050ab9b4-4de0-4ad8-b677-e9a5705d9023",
    "8beccf13-20c1-4f66-8387-ee2ccd293080",
    "9b0d053f-3b29-4562-99fd-30eadfbc345c",
    "b3c6cf52-4e4f-462d-85e2-212cae31fb62",
    "ccbf4d03-6c8c-4b13-adf4-b0c04e04d392",
    "b2b170f9-4c34-4dd4-b50c-5312d8887cb5",
    "91ab8823-f46d-44fc-a06a-2e370183ab82",
    "3d0535c5-a19d-40e6-a2da-aa7e12f8c96a",
    "fce95422-bdaf-458f-bccc-ff36ce7c9bfb",
    "1e68bef4-0b3c-4a98-8a16-75f96fff9985",
    "9d27ac33-c66b-443f-92a9-685b25273743",
    "3379f99e-d18f-45c3-a16d-6eaeec49ee70",
    "18187a3a-85f3-4b26-89ac-98971b0d0aa8",
    "6fd206a6-341a-47fc-8247-8ad4f68b2dd8",
    "3231854b-c9d2-4011-8692-b423d1c8a66f",
    "cd303d75-6b72-44b2-b890-761f8757f8c4",
    "3cf4af1e-9f26-42ab-aa5f-e3390569dabb",
    "b1af298c-9177-4cb4-9687-9d85fab013a9",
    "db210c74-e637-4614-9b99-76462c061fb7",
    "dde5878a-84bb-4839-8e46-9862a97a8c91",
    "9d39b02c-3553-40e2-97d1-7282db626050",
    "96c0df35-31e9-43fe-9e5c-b45c012c165f",
    "9d578c9a-59de-4209-bad4-9fd4b20967d1",
    "ea4ab416-432c-447f-8bc7-de3d7707ce3a",
    "971ff778-bf64-45b7-87e9-e4b2a3a4e183",
    "6fa1057d-8d25-44bf-835e-0f90cbdc9232",
    "f5885d6c-548e-495e-9053-00ee2e203081",
    "a7089f3c-1fad-4097-9975-b96be2fdaf23",
    "bf245ffa-3fbe-4682-869f-84565bc2ea05",
    "3906c9be-29a5-4a1e-b58e-4228926a8794",
]

env = utils.select_env()
orgId = utils.select_org(env)

with concurrent.futures.ThreadPoolExecutor(8) as pool:
    for pid in pids:
        pool.submit(fill_packages_list, env, orgId, "pi", pid)
        hubName = ""
pool.shutdown(wait=True)

with concurrent.futures.ThreadPoolExecutor(8) as pool:
    for package in PACKAGES:
        hubName = packages.get_package_hub(package)

        if hubName is not None:
            pool.submit(main, env, orgId, package["packageId"], hubName)

pool.shutdown(wait=True)
