#include "cell.h"

// Cell::Cell() {}

Cell::Cell(const string &name, const string &symbol,
    const string &unit_of_measurement, 
    const string &symbol_unit_of_measurement,
    int L, int T, const string &value_c, const shared_ptr<SysGroup> &group) :
    _name(name), _symbol(symbol), _unit_of_measurement(unit_of_measurement),
    _symbol_unit_of_measurement(symbol_unit_of_measurement),
    _L(L), _T(T), _value_c(value_c), _group(group) {}

Cell::~Cell() {}