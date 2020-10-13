#ifndef CELL_H
#define CELL_H

#include <string>
#include "sysgroup.h"
#include <memory>
#include <algorithm>

using std::string;
using std::shared_ptr;
using std::weak_ptr;

class SysGroup;

//Описание одного блока
class Cell
{
    string _name; //Название блока
    string _symbol; //Условное обозначение
    string _unit_of_measurement; //Единица измерения
    string _symbol_unit_of_measurement; //Обозначение единицы измерения
    int _L; //Координата пути
    int _T; //Координата времени
    string _value_c; // Размерность в СИ
    std::weak_ptr<SysGroup> _group;
public:
    // explicit Cell();
    Cell(const string &name, const string &symbol,
    const string &unit_of_measurement, 
    const string &symbol_unit_of_measurement,
    int L, int T, const string &value_c, const shared_ptr<SysGroup> &group);

    ~Cell();

    string getName() const {
        return _name;
    }

};

#endif // CELL_H
