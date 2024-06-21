import requests, json, pprint

pp = pprint.PrettyPrinter(indent=2)

headers = {'content-type': 'application/json'}
create_area_url = "http://sortationservices.prod.milezero.com/SortationServices-war/api/area"

org_id = "3c897e84-3957-4958-b54d-d02c01b14f15"
node_name = "3389"

def post_area(template):
    response = requests.post(url=create_area_url, headers=headers, data=json.dumps(template))
    if response.status_code == 204:
        print("area " + template["areaName"] + " created")
        return
    else:
        print("area " + template["areaName"] + " NOT created")
        return
    

def create_areas():
    for x in range(99):
        if x < 10:
            areaName = "STAGE_0" + str(x)
        else:
            areaName = "STAGE_" + str(x)
        stage_template = {
            "orgId": org_id,
            "scNodeName": node_name,
            "areaName": areaName,
            "type": "STAGE",
            "mode": "MANUAL",
        }
        post_area(stage_template)

    names = {"REATTEMPT_MONDAY" : "MONDAY","REATTEMPT_TUESDAY" : "TUESDAY","REATTEMPT_WEDNESDAY" : "WEDNESDAY","REATTEMPT_THURSDAY" : "THURSDAY","REATTEMPT_FRIDAY" : "FRIDAY","REATTEMPT_SATURDAY" : "SATURDAY","REATTEMPT_SUNDAY" : "SUNDAY","RECEIVE_1" : "SORT","REATTEMPT_FAIL" : "REATTEMPT_FAIL","PROBLEM_SOLVE" : "PROBLEM_SOLVE","REJECT" : "REJECT","SHORT" : "SHORT","KICKOUT" : "KICKOUT","REDIRECT" : "REDIRECT","STAGE_HOLDING" : "STAGE"}
    for name,types in names.items():
        extra_template = {
            "orgId": org_id,	
            "scNodeName": node_name,
            "areaName": name,
            "type": types,
            "mode": "MANUAL",
        }
        post_area(extra_template)


if __name__ == '__main__':
    create_areas()