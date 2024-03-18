package utils

import (
	"fmt"
	"strings"
)

type utils struct {
	Orgs map[string]interface{}
	Envs []string
}

func Initialize() utils {
	utils := utils{
		Orgs: map[string]interface{}{
			"PROD": map[string]string{
				"CLM":         "8a9e84be-9874-4346-baab-26053d35871e",
				"STAPLES":     "3c897e84-3957-4958-b54d-d02c01b14f15",
				"HN":          "c88987f9-91e8-4561-9f07-df795ef9b8f0",
				"EDG":         "ca3ffc06-b583-409f-a249-bdd014e21e31",
				"CUBPHARMA":   "706660ca-71f6-4c01-a9ff-3a480acebaf4",
				"SHOPRITE-MM": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
				"SHOPRITE":    "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
				"LOWES":       "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
			},
			"STAGE": map[string]string{
				"CLM":         "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
				"STAPLES":     "3e59b207-cea5-4b00-8035-eed1ae26e566",
				"HN":          "c88987f9-91e8-4561-9f07-df795ef9b8f0",
				"EDG":         "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
				"CUBPHARMA":   "6591e63e-6065-442d-87c3-20a5cd98cdba",
				"SHOPRITE-MM": "46474980-b149-4779-b9b5-76ea3d7baa90",
				"SHOPRITE":    "397190aa-18ab-4bef-a8aa-d5875d738911",
			},
			"INTEG": map[string]string{
				"HN":          "1aaae948-7cbc-4fc2-9cbf-8e17fe8c1457",
				"EDG":         "2c221bfd-1a58-4494-b2b5-20dc2407acd9",
				"CLM":         "33d7ccef-e43e-4e1c-940a-a9120b504888",
				"CUBPHARMA":   "93e0eee5-50e6-4200-86cf-1ab48303bb15",
				"SHOPRITE-MM": "44cf45b0-18f7-4f68-a43f-28fbeee9f8f9",
				"SHOPRITE":    "c5ad97fe-db54-4522-a166-2ad3e0a85edb",
			},
		},
		Envs: make([]string, 0, 3), // initializing an empty array of 3 items
	}

	for key := range utils.Orgs {
		utils.Envs = append(utils.Envs, key)
	}

	return utils
}

func (u *utils) SelectEnv() string {
	fmt.Println("Select one of the Envs:")
	var option int

	for {
		fmt.Printf("> ")
		for i, env := range u.Envs {
			fmt.Printf("(%d) %s\n> ", i, env)
		}

		if _, err := fmt.Scanf("%d", &option); err == nil && option >= 0 && option < len(u.Envs) {
			fmt.Println()
			return u.Envs[option]
		}

		fmt.Println("Type a valid number")
	}
}

func (u *utils) SelectOrg(env *string) string {
	fmt.Println("Select one of the Orgs:")

	for {
		fmt.Print("> ")

		// asserting that orgs[env] is a map of string: string
		// go can't loop over type interface{} so we're basically telling
		// it that this is not an empty interface
		if envMap, ok := u.Orgs[*env].(map[string]string); ok {
			keys := make([]string, 0, len(envMap))
			var option string

			for key := range envMap { // range returns key, value
				fmt.Printf("%s\n> ", key)
				keys = append(keys, key)
			}

			if _, err := fmt.Scanf("%s", &option); err == nil {
				option = strings.ToUpper(option)

				if Contains(&keys, &option) {
					value, ok := envMap[strings.ToUpper(option)]

					if ok {
						fmt.Println()
						return value
					}
				}
			}

			fmt.Print("Please select a valid option!\n\n")
		}
	}
}

func SelectOption(options *[]string) int {
	fmt.Println("Please select one of the options below:")

	for {
		for i, option := range *options {
			fmt.Printf("> (%d): %s\n", i, option)
		}

		fmt.Print("> ")
		fmt.Scanln()
		var opt int
		_, err := fmt.Scanf("%d", &opt)

		if err == nil && opt < len(*options) && opt >= 0 && opt < len(*options) {
			return opt
		}
		// fmt.Printf("Error: %s\n\n", err)
		fmt.Println("Type a valid option!")

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

func ConvertEnv(env *string) {
	*env = strings.ToLower(*env)

	if *env == "integ" {
		*env = "prod"
	}
}
