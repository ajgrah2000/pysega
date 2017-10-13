#ifndef INTERUPT_H
#define INTERUPT_H
class Interupt
{
    public:
        virtual ~Interupt(void){};
        virtual void interupt(void) = 0;
};
#endif
