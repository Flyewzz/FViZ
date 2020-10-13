#include "../include/sysgroup.h"
#include <iostream>

SysGroup::SysGroup(const string &name, int G, int k) : _name(name), _G(G), _k(k){}
string SysGroup::getName() const {
     return _name;
}
int SysGroup::getG() const { return _G; }
int SysGroup::getK() const { return _k; }

void SysGroup::setCell(shared_ptr<Cell> cell, int L, int T) {
     std::pair<int, int> pair = std::make_pair(L, T);
     auto found = _cells.find(pair);
     if (found != _cells.end()) {
          throw "Such cell already exists";
     } else {
          _cells[pair] = cell;
     }
}

shared_ptr<Cell> SysGroup::getCell(int L, int T) const {
     std::pair<int, int> pair = std::make_pair(L, T);
     shared_ptr<Cell> cell = _cells.at(pair);
     return cell;
}

void SysGroup::print() const {
     for (auto iterator = _cells.begin(); iterator != _cells.end(); ++iterator) {
          std::pair<int, int> key = iterator->first;
          std::cout <<  key.first << " " << key.second  << ": " << iterator->second->getName();
          std::cout << std::endl;
     }
}