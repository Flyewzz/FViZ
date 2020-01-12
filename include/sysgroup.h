#ifndef SYSGROUP_H
#define SYSGROUP_H

#include <string>

using std::string;

class SysGroup
{
   string _name;
   int _G;
   int _k;
public:
   SysGroup(string name, int G, int k);
   string getName() const;
   int getG() const;
   int getK() const;
};

#endif // SYSGROUP_H
