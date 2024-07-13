package utils

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"MZScripts/golang/utils/colors"
)

type utils struct {
	Orgs Orgs
	Envs []string
}

type Orgs struct {
	Prod  map[string]string `json:"PROD"`
	Stage map[string]string `json:"STAGE"`
	Integ map[string]string `json:"INTEG"`
}

func Initialize(i *colors.Input) utils {
	data := []byte(`{
		"PROD": {
			"CLM": "8a9e84be-9874-4346-baab-26053d35871e",
			"STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
			"HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
			"EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
			"CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
			"SHOPRITE-MM": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
			"SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
			"LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4"
		},
		"STAGE": {
			"CLM": "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
			"STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
			"HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
			"EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
			"CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
			"SHOPRITE-MM": "46474980-b149-4779-b9b5-76ea3d7baa90",
			"SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911"
		},
		"INTEG": {
			"HN": "1aaae948-7cbc-4fc2-9cbf-8e17fe8c1457",
			"EDG": "2c221bfd-1a58-4494-b2b5-20dc2407acd9",
			"M3": "1bdc25a0-d75e-4f9e-a648-e16af9d2f5f6",
			"CLM": "33d7ccef-e43e-4e1c-940a-a9120b504888",
			"CUBPHARMA": "93e0eee5-50e6-4200-86cf-1ab48303bb15",
			"SHOPRITE-MM": "44cf45b0-18f7-4f68-a43f-28fbeee9f8f9",
			"SHOPRITE": "c5ad97fe-db54-4522-a166-2ad3e0a85edb"
		}
	}`)
	utils := utils{
		Envs: []string{"PROD", "STAGE", "INTEG"}, // initializing an empty array of 3 items. Add more or remove as necessary, but also change the env definition below
	}

	if err := json.Unmarshal(data, &utils.Orgs); err != nil {
		i.Text = "Could not initialize Orgs. Check error below."
		i.FontColor = colors.Red
		i.Bold = true
		fmt.Println(i.Paint())
		panic(err)
	}

	return utils
}

func (u *utils) SelectEnv(input *colors.Input) string {
	input.Text = "Select one of the Envs:"
	input.FontColor = colors.Green

	fmt.Println(input.Paint())
	var option int

	for {
		input.FontColor = colors.Green
		input.Bold = false

		for i, env := range u.Envs {
			input.Text = fmt.Sprintf("> (%d) %s", i, env)
			fmt.Println(input.Paint())
		}

		fmt.Print("> ")
		if _, err := fmt.Scanf("%d", &option); err == nil && option >= 0 && option < len(u.Envs) {
			fmt.Println()
			input.Reset()
			return u.Envs[option]
		}

		input.Text = "Type a valid number"
		input.FontColor = colors.Red
		input.Bold = true

		fmt.Println(input.Paint())
	}
}

func (u *utils) SelectOrg(input *colors.Input, envs ...string) string {
	var env, orgName, orgId string
	input.FontColor = colors.Green

	length := len(envs)

	input.Text = fmt.Sprintf("%d arguments provided:", length)
	fmt.Println(input.Paint())

	for i, val := range envs {
		switch i {
		case 0:
			env = val
		case 1:
			orgName = strings.ToUpper(val)
		default:
			input.FontColor = colors.Red
			input.Text = fmt.Sprintf("Unexpected Arg: %s", val)
			fmt.Println(input.Paint())
		}
	}

	input.Bold = true
	input.FontColor = colors.Red

	switch length {
	case 0:
		input.Text = "No arguments provided, can't determine which orgId to pick. Quitting now"

		fmt.Println(input.Paint())
		os.Exit(1)
	case 1:
		orgId = getOrgFromUser(env, u)
	case 2:
		orgId = getOrgFromArgs(env, orgName, u)
	default:
		input.Text = "More than 2 arguments were provided. Please check them above and review your code or add more support to them"

		fmt.Println(input.Paint())
		os.Exit(1)
	}

	return orgId
}

func getOrgFromUser(env string, u *utils) string {
	fmt.Println("Select one of the Orgs:")

	var envMap map[string]string

	switch env {
	default: // defaults to PROD
		envMap = u.Orgs.Prod
	case "STAGE":
		envMap = u.Orgs.Stage
	case "INTEG":
		envMap = u.Orgs.Integ
	}

	keys := make([]string, 0, len(envMap))
	for key := range envMap {
		fmt.Printf("> %s\n", key)
		keys = append(keys, key)
	}

	for {
		fmt.Print("> ")
		var option string

		if _, err := fmt.Scanf("%s", &option); err == nil {
			option = strings.ToUpper(option)

			if Contains(&keys, &option) {
				value, ok := envMap[option]

				if ok {
					fmt.Println()
					return value
				}
			}
		}

		fmt.Print("Please select a valid option! Press Enter to continue\n\n")
		fmt.Scanln()
	}
}

func getOrgFromArgs(env, orgName string, u *utils) string {
	var id string
	var present bool

	if orgName != "" && containsOrgName(orgName, u) {
		switch strings.ToUpper(env) {
		default: // defaults to PROD
			id, present = u.Orgs.Prod[orgName]

			if !present {
				panic(fmt.Sprintf("%s does not exist in PROD\n", orgName))
			}
		case "STAGE":
			id, present = u.Orgs.Stage[orgName]

			if !present {
				panic(fmt.Sprintf("%s does not exist in STAGE\n", orgName))
			}
		case "INTEG":
			id, present = u.Orgs.Integ[orgName]

			if !present {
				panic(fmt.Sprintf("%s does not exist in INTEG\n", orgName))
			}
		}
	}

	return id
}

func SelectOption(options *[]string) int64 {
	fmt.Println("Please select one of the options below:")

	for {
		for i, option := range *options {
			fmt.Printf("> (%d): %s\n", i, option)
		}

		fmt.Print("> ")
		var opt int
		_, err := fmt.Scanf("%d", &opt)

		if err == nil && opt >= 0 && opt < len(*options) {
			return int64(opt)
		} else {
			fmt.Println("Error: ", err)
		}
		// fmt.Printf("Error: %s\n\n", err)
		fmt.Println("Type a valid option! Press enter to try again")
		fmt.Scanln()

	}
}

func Contains(slice *[]string, item *string) bool {
	for _, value := range *slice {
		if value == *item {
			return true
		}
	}
	return false
}

func containsOrgName(orgName string, u *utils) bool {
	_, existInProd := u.Orgs.Prod[orgName]
	_, existInStage := u.Orgs.Stage[orgName]
	_, existInInteg := u.Orgs.Integ[orgName]

	return existInProd || existInStage || existInInteg
}

func ConvertEnv(env *string) {
	*env = strings.ToLower(*env)

	if *env == "integ" {
		*env = "prod"
	}
}
