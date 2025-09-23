package main

import "fmt"

type Car struct {
	Brand string
	Color string
	Year  int
}

type Vehicle struct {
	Make  string
	Model string
}

func (c *Car) StartEngine() {
	fmt.Printf("The %s %s engine has started.\n", c.Color, c.Brand)
}

func (c *Car) StopEngine() {
	fmt.Printf("The %s engine has stopped.\n", c.Brand)
}

func NewCar(brand, color string, year int) *Car {
	return &Car{
		Brand: brand,
		Color: color,
		Year:  year,
	}
}
