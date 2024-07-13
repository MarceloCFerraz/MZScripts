package main

import (
	"database/sql"
	"fmt"
	"log"
)

const dbName = "tickets.db"

func main() {
	_, err := sql.Open("sqlite3", dbName)

	if err != nil {
		log.Fatal(fmt.Sprintf("Error opening/creating db %s", dbName))
	}
}
