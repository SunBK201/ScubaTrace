struct Car {
    brand: String,
    color: String,
    year: u32,
}

struct Vehicle {
    make: String,
    model: String,
}

impl Car {
    fn new(brand: String, color: String, year: u32) -> Self {
        Car { brand, color, year }
    }
    
    fn start_engine(&self) {
        println!("The {} {} engine has started.", self.color, self.brand);
    }
    
    fn stop_engine(&self) {
        println!("The {} engine has stopped.", self.brand);
    }
}

fn main() {
    let car = Car::new("Toyota".to_string(), "Red".to_string(), 2020);
    car.start_engine();
    car.stop_engine();
}