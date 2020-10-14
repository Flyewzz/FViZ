#ifndef SYSTEM_H
#define SYSTEM_H

#include "sysgroup.h"
#include <list>
#include <vector>

using std::string;
using std::pair;
using std::vector;

class System
{
   std::list<shared_ptr<SysGroup> > _groups;
public:
   System(const std::list<shared_ptr<SysGroup> > &groups);
   System();
   void addSysGroup(shared_ptr<SysGroup> group);
   shared_ptr<SysGroup> getSysGroup(int G, int k) const;
   void removeSysGroup(int G, int k);
   vector<shared_ptr<Cell> > getCells(int L, int T) const;
};

#endif // SYSTEM_H
