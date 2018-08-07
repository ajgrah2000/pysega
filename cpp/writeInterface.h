#ifndef WRITEINTERFACE_H
#define WRITEINTERFACE_H

#include "types.h"

class WriteInterface
{
        public:
                virtual void write(void *, const Byte data) = 0;
                virtual void write(void *, const Byte *data, uint16 length) = 0;
                virtual ~WriteInterface(){};
};
#endif
