from utils.associates import get_associate_latest_itinerary
from utils.utils import select_env, select_org

if __name__ == "__main__":
    env = select_env()
    orgId = select_org(env)
    associate_id = input(">> Type the associate ID: ")

    data = get_associate_latest_itinerary(env, orgId, associate_id)
    for key in data.keys():
        print(f"{key:>>19}: {data[key]}")
