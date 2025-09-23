import Foundation

class Car {
    var brand: String
    var color: String
    var year: Int
    
    init(brand: String, color: String, year: Int) {
        self.brand = brand
        self.color = color
        self.year = year
    }
    
    func startEngine() {
        print("The \(color) \(brand) engine has started.")
    }
    
    func stopEngine() {
        print("The \(brand) engine has stopped.")
    }
}

struct Vehicle {
    var make: String
    var model: String
}