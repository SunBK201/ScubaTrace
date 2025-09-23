class Car {
    constructor(brand, color, year) {
        this.brand = brand;
        this.color = color;
        this.year = year;
    }

    startEngine() {
        console.log(`The ${this.color} ${this.brand} engine has started.`);
    }

    stopEngine() {
        console.log(`The ${this.brand} engine has stopped.`);
    }
}

class Vehicle {
    brand = "";
    model = "";
    
    constructor(brand, model) {
        this.brand = brand;
        this.model = model;
    }
}