#include "errors.h"

class Exception
{
};

#include <iostream>

void errors::unsupported(const char *message)
{
    std::cerr << "Unsupported feature: " << message << std::endl;
    throw Exception();
}

void errors::error(const char *message)
{
    std::cerr << "Error: " << message << std::endl;
    throw Exception();
}

void errors::warning(const char *message)
{
    std::cerr << "Warning: " << message << std::endl;
}
