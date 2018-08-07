#ifndef ERRORS_H
#define ERRORS_H
class errors
{
    public:
        static void unsupported(const char *message);
        static void error(const char *message);
        static void warning(const char *message);
};
#endif
