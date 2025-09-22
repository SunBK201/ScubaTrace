#include <iostream>
using namespace std;

class Car {
private:
  string brand;
  string color;

public:
  // Constructor
  Car(string b, string c) {
    brand = b;
    color = c;
  }

  // Method: start engine
  void startEngine() {
    cout << "The " << color << " " << brand << " engine has started." << endl;
  }

  // Method: stop engine
  void stopEngine() {
    cout << "The " << brand << " engine has stopped." << endl;
  }
};
