#ifndef LAWSGROUP_H
#define LAWSGROUP_H

#include <string>
#include "law.h"
#include <list>

using std::string;
using std::list;

class LawsGroup
{
   string _name;
   list<LawC*> _laws;
public:
    LawsGroup();
};

#endif // LAWSGROUP_H
