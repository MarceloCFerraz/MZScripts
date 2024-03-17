package main

import (
	"github.com/MarceloCFerraz/MZScripts/utils"
)

func main() {
	// var json fastjson.Parser // or ParserPool
	utils := utils.Initialize()

	env := utils.SelectEnv()
	orgId := utils.SelectOrg(&env)

	// gazetteer_get_addresses := "https://gazetteer.{env}.milezero.com/gazetteer-war/api/location/matching/org/{org_id}"
	// lockbox_get_location := "https://lockbox.{env}.milezero.com/lockbox-war/api/location/{location_id}"
	// geocoder_get_geocode := "http://geocoder.{env}.milezero.com/gc/api/address?street={1}&city={2}&state={3}&zip_code={4}&cc=US&provider={5}"
	// lockbox_update_address := "https://lockbox.{env}.milezero.com/lockbox-war/api/location/{location_id}"
	// cromag_get_hub := "http://cromag.{convert_env(env)}.milezero.com/retail/api/hubs/org/{org_id}"

	//	read all hubs
	//	iterate through hubs and read ever address from each of them
	//		correct each address (spam goroutines)
	//			get current address
	//			verify geocode quality
	//			if less than EXACT, correct generate new geo code with google
	//				generate 2 goroutines to verify precision (LOW, MEDIUM, HIGH or EXACT) for:
	//				1. addr 1 (as addr1) + addr 2 (as addr2)
	//				2. addr 2 (as addr1) + addr 1 (as addr2)
	//			highest result should be used
	// save updated addresses into csv file once all done
}
