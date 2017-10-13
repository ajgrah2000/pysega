#ifndef PORTS_H_
#define PORTS_H_

#include "readInterface.h"
#include "writeInterface.h"

class Ports
{
  public:
    static Ports *instance();

    // Initialise the Ports class.
    virtual bool init();

        void addDeviceToPort(void *object, 
                             ReadInterface *read, 
                             Byte port);
        void addDeviceToPort(void *object, 
                              ReadInterface *read, 
                             WriteInterface *write, 
                             Byte port);
        Byte portRead(Byte port);
        void portWrite(Byte port, Byte data);
        void portWrite(Byte port, const Byte *data, uint16 length);

    protected:

        Ports();
        virtual ~Ports();
        static Ports *self;

        ReadInterface **portDevicesRead;
        WriteInterface **portDevicesWrite;
        void **portObjectsRead;
        void **portObjectsWrite;

        // Inner class for the dummy read and write.
        class DummyRead : public ReadInterface
        {
                virtual Byte read(void *arg){return dummyDeviceRead(arg);};
        };
        static DummyRead dummyDeviceReadFunction;

        static Byte dummyDeviceRead(void *object);

        static void dummyDeviceWrite(void *object, Byte data);
        static void dummyDeviceWriteMultiple(void *object, 
                                             const Byte *data, uint16 length);
        class DummyWrite : public WriteInterface
        {
            virtual void write(void *object, const Byte data){dummyDeviceWrite(object, data);};
            virtual void write(void *object, const Byte *data, uint16 length){dummyDeviceWriteMultiple(object, data, length);};
        };
        static DummyWrite dummyDeviceWriteFunction;

    private:
        static const unsigned int MAXPORTS    = 256;
};

#endif
