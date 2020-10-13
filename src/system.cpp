#include <string>
#include "system.h"
using std::pair;
using std::string;

System::System() {}

System::System(const std::list<shared_ptr<SysGroup>> &groups) : _groups(groups) {}

shared_ptr<SysGroup> System::getSysGroup(int G, int k) const
{
   for (auto iterator = _groups.begin(); iterator != _groups.end(); ++iterator)
   {
      if ((*iterator)->getG() == G && (*iterator)->getK() == k)
      {
         return *iterator;
      }
   }
   return nullptr;
}

void System::addSysGroup(shared_ptr<SysGroup> group)
{
   if (getSysGroup(group->getG(), group->getK())) {
      throw "A system group with such G and k already exists!";
   }
   _groups.push_back(group);
}

void System::removeSysGroup(int G, int k)
{
   shared_ptr<SysGroup> group = getSysGroup(G, k);
   if (group == nullptr) {
      throw "No group with such G and k found";
   }
   _groups.remove(group);
}


void System::print() const
{
}
