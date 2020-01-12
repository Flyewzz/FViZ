#include "sysgroup.h"

SysGroup::SysGroup(string name, int G, int k) : _name(name), _G(G), _k(k){}
string SysGroup::getName() const {
     return _name;
}
int SysGroup::getG() const { return _G; }
int SysGroup::getK() const { return _k; }
