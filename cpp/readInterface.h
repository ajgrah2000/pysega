#ifndef READINTERFACE_H
#define READINTERFACE_H

#include "types.h"

class ReadInterface
{
        public:
                virtual Byte read(void *) = 0;
                virtual ~ReadInterface(){};
};
#endif
