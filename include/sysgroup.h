#ifndef SYSGROUP_H
#define SYSGROUP_H

#include <string>
#include "cell.h"
#include <unordered_map>
#include <utility>
#include <boost/functional/hash.hpp>

using std::string;
using std::pair;

class Cell;

using std::shared_ptr;

class SysGroup
{
   string _name;
   int _G;
   int _k;
   std::unordered_map<
      pair<int, int>, shared_ptr<Cell>, 
               boost::hash<pair<int, int> > > _cells;
public:
   SysGroup(const string &name, int G, int k);
   string getName() const;
   int getG() const;
   int getK() const;

   void setCell(shared_ptr<Cell> cell, int L, int T);
   shared_ptr<Cell> getCell(int L, int T) const;
};

#endif // SYSGROUP_H
