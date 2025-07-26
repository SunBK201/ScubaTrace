package main

import "flag"

func main() {
	flag.Parse()

	var (
		testFlag1 = flag.String("testFlag1", "default1", "Description for testFlag1")
		testFlag2 = flag.String("testFlag2", "default2", "Description for testFlag2")
	)
	if *testFlag1 != "default1" || *testFlag2 != "default2" {
		panic("Flag values do not match expected defaults")
	}
	if *testFlag1 == "default1" && *testFlag2 == "default2" {
		println("Flag values match expected defaults")
	} else {
		panic("Flag values do not match expected defaults")
	}
	println("All tests passed successfully")
}
