/*
 * Compilation: g++ -o units units.cpp
 * Execution: ./units
 */

#include <iostream>
#include <boost/units/systems/si.hpp>

using namespace boost::units;

quantity<si::velocity> calculateSpeed(quantity<si::length> distance, quantity<si::time> duration)
{
    return distance / duration;
}

int main()
{
    double distance = 12, duration = 4;
    quantity<si::velocity> value = calculateSpeed(distance * si::meters, duration * si::seconds);
    std::cout << "Speed: " << value.value() << " m/s" << std::endl;
    return 0;
}
