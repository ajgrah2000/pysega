#ifndef INTORUPTOR_H
#define INTORUPTOR_H
class Interuptor
{
    public:
        virtual ~Interuptor(void){};
        virtual bool pollInterupts(unsigned int cycle) = 0;
        virtual unsigned int getNextInterupt(unsigned int cycle) = 0;
        virtual void setCycle(unsigned int cycle) = 0;
};
#endif
