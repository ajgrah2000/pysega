#include "sega.h"

#include <iostream>
#include <stdexcept>
#include <unistd.h>

/* Test driver for the sega master system */
int main(int argc, char **argv)
{
    const char *cartName;
    Sega *sega;
    bool isFullSpeed = false;

        // Process arguments, curretnly only `n' for full speed
    int c;
    while((c = getopt(argc, argv, "n")) > 0)
    {
        switch(c)
        {
            case 'n':
                isFullSpeed = true;
                break;

            default:
                break;
        }
    }

    if (optind < argc)
        cartName = argv[argc-1];
    else
    {
        std::cerr << "Usage: " << argv[0] << " -n romfile" << std::endl;
        std::cerr << "        -n     No delay (full speed)" << std::endl;
        exit(1);
    }

      // Commandline ok, instantiate the sega mastersystem
    sega = new Sega;

    sega->setFullSpeed(isFullSpeed);

      // Load cartdridge as specified at command line
    sega->loadCartridge(cartName);

    try
    {
          // `Turn on' the power
        sega->powerOn();
    } catch(std::out_of_range e)
    {
        std::cout << "exception caught: " << std::endl;
        std::cout << e.what() << std::endl;
    }
    catch(std::exception e)
    {
        std::cout << "generic exception caught: " << std::endl;
    }
    catch(...)
    {
        std::cout << "unknown exception" << std::endl;
    }

    delete sega;

    std::cout << "Finished" << std::endl;

    return 0;
}

