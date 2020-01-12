#ifndef SYSGROUP_H
#define SYSGROUP_H

#include <string>
#include f
using std::string;

class SysGroup
{
   string _name;
   int _G;
   int _k;
public:
    SysGroup();
    string getName() const {
        return _name;
    }
};

#endif // SYSGROUP_H
